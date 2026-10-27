import unittest

from msen.screener import PoliticaExtensaoAtiva


LIMITES = {
    "limite_inferior_extensao": 8.650282,
    "limite_superior_extensao": 32.300058,
}


class PoliticaExtensaoAtivaTestCase(unittest.TestCase):
    def test_exclui_extensao_abaixo_da_faixa(self):
        resultado = PoliticaExtensaoAtiva()((1, 2, 3, 4, 5, 6), LIMITES)
        self.assertFalse(resultado.aprovada)
        self.assertEqual("excluir", resultado.valores["decisao"])

    def test_aprova_extensao_dentro_da_faixa(self):
        resultado = PoliticaExtensaoAtiva()((1, 10, 20, 30, 40, 50), LIMITES)
        self.assertTrue(resultado.aprovada)
        self.assertEqual("aprovar", resultado.valores["decisao"])


if __name__ == "__main__":
    unittest.main()
