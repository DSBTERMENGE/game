"""Testes dos detectores e das estatísticas dos padrões sequenciais."""

from datetime import date, timedelta
from decimal import Decimal
import unittest

from msen.modelos import ResultadoEntrada
from msen.padroes import (
    CODIGO_DUAS_SEQUENCIAIS,
    CODIGO_MAIS_DE_TRES_SEQUENCIAIS,
    CODIGO_TRES_SEQUENCIAIS,
    ErroAnalisePadrao,
    calcular_estatistica_padrao,
    calcular_estatisticas_sequenciais,
    criar_registro_detectores_iniciais,
    detectar_duas_dezenas_sequenciais,
    detectar_mais_de_tres_dezenas_sequenciais,
    detectar_tres_dezenas_sequenciais,
)


def criar_resultado(numero_ap: int, dezenas, *, dia: int | None = None):
    """Cria um resultado validado e controlado para os testes históricos."""

    return ResultadoEntrada.criar(
        data_resultado=date(2020, 1, 1)
        + timedelta(days=numero_ap if dia is None else dia),
        numero_ap=numero_ap,
        resultados=dezenas,
    )


class DetectoresSequenciaisTestCase(unittest.TestCase):
    def test_exemplo_aprovado_e_classificado_somente_como_tres(self):
        dezenas = (10, 25, 26, 27, 50, 58)

        self.assertFalse(detectar_duas_dezenas_sequenciais(dezenas))
        self.assertTrue(detectar_tres_dezenas_sequenciais(dezenas))
        self.assertFalse(detectar_mais_de_tres_dezenas_sequenciais(dezenas))

    def test_classifica_pelo_maior_grupo_sem_sobreposicao(self):
        casos = (
            ((1, 3, 5, 7, 9, 11), (False, False, False)),
            ((10, 25, 26, 38, 50, 58), (True, False, False)),
            ((1, 2, 10, 11, 12, 50), (False, True, False)),
            ((10, 25, 26, 27, 28, 58), (False, False, True)),
            ((10, 25, 26, 27, 28, 29), (False, False, True)),
            ((25, 26, 27, 28, 29, 30), (False, False, True)),
        )
        for dezenas, esperado in casos:
            with self.subTest(dezenas=dezenas):
                obtido = (
                    detectar_duas_dezenas_sequenciais(dezenas),
                    detectar_tres_dezenas_sequenciais(dezenas),
                    detectar_mais_de_tres_dezenas_sequenciais(dezenas),
                )
                self.assertEqual(esperado, obtido)

    def test_dois_grupos_de_duas_contam_como_um_resultado_do_padrao(self):
        dezenas = (10, 11, 25, 26, 40, 58)
        self.assertTrue(detectar_duas_dezenas_sequenciais(dezenas))

    def test_limites_um_e_sessenta_e_ordem_nao_alteram_classificacao(self):
        for dezenas in ((1, 2, 10, 20, 30, 60), (60, 40, 59, 20, 10, 1)):
            with self.subTest(dezenas=dezenas):
                self.assertTrue(detectar_duas_dezenas_sequenciais(dezenas))

    def test_rejeita_entrada_fora_do_contrato(self):
        casos = (
            ((1, 2, 3), ValueError),
            ((1, 2, 3, 4, 5, 61), ValueError),
            ((1, 2, 3, 4, 5, 5), ValueError),
            ((1, 2, 3, 4, 5, True), TypeError),
        )
        for dezenas, erro in casos:
            with self.subTest(dezenas=dezenas):
                with self.assertRaises(erro):
                    detectar_duas_dezenas_sequenciais(dezenas)

    def test_registro_inicial_vincula_os_tres_codigos(self):
        registro = criar_registro_detectores_iniciais()
        self.assertEqual(
            (
                CODIGO_DUAS_SEQUENCIAIS,
                CODIGO_TRES_SEQUENCIAIS,
                CODIGO_MAIS_DE_TRES_SEQUENCIAIS,
            ),
            registro.codigos_registrados(),
        )


class EstatisticasSequenciaisTestCase(unittest.TestCase):
    def test_calcula_contagem_intervalo_media_e_desvio_de_cada_padrao(self):
        historico = (
            criar_resultado(10, (10, 25, 26, 38, 50, 58)),
            criar_resultado(20, (1, 3, 5, 7, 9, 11)),
            criar_resultado(25, (1, 10, 20, 40, 41, 60)),
            criar_resultado(40, (10, 25, 26, 27, 50, 58)),
            criar_resultado(50, (1, 2, 3, 10, 20, 60)),
            criar_resultado(60, (10, 25, 26, 27, 28, 58)),
            criar_resultado(80, (25, 26, 27, 28, 29, 30)),
        )

        duas, tres, mais_de_tres = calcular_estatisticas_sequenciais(historico)

        self.assertEqual((10, 25), duas.ocorrencias)
        self.assertEqual((15,), duas.intervalos)
        self.assertEqual(2, duas.num_oco)
        self.assertEqual(Decimal("15.000000"), duas.intervalo_medio)
        self.assertEqual(Decimal("0.000000"), duas.desv_padrao)

        self.assertEqual((40, 50), tres.ocorrencias)
        self.assertEqual(Decimal("10.000000"), tres.intervalo_medio)
        self.assertEqual(Decimal("0.000000"), tres.desv_padrao)

        self.assertEqual((60, 80), mais_de_tres.ocorrencias)
        self.assertEqual(Decimal("20.000000"), mais_de_tres.intervalo_medio)
        self.assertEqual(Decimal("0.000000"), mais_de_tres.desv_padrao)

    def test_historico_vazio_e_uma_ocorrencia_nao_inventam_intervalo(self):
        vazio = calcular_estatistica_padrao(
            "PD_001", detectar_duas_dezenas_sequenciais, []
        )
        uma = calcular_estatistica_padrao(
            "PD_001",
            detectar_duas_dezenas_sequenciais,
            [criar_resultado(35, (10, 25, 26, 38, 50, 58))],
        )

        for resumo, quantidade in ((vazio, 0), (uma, 1)):
            self.assertEqual(quantidade, resumo.num_oco)
            self.assertEqual((), resumo.intervalos)
            self.assertIsNone(resumo.intervalo_medio)
            self.assertIsNone(resumo.desv_padrao)

    def test_intervalos_variados_usam_media_e_desvio_populacional(self):
        historico = (
            criar_resultado(10, (10, 25, 26, 38, 50, 58)),
            criar_resultado(20, (10, 25, 26, 38, 50, 58)),
            criar_resultado(35, (10, 25, 26, 38, 50, 58)),
            criar_resultado(50, (10, 25, 26, 38, 50, 58)),
        )
        resumo = calcular_estatistica_padrao(
            "PD_001", detectar_duas_dezenas_sequenciais, historico
        )

        self.assertEqual((10, 15, 15), resumo.intervalos)
        self.assertEqual(Decimal("13.333333"), resumo.intervalo_medio)
        self.assertEqual(Decimal("2.357023"), resumo.desv_padrao)

    def test_ordena_historico_sem_modificar_entrada(self):
        historico = [
            criar_resultado(50, (10, 25, 26, 38, 50, 58)),
            criar_resultado(35, (10, 25, 26, 38, 50, 58)),
        ]
        estado_antes = tuple(item.numero_ap for item in historico)

        resumo = calcular_estatistica_padrao(
            "PD_001", detectar_duas_dezenas_sequenciais, historico
        )

        self.assertEqual((35, 50), resumo.ocorrencias)
        self.assertEqual(estado_antes, tuple(item.numero_ap for item in historico))

    def test_rejeita_concurso_duplicado_e_data_historicamente_invalida(self):
        casos = (
            (
                "NUMERO_AP_DUPLICADO",
                [
                    criar_resultado(10, (1, 3, 5, 7, 9, 11)),
                    criar_resultado(10, (2, 4, 6, 8, 10, 12)),
                ],
            ),
            (
                "ORDEM_HISTORICA_DIVERGENTE",
                [
                    criar_resultado(10, (1, 3, 5, 7, 9, 11), dia=20),
                    criar_resultado(20, (2, 4, 6, 8, 10, 12), dia=10),
                ],
            ),
        )
        for codigo, historico in casos:
            with self.subTest(codigo=codigo):
                with self.assertRaises(ErroAnalisePadrao) as contexto:
                    calcular_estatistica_padrao(
                        "PD_001", detectar_duas_dezenas_sequenciais, historico
                    )
                self.assertEqual(codigo, contexto.exception.codigo)

    def test_rejeita_historico_nao_validado_e_detector_nao_booleano(self):
        with self.assertRaisesRegex(TypeError, "ResultadoEntrada"):
            calcular_estatistica_padrao("PD_001", lambda dezenas: False, [object()])

        with self.assertRaisesRegex(TypeError, "booleano"):
            calcular_estatistica_padrao(
                "PD_001",
                lambda dezenas: 1,
                [criar_resultado(1, (1, 3, 5, 7, 9, 11))],
            )


if __name__ == "__main__":
    unittest.main()
