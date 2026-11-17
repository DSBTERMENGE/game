"""Integração isolada do filtro diagonal ao executor extensível."""

from datetime import date
import unittest

from msen.modelos import ResultadoEntrada
from msen.padroes import criar_fotografia_historica_diagonal
from msen.screener import (
    DecisaoFiltro,
    DefinicaoFamilia,
    DefinicaoFiltro,
    acrescentar_filtro_diagonal,
    executar_funil_extensivel,
)


def _resultado(numero: int, dezenas: tuple[int, ...]) -> ResultadoEntrada:
    return ResultadoEntrada(date(2026, 4, numero), numero, *dezenas)


class IntegracaoFiltroDiagonalFunilTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.fotografia = criar_fotografia_historica_diagonal(
            (
                _resultado(1, (4, 15, 26, 37, 48, 59)),
                _resultado(2, (1, 2, 3, 8, 9, 10)),
                _resultado(3, (1, 7, 25, 29, 44, 49)),
            )
        )

    @staticmethod
    def _familia_com_filtro_anterior() -> DefinicaoFamilia:
        def avaliar_anterior(combinacao):
            excluir = combinacao == (1, 2, 3, 4, 5, 6)
            return DecisaoFiltro.criar(
                codigo_filtro="PAD_ANTERIOR",
                aprovada=not excluir,
                motivo="TESTE",
                evidencias={},
            )

        return DefinicaoFamilia(
            "PADROES",
            "Padrões históricos",
            3,
            (DefinicaoFiltro("PAD_ANTERIOR", "Anterior", 1, avaliar_anterior),),
        )

    def test_acrescenta_um_unico_filtro_ao_final_da_familia(self) -> None:
        familia = acrescentar_filtro_diagonal(
            self._familia_com_filtro_anterior(), self.fotografia, 10
        )

        self.assertEqual(
            ("PAD_ANTERIOR", "PAD_PG_004"),
            tuple(item.codigo for item in familia.filtros),
        )
        self.assertEqual((1, 2), tuple(item.ordem for item in familia.filtros))

    def test_executa_diagonal_uma_vez_por_combinacao_que_chega_ao_filtro(self) -> None:
        familia = acrescentar_filtro_diagonal(
            self._familia_com_filtro_anterior(), self.fotografia, 10
        )
        combinacoes = (
            (1, 2, 3, 4, 5, 6),
            (4, 15, 26, 37, 48, 59),
            (1, 4, 26, 48, 50, 60),
        )

        relatorio = executar_funil_extensivel(
            combinacoes, (familia,), total_combinacoes=3
        )
        linha_anterior, linha_diagonal = relatorio.familias[0].filtros

        self.assertEqual(3, linha_anterior.avaliacoes)
        self.assertEqual(1, linha_anterior.exclusoes)
        self.assertEqual(2, linha_diagonal.avaliacoes)
        self.assertEqual(1, linha_diagonal.exclusoes)
        self.assertEqual(1, relatorio.total_aprovado)

    def test_recusa_familia_errada_duplicidade_e_limite_invalido(self) -> None:
        outra = DefinicaoFamilia("OUTRA", "Outra", 3, ())
        with self.assertRaises(ValueError):
            acrescentar_filtro_diagonal(outra, self.fotografia, 10)
        integrada = acrescentar_filtro_diagonal(
            self._familia_com_filtro_anterior(), self.fotografia, 10
        )
        with self.assertRaises(ValueError):
            acrescentar_filtro_diagonal(integrada, self.fotografia, 10)
        with self.assertRaises(ValueError):
            acrescentar_filtro_diagonal(
                self._familia_com_filtro_anterior(), self.fotografia, 101
            )


if __name__ == "__main__":
    unittest.main()
