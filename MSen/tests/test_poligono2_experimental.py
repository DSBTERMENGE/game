import unittest

from msen.geometria import analisar_poligono2_experimental


class Poligono2ExperimentalTest(unittest.TestCase):
    def test_diagnostico_preserva_as_seis_dezenas_e_duas_escolhas_por_origem(self):
        analise = analisar_poligono2_experimental((1, 6, 10, 41, 55, 60))

        self.assertEqual((1, 6, 10, 41, 55, 60), tuple(x[0] for x in analise.graus))
        self.assertEqual(6, len(analise.escolhas_por_dezena))
        self.assertTrue(all(len(destinos) == 2 for _, destinos in analise.escolhas_por_dezena))
        self.assertGreaterEqual(analise.quantidade_arestas, 6)

    def test_excedentes_sao_informados_sem_eliminacao_automatica(self):
        analise = analisar_poligono2_experimental((1, 2, 3, 11, 12, 60))

        self.assertEqual(analise.quantidade_arestas, len(analise.arestas))
        self.assertEqual(analise.circuito_pronto, (
            analise.quantidade_arestas == 6
            and analise.conectado
            and not analise.possui_cruzamento
            and all(grau == 2 for _, grau in analise.graus)
        ))

    def test_resultado_independe_da_ordem_de_entrada(self):
        primeira = analisar_poligono2_experimental((1, 6, 10, 41, 55, 60))
        segunda = analisar_poligono2_experimental((60, 10, 55, 1, 41, 6))
        self.assertEqual(primeira, segunda)

    def test_reutiliza_validacao_das_seis_dezenas(self):
        with self.assertRaisesRegex(ValueError, "exatamente seis"):
            analisar_poligono2_experimental((1, 2, 3))
        with self.assertRaisesRegex(ValueError, "devem ser diferentes"):
            analisar_poligono2_experimental((1, 1, 2, 3, 4, 5))


if __name__ == "__main__":
    unittest.main()
