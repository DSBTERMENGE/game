from dataclasses import replace
from pathlib import Path
import random
import unittest

from msen.screener import (
    ErroGeracaoAmostra,
    carregar_configuracao_screener,
    gerar_amostra,
)

PADRAO = Path(__file__).resolve().parents[1] / "config" / "screener.toml"


class GeradorAmostralTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.configuracao = carregar_configuracao_screener(PADRAO)
        cls.amostra = gerar_amostra(cls.configuracao)

    def test_gera_exatamente_cinco_mil_combinacoes_distintas(self):
        self.assertEqual(5_000, len(self.amostra))
        self.assertEqual(5_000, len(set(self.amostra)))

    def test_cada_combinacao_possui_seis_dezenas_validas_e_ordenadas(self):
        for combinacao in self.amostra:
            self.assertEqual(6, len(combinacao))
            self.assertEqual(tuple(sorted(combinacao)), combinacao)
            self.assertEqual(6, len(set(combinacao)))
            self.assertGreaterEqual(combinacao[0], 1)
            self.assertLessEqual(combinacao[-1], 60)

    def test_mesma_semente_reproduz_exatamente_a_mesma_amostra(self):
        repetida = gerar_amostra(self.configuracao)
        self.assertEqual(self.amostra, repetida)

    def test_semente_diferente_produz_amostra_diferente(self):
        outra = gerar_amostra(replace(self.configuracao, semente=42))
        self.assertNotEqual(self.amostra, outra)

    def test_nao_altera_estado_aleatorio_global(self):
        random.seed(1234)
        esperado = random.random()
        random.seed(1234)
        gerar_amostra(self.configuracao)
        self.assertEqual(esperado, random.random())

    def test_rejeita_modo_integral(self):
        integral = replace(self.configuracao, modo="integral")
        with self.assertRaises(ErroGeracaoAmostra) as contexto:
            gerar_amostra(integral)
        self.assertEqual("MODO_NAO_AMOSTRAL", contexto.exception.codigo)

    def test_exige_configuracao_validada(self):
        with self.assertRaises(TypeError):
            gerar_amostra(object())


if __name__ == "__main__":
    unittest.main()
