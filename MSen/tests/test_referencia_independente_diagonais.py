"""Casos manuais do oráculo independente de diagonais."""

import unittest

from referencia_independente_diagonais import (
    calcular_referencia_categorias_diagonais,
)


class ReferenciaIndependenteDiagonaisTestCase(unittest.TestCase):
    def test_casos_manuais_documentados(self) -> None:
        casos = (
            ((4, 15, 26, 37, 48, 59), "0D5E"),
            ((1, 2, 3, 8, 9, 10), "SEM_REFERENCIA_LONGA"),
            ((1, 7, 25, 29, 44, 49), "0D0E|0D1E|1D0E|1D1E"),
            ((15, 17, 26, 35, 37, 60), "0D2E|2D0E|2D2E"),
        )
        for dezenas, esperado in casos:
            with self.subTest(dezenas=dezenas):
                self.assertEqual(
                    esperado, calcular_referencia_categorias_diagonais(dezenas)
                )

    def test_salto_numerico_que_cruza_borda_nao_e_diagonal(self) -> None:
        resposta = calcular_referencia_categorias_diagonais(
            (4, 10, 22, 40, 50, 60)
        )

        self.assertNotIn("2D", resposta)

    def test_ordem_da_entrada_nao_altera_referencia(self) -> None:
        dezenas = (1, 7, 25, 29, 44, 49)
        self.assertEqual(
            calcular_referencia_categorias_diagonais(dezenas),
            calcular_referencia_categorias_diagonais(tuple(reversed(dezenas))),
        )


if __name__ == "__main__":
    unittest.main()
