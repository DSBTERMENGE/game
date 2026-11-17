"""Testes da decisão categórica diagonal antes da integração ao funil."""

from datetime import date
from decimal import Decimal
import unittest

from msen.modelos import ResultadoEntrada
from msen.padroes import criar_fotografia_historica_diagonal
from msen.padroes import (
    DistribuicaoCategoriasDiagonais,
    FotografiaHistoricaDiagonal,
    IncidenciaCategoriaDiagonal,
)
from msen.screener import avaliar_filtro_diagonal


def _resultado(numero: int, dezenas: tuple[int, ...]) -> ResultadoEntrada:
    return ResultadoEntrada(date(2026, 3, numero), numero, *dezenas)


class FiltroDiagonalTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.fotografia = criar_fotografia_historica_diagonal(
            (
                _resultado(1, (4, 15, 26, 37, 48, 59)),
                _resultado(2, (1, 2, 3, 8, 9, 10)),
                _resultado(3, (1, 7, 25, 29, 44, 49)),
            )
        )

    def test_aprova_quando_todas_as_categorias_atingem_o_limite(self) -> None:
        decisao = avaliar_filtro_diagonal(
            (1, 7, 25, 29, 44, 49), self.fotografia, Decimal("10")
        )

        self.assertTrue(decisao.aprovada)
        self.assertEqual("ARRANJOS_DIAGONAIS_ACEITOS", decisao.motivo)
        self.assertEqual(
            ("0D0E", "0D1E", "1D0E", "1D1E"),
            decisao.evidencias["categorias"],
        )
        self.assertEqual((), decisao.evidencias["categorias_raras"])
        self.assertTrue(
            all(not item.rara for item in decisao.evidencias["comparacoes"])
        )

    def test_reprova_se_uma_das_categorias_estiver_abaixo_do_limite(self) -> None:
        decisao = avaliar_filtro_diagonal(
            (1, 4, 26, 48, 50, 60), self.fotografia, Decimal("10")
        )

        self.assertFalse(decisao.aprovada)
        self.assertEqual("ARRANJO_DIAGONAL_RARO", decisao.motivo)
        self.assertIn("0D2E", decisao.evidencias["categorias_raras"])
        comparacao = next(
            item
            for item in decisao.evidencias["comparacoes"]
            if item.codigo == "0D2E"
        )
        self.assertEqual(0, comparacao.ocorrencias)
        self.assertEqual(Decimal("0.000000"), comparacao.percentual)
        self.assertTrue(comparacao.rara)

    def test_sem_referencia_longa_usa_a_mesma_comparacao(self) -> None:
        decisao = avaliar_filtro_diagonal(
            (1, 2, 3, 8, 9, 10), self.fotografia, Decimal("10")
        )

        self.assertTrue(decisao.aprovada)
        self.assertEqual(
            ("SEM_REFERENCIA_LONGA",), decisao.evidencias["categorias"]
        )
        comparacao = decisao.evidencias["comparacoes"][0]
        self.assertEqual(1, comparacao.ocorrencias)
        self.assertEqual(3, comparacao.denominador)

    def test_percentual_igual_ao_limite_e_aprovado(self) -> None:
        decisao = avaliar_filtro_diagonal(
            (4, 15, 26, 37, 48, 59),
            self.fotografia,
            Decimal("33.333333"),
        )

        self.assertTrue(decisao.aprovada)
        self.assertFalse(decisao.evidencias["comparacoes"][0].rara)

    def test_percentual_abaixo_do_limite_e_reprovado(self) -> None:
        decisao = avaliar_filtro_diagonal(
            (4, 15, 26, 37, 48, 59),
            self.fotografia,
            Decimal("33.333334"),
        )

        self.assertFalse(decisao.aprovada)
        self.assertEqual(("0D5E",), decisao.evidencias["categorias_raras"])

    def test_evidencia_identifica_fotografia_e_registros_cadastrais(self) -> None:
        decisao = avaliar_filtro_diagonal(
            (4, 15, 26, 37, 48, 59), self.fotografia, 10
        )

        self.assertEqual("PAD_PG_004", decisao.codigo_filtro)
        self.assertEqual("PG_004", decisao.evidencias["grupo_cod"])
        self.assertEqual("PD_013", decisao.evidencias["padrao_cod"])
        self.assertEqual(3, decisao.evidencias["denominador_historico"])
        self.assertEqual(
            self.fotografia.identificacao_carga,
            decisao.evidencias["identificacao_carga"],
        )

    def test_categoria_ausente_da_fotografia_e_reprovada_mesmo_com_limite_zero(self) -> None:
        incompleta = FotografiaHistoricaDiagonal(
            identificacao_carga=f"sha256:{'0' * 64}",
            versao_calculo=1,
            distribuicao=DistribuicaoCategoriasDiagonais(
                total_resultados=3,
                incidencias=(
                    IncidenciaCategoriaDiagonal(
                        "0D0E", 3, 3, Decimal("100.000000")
                    ),
                ),
            ),
        )

        decisao = avaliar_filtro_diagonal(
            (4, 15, 26, 37, 48, 59), incompleta, Decimal("0")
        )

        self.assertFalse(decisao.aprovada)
        comparacao = decisao.evidencias["comparacoes"][0]
        self.assertFalse(comparacao.encontrada)
        self.assertTrue(comparacao.rara)
        self.assertEqual(Decimal("0.000000"), comparacao.percentual)

    def test_rejeita_fotografia_e_limite_invalidos(self) -> None:
        with self.assertRaises(TypeError):
            avaliar_filtro_diagonal((1, 2, 3, 4, 5, 6), object(), 10)  # type: ignore[arg-type]
        for limite in (-1, 101, "invalido"):
            with self.subTest(limite=limite):
                with self.assertRaises(ValueError):
                    avaliar_filtro_diagonal(
                        (1, 2, 3, 4, 5, 6), self.fotografia, limite
                    )


if __name__ == "__main__":
    unittest.main()
