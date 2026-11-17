"""Testes da fotografia histórica diagonal mantida em memória."""

from dataclasses import FrozenInstanceError
from datetime import date
import unittest

from msen.modelos import ResultadoEntrada
from msen.padroes import (
    VERSAO_CALCULO_DIAGONAL,
    criar_fotografia_historica_diagonal,
)


def _resultado(numero: int, dezenas: tuple[int, ...]) -> ResultadoEntrada:
    return ResultadoEntrada(date(2026, 2, numero), numero, *dezenas)


class FotografiaDiagonaisTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.resultados = (
            _resultado(1, (4, 15, 26, 37, 48, 59)),
            _resultado(2, (1, 2, 3, 8, 9, 10)),
            _resultado(3, (1, 7, 25, 29, 44, 49)),
        )

    def test_registra_identificacao_versao_total_e_tabela(self) -> None:
        fotografia = criar_fotografia_historica_diagonal(self.resultados)

        self.assertRegex(fotografia.identificacao_carga, r"^sha256:[0-9a-f]{64}$")
        self.assertEqual(VERSAO_CALCULO_DIAGONAL, fotografia.versao_calculo)
        self.assertEqual(3, fotografia.total_resultados)
        self.assertEqual(22, len(fotografia.incidencias))

    def test_identificacao_independe_da_ordem_da_carga(self) -> None:
        primeira = criar_fotografia_historica_diagonal(self.resultados)
        segunda = criar_fotografia_historica_diagonal(reversed(self.resultados))

        self.assertEqual(primeira, segunda)
        self.assertEqual(primeira.identificacao_carga, segunda.identificacao_carga)

    def test_identificacao_muda_quando_o_historico_muda(self) -> None:
        original = criar_fotografia_historica_diagonal(self.resultados)
        alterados = (*self.resultados[:2], _resultado(3, (2, 7, 25, 29, 44, 49)))
        alterada = criar_fotografia_historica_diagonal(alterados)

        self.assertNotEqual(original.identificacao_carga, alterada.identificacao_carga)

    def test_consulta_indexada_reutiliza_a_incidencia_da_fotografia(self) -> None:
        fotografia = criar_fotografia_historica_diagonal(self.resultados)
        incidencia = fotografia.obter("0D5E")

        self.assertIs(incidencia, fotografia.distribuicao.obter("0D5E"))
        self.assertEqual(1, incidencia.ocorrencias)
        with self.assertRaises(KeyError):
            fotografia.obter("9D9E")

    def test_fotografia_e_seus_dados_sao_imutaveis(self) -> None:
        fotografia = criar_fotografia_historica_diagonal(self.resultados)

        with self.assertRaises(FrozenInstanceError):
            fotografia.versao_calculo = 2  # type: ignore[misc]
        with self.assertRaises(FrozenInstanceError):
            fotografia.incidencias[0].ocorrencias = 99  # type: ignore[misc]


if __name__ == "__main__":
    unittest.main()
