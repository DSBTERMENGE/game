"""Testes do motor acumulado de frequência simples, 2VS e 3VS."""

from dataclasses import replace
from datetime import date, timedelta
from decimal import Decimal
import unittest

from msen.calculos import calcular_frequencias
from msen.modelos import ResultadoEntrada
from msen.services import (
    ErroMotorFrequencia,
    MotorFrequenciaAcumulada,
    calcular_fotografias_acumuladas,
    configuracao_frequencia_inicial,
)


def resultado(numero: int, *, inclui_10: bool) -> ResultadoEntrada:
    dezenas = (10, 21, 32, 43, 54, 60) if inclui_10 else (9, 21, 32, 43, 54, 60)
    return ResultadoEntrada.criar(
        data_resultado=date(2020, 1, 1) + timedelta(days=numero),
        numero_ap=numero,
        resultados=dezenas,
    )


def localizar(fotografias, concurso, dezena, tipo):
    return next(
        item for item in fotografias
        if item.numero_do_concurso == concurso
        and item.dezena == dezena and item.tipo_evento == tipo
    )


class FrequenciaHistoricaTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.config = replace(configuracao_frequencia_inicial(), tamanho_inicial=3)
        self.serie = tuple(
            resultado(numero, inclui_10=numero in {1, 2, 3, 5, 6, 7})
            for numero in range(1, 8)
        )

    def test_primeira_fotografia_e_no_corte_configurado(self) -> None:
        fotografias = calcular_fotografias_acumuladas(self.serie, self.config)
        self.assertEqual(5 * 60 * 3, len(fotografias))
        self.assertEqual(3, min(item.numero_do_concurso for item in fotografias))
        simples = localizar(fotografias, 3, 10, "SIMPLES")
        self.assertEqual(3, simples.quantidade_ocorrencias)
        self.assertEqual(2, simples.quantidade_intervalos)
        self.assertEqual(1, simples.intervalo_minimo)
        self.assertEqual(Decimal("1.000000"), simples.media_intervalos)
        self.assertEqual(Decimal("0.000000"), simples.desvio_padrao_intervalos)
        self.assertEqual(Decimal("4.000000"), simples.previsao_central)
        self.assertEqual(4, simples.concurso_limite_inferior)
        self.assertEqual(4, simples.concurso_limite_superior)

    def test_configuracao_inicial_produz_primeiro_corte_500(self) -> None:
        config = configuracao_frequencia_inicial()
        serie = tuple(
            resultado(numero, inclui_10=numero % 5 == 0)
            for numero in range(1, 501)
        )
        fotografias = calcular_fotografias_acumuladas(serie, config)
        self.assertEqual(180, len(fotografias))
        self.assertEqual({500}, {item.numero_do_concurso for item in fotografias})
        self.assertEqual(
            fotografias,
            calcular_fotografias_acumuladas(serie, config),
        )

    def test_janelas_sobrepostas_de_2vs_e_3vs(self) -> None:
        fotografias = calcular_fotografias_acumuladas(self.serie, self.config)
        dois = localizar(fotografias, 3, 10, "2VS")
        tres = localizar(fotografias, 3, 10, "3VS")
        self.assertEqual(2, dois.quantidade_ocorrencias)
        self.assertEqual(1, dois.quantidade_intervalos)
        self.assertEqual(1, dois.intervalo_minimo)
        self.assertEqual(1, tres.quantidade_ocorrencias)
        self.assertEqual(0, tres.quantidade_intervalos)
        self.assertIsNone(tres.media_intervalos)

    def test_sequencia_interrompida_e_reiniciada(self) -> None:
        fotografias = calcular_fotografias_acumuladas(self.serie, self.config)
        dois = localizar(fotografias, 7, 10, "2VS")
        tres = localizar(fotografias, 7, 10, "3VS")
        self.assertEqual(4, dois.quantidade_ocorrencias)
        self.assertEqual((1, 3), (dois.intervalo_minimo, dois.intervalo_maximo))
        self.assertEqual(2, tres.quantidade_ocorrencias)
        self.assertEqual(1, tres.quantidade_intervalos)
        self.assertEqual(Decimal("4.000000"), tres.media_intervalos)
        self.assertEqual(Decimal("11.000000"), tres.previsao_central)

    def test_media_desvio_e_limites_preservam_unidades(self) -> None:
        fotografias = calcular_fotografias_acumuladas(self.serie, self.config)
        simples = localizar(fotografias, 7, 10, "SIMPLES")
        self.assertEqual(Decimal("1.200000"), simples.media_intervalos)
        self.assertEqual(Decimal("0.400000"), simples.desvio_padrao_intervalos)
        self.assertEqual(Decimal("8.200000"), simples.previsao_central)
        self.assertEqual(Decimal("7.800000"), simples.limite_inferior_exato)
        self.assertEqual(Decimal("8.600000"), simples.limite_superior_exato)
        self.assertEqual(8, simples.concurso_limite_inferior)
        self.assertEqual(9, simples.concurso_limite_superior)

    def test_sem_vazamento_de_informacao_futura(self) -> None:
        config = replace(self.config, tamanho_inicial=1)
        motor = MotorFrequenciaAcumulada(config)
        motor.processar(resultado(1, inclui_10=True))
        corte_2 = motor.processar(resultado(2, inclui_10=True))
        self.assertEqual(0, localizar(corte_2, 2, 10, "3VS").quantidade_ocorrencias)
        corte_3 = motor.processar(resultado(3, inclui_10=True))
        self.assertEqual(1, localizar(corte_3, 3, 10, "3VS").quantidade_ocorrencias)

    def test_carga_integral_e_incremental_sao_identicas(self) -> None:
        integral = calcular_fotografias_acumuladas(self.serie, self.config)
        motor = MotorFrequenciaAcumulada(self.config)
        incremental = motor.processar_varios(self.serie[:4]) + motor.processar_varios(
            self.serie[4:]
        )
        self.assertEqual(integral, incremental)

    def test_simples_reconcilia_com_calculo_atual(self) -> None:
        fotografias = calcular_fotografias_acumuladas(self.serie, self.config)
        atual = calcular_frequencias(self.serie)[9]
        simples = localizar(fotografias, 7, 10, "SIMPLES")
        self.assertEqual(atual.num_oco, simples.quantidade_ocorrencias)
        self.assertEqual(atual.qtd_intervalos, simples.quantidade_intervalos)
        self.assertEqual(atual.intervalo_minimo, simples.intervalo_minimo)
        self.assertEqual(atual.intervalo_maximo, simples.intervalo_maximo)
        self.assertEqual(atual.media_oco, simples.media_intervalos)
        self.assertEqual(atual.mediana_oco, simples.mediana_intervalos)
        self.assertEqual(atual.desv_padrao_oco, simples.desvio_padrao_intervalos)

    def test_tipo_individual_reduz_a_saida_sem_mudar_o_calculo(self) -> None:
        config = replace(self.config, tipo_evento="2VS")
        fotografias = calcular_fotografias_acumuladas(self.serie, config)
        self.assertEqual(5 * 60, len(fotografias))
        self.assertEqual({"2VS"}, {item.tipo_evento for item in fotografias})

    def test_rejeita_lacuna_e_retrocesso(self) -> None:
        motor = MotorFrequenciaAcumulada(self.config)
        motor.processar(resultado(1, inclui_10=True))
        with self.assertRaises(ErroMotorFrequencia) as lacuna:
            motor.processar(resultado(3, inclui_10=True))
        self.assertEqual("LACUNA_HISTORICA", lacuna.exception.codigo)
        motor.processar(resultado(2, inclui_10=True))
        with self.assertRaises(ErroMotorFrequencia) as ordem:
            motor.processar(resultado(2, inclui_10=True))
        self.assertEqual("CONCURSO_FORA_DE_ORDEM", ordem.exception.codigo)

    def test_estado_sem_base_nao_inventa_zero(self) -> None:
        fotografias = calcular_fotografias_acumuladas(self.serie[:3], self.config)
        item = localizar(fotografias, 3, 1, "SIMPLES")
        self.assertEqual(0, item.quantidade_ocorrencias)
        self.assertEqual(0, item.quantidade_intervalos)
        self.assertIsNone(item.media_intervalos)
        self.assertIsNone(item.desvio_padrao_intervalos)
        self.assertIsNone(item.previsao_central)


if __name__ == "__main__":
    unittest.main()
