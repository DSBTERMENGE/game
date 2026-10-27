import unittest

from msen.screener import estimar_capacidade


class CapacidadeScreenerTestCase(unittest.TestCase):
    def test_extrapola_tempo_e_armazenamento_linearmente(self):
        estimativa = estimar_capacidade(5_000, 2.5, 500_000)
        fator = 50_063_860 / 5_000
        self.assertEqual(2_000.0, estimativa.combinacoes_por_segundo)
        self.assertAlmostEqual(2.5 * fator, estimativa.duracao_universo_segundos)
        self.assertAlmostEqual(500_000 * fator, estimativa.bytes_universo)

    def test_aceita_estimativa_sem_armazenamento(self):
        estimativa = estimar_capacidade(5_000, 0.5)
        self.assertEqual(0, estimativa.bytes_universo)

    def test_rejeita_parametros_invalidos(self):
        for argumentos in ((0, 1, 0), (1, 0, 0), (1, 1, -1)):
            with self.subTest(argumentos=argumentos):
                with self.assertRaises(ValueError):
                    estimar_capacidade(*argumentos)


if __name__ == "__main__":
    unittest.main()
