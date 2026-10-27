import unittest

from tests.suporte_banco_integracao import validar_nome


class SuporteBancoIntegracaoTestCase(unittest.TestCase):
    def test_aceita_somente_nome_temporario_com_identificador_numerico(self):
        self.assertEqual(
            "games_test_7_1_12345",
            validar_nome("games_test_7_1_12345"),
        )

    def test_rejeita_bancos_persistentes_e_nomes_fora_do_padrao(self):
        for nome in (
            "games",
            "postgres",
            "financas",
            "games_test_7_1_",
            "games_test_7_1_abc",
            "games_test_7_1_123; DROP DATABASE games",
        ):
            with self.subTest(nome=nome):
                with self.assertRaises(ValueError):
                    validar_nome(nome)


if __name__ == "__main__":
    unittest.main()
