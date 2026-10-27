import unittest

from msen.screener import gerar_quadro_screener


class QuadroScreenerAtivoTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dados = gerar_quadro_screener(12)

    def test_monta_quadro_dos_oito_filtros(self):
        self.assertEqual(5_000, self.dados["total_recebido"])
        self.assertEqual(4_409, self.dados["total_aprovado"])
        self.assertEqual(8, len(self.dados["linhas"]))
        self.assertEqual("PD_003", self.dados["linhas"][0]["codigo_criterio"])
        self.assertEqual(
            "GEO_EXTENSAO_P01_P99", self.dados["linhas"][-1]["codigo_criterio"]
        )

    def test_fornece_casos_pendentes_de_validacao_humana(self):
        self.assertEqual(12, len(self.dados["validacoes"]))
        for caso in self.dados["validacoes"]:
            self.assertEqual(6, len(caso["combinacao"]))
            self.assertIn(caso["resultado_obtido"], {"aprovar", "excluir"})
            self.assertIsNone(caso["resultado_esperado"])
            self.assertIsNone(caso["conformidade"])

    def test_rejeita_quantidade_fora_da_protecao(self):
        for limite in (0, 201, True):
            with self.subTest(limite=limite), self.assertRaises(ValueError):
                gerar_quadro_screener(limite)


if __name__ == "__main__":
    unittest.main()
