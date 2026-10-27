"""Testes dos detectores e estatísticas de dezenas na mesma linha."""

from datetime import date, timedelta
from decimal import Decimal
import unittest

from msen.modelos import ResultadoEntrada
from msen.padroes import (
    CODIGO_DUAS_NA_MESMA_LINHA,
    CODIGO_MAIS_DE_TRES_NA_MESMA_LINHA,
    CODIGO_TRES_NA_MESMA_LINHA,
    calcular_estatisticas_mesma_linha,
    criar_registro_detectores_mesma_linha,
    detectar_duas_dezenas_na_mesma_linha,
    detectar_mais_de_tres_dezenas_na_mesma_linha,
    detectar_tres_dezenas_na_mesma_linha,
)


def criar_resultado(numero_ap: int, dezenas) -> ResultadoEntrada:
    """Cria um resultado validado para os testes históricos em memória."""

    return ResultadoEntrada.criar(
        data_resultado=date(2020, 1, 1) + timedelta(days=numero_ap),
        numero_ap=numero_ap,
        resultados=dezenas,
    )


def detectar_todos(dezenas: tuple[int, ...]) -> tuple[bool, bool, bool]:
    """Executa os três detectores para conferir a classificação exclusiva."""

    return (
        detectar_duas_dezenas_na_mesma_linha(dezenas),
        detectar_tres_dezenas_na_mesma_linha(dezenas),
        detectar_mais_de_tres_dezenas_na_mesma_linha(dezenas),
    )


class DetectoresMesmaLinhaTestCase(unittest.TestCase):
    def test_classifica_pela_maior_ocupacao_sem_sobreposicao(self):
        casos = (
            ((1, 12, 23, 34, 45, 56), (False, False, False)),
            ((1, 5, 18, 27, 44, 59), (True, False, False)),
            ((21, 25, 30, 34, 45, 56), (False, True, False)),
            ((31, 33, 36, 40, 45, 56), (False, False, True)),
            ((41, 42, 43, 44, 45, 56), (False, False, True)),
            ((1, 2, 3, 4, 5, 6), (False, False, True)),
        )
        for dezenas, esperado in casos:
            with self.subTest(dezenas=dezenas):
                self.assertEqual(esperado, detectar_todos(dezenas))

    def test_dezenas_nao_precisam_ser_sequenciais(self):
        self.assertEqual(
            (True, False, False),
            detectar_todos((1, 9, 18, 27, 44, 59)),
        )

    def test_dois_pares_contam_como_uma_ocorrencia_de_duas(self):
        self.assertEqual(
            (True, False, False),
            detectar_todos((1, 5, 12, 18, 44, 59)),
        )

    def test_tripla_e_par_classificam_somente_como_tres(self):
        self.assertEqual(
            (False, True, False),
            detectar_todos((1, 5, 9, 12, 18, 44)),
        )

    def test_limites_das_linhas_e_ordem_nao_interferem(self):
        casos = (
            ((1, 10, 11, 30, 41, 60), (True, False, False)),
            ((60, 52, 51, 40, 20, 1), (False, True, False)),
        )
        for dezenas, esperado in casos:
            with self.subTest(dezenas=dezenas):
                self.assertEqual(esperado, detectar_todos(dezenas))

    def test_rejeita_entrada_fora_do_contrato(self):
        casos = (
            ((1, 2, 3), ValueError),
            ((1, 2, 3, 4, 5, 61), ValueError),
            ((1, 2, 3, 4, 5, 5), ValueError),
            ((1, 2, 3, 4, 5, True), TypeError),
            ("01,02,03,04,05,06", TypeError),
        )
        for dezenas, erro in casos:
            with self.subTest(dezenas=dezenas):
                with self.assertRaises(erro):
                    detectar_duas_dezenas_na_mesma_linha(dezenas)

    def test_funcoes_publicas_possuem_documentacao_em_portugues(self):
        for detector in (
            detectar_duas_dezenas_na_mesma_linha,
            detectar_tres_dezenas_na_mesma_linha,
            detectar_mais_de_tres_dezenas_na_mesma_linha,
        ):
            with self.subTest(detector=detector.__name__):
                self.assertIn("Parâmetros:", detector.__doc__ or "")
                self.assertIn("Retorno:", detector.__doc__ or "")
                self.assertIn("Regra:", detector.__doc__ or "")


class EstatisticasMesmaLinhaTestCase(unittest.TestCase):
    def test_registro_associa_os_tres_codigos_aprovados(self):
        registro = criar_registro_detectores_mesma_linha()

        self.assertEqual(
            (
                CODIGO_DUAS_NA_MESMA_LINHA,
                CODIGO_TRES_NA_MESMA_LINHA,
                CODIGO_MAIS_DE_TRES_NA_MESMA_LINHA,
            ),
            registro.codigos_registrados(),
        )

    def test_calcula_ocorrencias_intervalos_media_e_desvio(self):
        historico = (
            criar_resultado(10, (1, 5, 18, 27, 44, 59)),
            criar_resultado(20, (1, 12, 23, 34, 45, 56)),
            criar_resultado(25, (1, 5, 12, 18, 44, 59)),
            criar_resultado(40, (21, 25, 30, 34, 45, 56)),
            criar_resultado(50, (1, 5, 9, 12, 18, 44)),
            criar_resultado(60, (31, 33, 36, 40, 45, 56)),
            criar_resultado(80, (1, 2, 3, 4, 5, 6)),
        )

        duas, tres, mais_de_tres = calcular_estatisticas_mesma_linha(historico)

        self.assertEqual((10, 25), duas.ocorrencias)
        self.assertEqual((15,), duas.intervalos)
        self.assertEqual(Decimal("15.000000"), duas.intervalo_medio)
        self.assertEqual(Decimal("0.000000"), duas.desv_padrao)

        self.assertEqual((40, 50), tres.ocorrencias)
        self.assertEqual((10,), tres.intervalos)
        self.assertEqual(Decimal("10.000000"), tres.intervalo_medio)
        self.assertEqual(Decimal("0.000000"), tres.desv_padrao)

        self.assertEqual((60, 80), mais_de_tres.ocorrencias)
        self.assertEqual((20,), mais_de_tres.intervalos)
        self.assertEqual(Decimal("20.000000"), mais_de_tres.intervalo_medio)
        self.assertEqual(Decimal("0.000000"), mais_de_tres.desv_padrao)

    def test_historico_vazio_e_uma_ocorrencia_nao_criam_intervalo(self):
        vazio = calcular_estatisticas_mesma_linha(())
        uma = calcular_estatisticas_mesma_linha(
            (criar_resultado(35, (1, 5, 18, 27, 44, 59)),)
        )

        self.assertEqual((0, 0, 0), tuple(item.num_oco for item in vazio))
        self.assertEqual((1, 0, 0), tuple(item.num_oco for item in uma))
        for resumo in (*vazio, *uma):
            self.assertEqual((), resumo.intervalos)
            self.assertIsNone(resumo.intervalo_medio)
            self.assertIsNone(resumo.desv_padrao)

    def test_materializa_iterador_uma_vez_e_ordena_o_historico(self):
        historico = (
            criar_resultado(numero, dezenas)
            for numero, dezenas in (
                (50, (1, 5, 9, 12, 18, 44)),
                (40, (21, 25, 30, 34, 45, 56)),
            )
        )

        _, tres, _ = calcular_estatisticas_mesma_linha(historico)

        self.assertEqual((40, 50), tres.ocorrencias)


if __name__ == "__main__":
    unittest.main()
