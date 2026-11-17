"""Testes do contrato público do analisador categórico diagonal."""

from dataclasses import fields
from typing import get_type_hints
import unittest

from msen.padroes import (
    AnaliseAssinaturasDiagonais,
    AnaliseReferenciaDiagonal,
    AssinaturaDiagonal,
    CATEGORIA_SEM_REFERENCIA_LONGA,
    analisar_assinaturas_diagonais,
)


class ContratoAnalisadorDiagonalTestCase(unittest.TestCase):
    def test_funcao_publica_recebe_tupla_e_devolve_analise_auditavel(self) -> None:
        tipos = get_type_hints(analisar_assinaturas_diagonais)

        self.assertEqual(tuple[int, ...], tipos["dezenas"])
        self.assertIs(AnaliseAssinaturasDiagonais, tipos["return"])

    def test_analise_consolida_entrada_referencias_e_assinaturas(self) -> None:
        self.assertEqual(
            ("dezenas_ordenadas", "referencias", "assinaturas"),
            tuple(campo.name for campo in fields(AnaliseAssinaturasDiagonais)),
        )
        self.assertEqual(
            (
                "posicao",
                "dezena",
                "diagonal_direita",
                "diagonal_esquerda",
                "assinatura",
            ),
            tuple(campo.name for campo in fields(AnaliseReferenciaDiagonal)),
        )

    def test_assinatura_publica_possui_as_duas_contagens(self) -> None:
        self.assertEqual(
            ("direita", "esquerda"),
            tuple(campo.name for campo in fields(AssinaturaDiagonal)),
        )

    def test_categoria_sem_referencia_longa_tem_codigo_estavel(self) -> None:
        self.assertEqual(
            "SEM_REFERENCIA_LONGA", CATEGORIA_SEM_REFERENCIA_LONGA
        )


if __name__ == "__main__":
    unittest.main()
