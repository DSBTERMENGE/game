"""Casos determinísticos do critério diagonal ainda não ativado no banco."""

import unittest

from msen.validacao import (
    criar_definicao_criterio_diagonal,
    criar_registro_criterios_producao,
)


class CriterioValidacaoDiagonalTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.criterio = criar_definicao_criterio_diagonal()

    def test_define_contrato_categorico_do_grupo_pg004(self) -> None:
        self.assertEqual("PAD_PG_004", self.criterio.codigo)
        self.assertEqual("PADRAO", self.criterio.categoria)
        self.assertEqual("CATEGORICO", self.criterio.tipo_resultado)
        self.assertEqual("PG_004", self.criterio.grupo_codigo)
        self.assertIsNone(self.criterio.precisao_decimal)
        self.assertRegex(self.criterio.assinatura_funcao, r"^[0-9a-f]{64}$")
        self.assertRegex(self.criterio.assinatura_regra, r"^[0-9a-f]{64}$")

    def test_casos_de_aceitacao_possuem_resposta_canonica(self) -> None:
        casos = (
            ((4, 15, 26, 37, 48, 59), "0D5E"),
            ((1, 2, 3, 8, 9, 10), "SEM_REFERENCIA_LONGA"),
            ((1, 7, 25, 29, 44, 49), "0D0E|0D1E|1D0E|1D1E"),
            ((15, 17, 26, 35, 37, 60), "0D2E|2D0E|2D2E"),
        )
        for dezenas, esperado in casos:
            with self.subTest(dezenas=dezenas):
                self.assertEqual(esperado, self.criterio.funcao(dezenas))

    def test_ordem_da_entrada_nao_altera_valor_categorico(self) -> None:
        dezenas = (1, 7, 25, 29, 44, 49)

        self.assertEqual(
            self.criterio.funcao(dezenas),
            self.criterio.funcao(tuple(reversed(dezenas))),
        )

    def test_criterio_integra_o_catalogo_apos_migracao_validada(self) -> None:
        ativos = {item.codigo for item in criar_registro_criterios_producao().listar()}

        self.assertIn("PAD_PG_004", ativos)


if __name__ == "__main__":
    unittest.main()
