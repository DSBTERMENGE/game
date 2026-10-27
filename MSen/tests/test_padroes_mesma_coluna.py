"""Testes dos detectores e estatísticas de dezenas na mesma coluna."""

from datetime import date, timedelta
from decimal import Decimal
import unittest

from msen.modelos import ResultadoEntrada
from msen.padroes import (
    CODIGO_DUAS_NA_MESMA_COLUNA,
    CODIGO_MAIS_DE_TRES_NA_MESMA_COLUNA,
    CODIGO_TRES_NA_MESMA_COLUNA,
    calcular_estatisticas_mesma_coluna,
    criar_registro_detectores_aprovados,
    criar_registro_detectores_mesma_coluna,
    detectar_duas_dezenas_na_mesma_coluna,
    detectar_mais_de_tres_dezenas_na_mesma_coluna,
    detectar_tres_dezenas_na_mesma_coluna,
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
        detectar_duas_dezenas_na_mesma_coluna(dezenas),
        detectar_tres_dezenas_na_mesma_coluna(dezenas),
        detectar_mais_de_tres_dezenas_na_mesma_coluna(dezenas),
    )


class DetectoresMesmaColunaTestCase(unittest.TestCase):
    def test_classifica_pela_maior_sequencia_vertical_sem_sobreposicao(self):
        casos = (
            ((1, 12, 23, 34, 45, 56), (False, False, False)),
            ((10, 25, 35, 48, 51, 59), (True, False, False)),
            ((7, 17, 27, 34, 45, 56), (False, True, False)),
            ((5, 15, 25, 35, 48, 59), (False, False, True)),
            ((5, 15, 25, 35, 45, 59), (False, False, True)),
            ((10, 20, 30, 40, 50, 60), (False, False, True)),
        )
        for dezenas, esperado in casos:
            with self.subTest(dezenas=dezenas):
                self.assertEqual(esperado, detectar_todos(dezenas))

    def test_dois_pares_contam_como_um_resultado_de_duas(self):
        self.assertEqual(
            (True, False, False),
            detectar_todos((5, 15, 22, 32, 48, 59)),
        )

    def test_dezenas_na_mesma_coluna_sem_linhas_subjacentes_nao_contam(self):
        self.assertEqual(
            (False, False, False),
            detectar_todos((10, 25, 38, 45, 51, 59)),
        )

    def test_tripla_e_par_classificam_somente_como_tres(self):
        self.assertEqual(
            (False, True, False),
            detectar_todos((5, 15, 25, 32, 42, 59)),
        )

    def test_colunas_um_e_dez_limites_e_ordem_nao_interferem(self):
        casos = (
            ((1, 11, 23, 34, 45, 56), (True, False, False)),
            ((60, 40, 50, 1, 33, 56), (False, True, False)),
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
                    detectar_duas_dezenas_na_mesma_coluna(dezenas)

    def test_funcoes_publicas_possuem_documentacao_em_portugues(self):
        for detector in (
            detectar_duas_dezenas_na_mesma_coluna,
            detectar_tres_dezenas_na_mesma_coluna,
            detectar_mais_de_tres_dezenas_na_mesma_coluna,
        ):
            with self.subTest(detector=detector.__name__):
                self.assertIn("Parâmetros:", detector.__doc__ or "")
                self.assertIn("Retorno:", detector.__doc__ or "")
                self.assertIn("Regra:", detector.__doc__ or "")


class EstatisticasMesmaColunaTestCase(unittest.TestCase):
    def test_catalogo_unificado_contem_os_seis_detectores(self):
        self.assertEqual(
            tuple(f"PD_{numero:03d}" for numero in range(1, 10)),
            criar_registro_detectores_aprovados().codigos_registrados(),
        )

    def test_registro_associa_os_tres_codigos_aprovados(self):
        registro = criar_registro_detectores_mesma_coluna()

        self.assertEqual(
            (
                CODIGO_DUAS_NA_MESMA_COLUNA,
                CODIGO_TRES_NA_MESMA_COLUNA,
                CODIGO_MAIS_DE_TRES_NA_MESMA_COLUNA,
            ),
            registro.codigos_registrados(),
        )

    def test_calcula_ocorrencias_intervalos_media_e_desvio(self):
        historico = (
            criar_resultado(10, (10, 25, 35, 48, 51, 59)),
            criar_resultado(20, (1, 12, 23, 34, 45, 56)),
            criar_resultado(25, (5, 15, 22, 32, 48, 59)),
            criar_resultado(40, (7, 17, 27, 34, 45, 56)),
            criar_resultado(50, (5, 15, 25, 32, 42, 59)),
            criar_resultado(60, (5, 15, 25, 35, 48, 59)),
            criar_resultado(80, (10, 20, 30, 40, 50, 60)),
        )

        duas, tres, mais_de_tres = calcular_estatisticas_mesma_coluna(historico)

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
        vazio = calcular_estatisticas_mesma_coluna(())
        uma = calcular_estatisticas_mesma_coluna(
            (criar_resultado(35, (10, 25, 35, 48, 51, 59)),)
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
                (50, (5, 15, 25, 32, 42, 59)),
                (40, (7, 17, 27, 34, 45, 56)),
            )
        )

        _, tres, _ = calcular_estatisticas_mesma_coluna(historico)

        self.assertEqual((40, 50), tres.ocorrencias)


if __name__ == "__main__":
    unittest.main()
