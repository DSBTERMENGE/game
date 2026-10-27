from dataclasses import replace
from pathlib import Path
import unittest

from msen.screener import carregar_configuracao_screener, executar_pd003_ativo


PADRAO = Path(__file__).resolve().parents[1] / "config" / "screener.toml"


class AtivacaoPD003TestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.configuracao = carregar_configuracao_screener(PADRAO)
        cls.relatorio = executar_pd003_ativo(cls.configuracao)

    def test_contabilidade_da_amostra_protegida(self):
        self.assertEqual(5_000, self.relatorio.total_recebido)
        self.assertEqual(11, self.relatorio.exclusoes_por_criterio["PD_003"])
        self.assertEqual(4_989, self.relatorio.total_aprovado)
        self.assertEqual(5_000, 11 + 4_989)
        self.assertEqual(4_989, self.relatorio.saldo_apos_criterio["PD_003"])

    def test_pd003_avalia_toda_a_amostra(self):
        self.assertEqual(5_000, self.relatorio.avaliacoes_por_criterio["PD_003"])
        self.assertEqual(("PD_003",), self.relatorio.ordem_criterios)

    def test_processamento_integral_permanece_bloqueado(self):
        self.assertEqual("amostra", self.configuracao.modo)
        self.assertFalse(self.configuracao.confirmacao_processamento_integral)
        integral = replace(self.configuracao, modo="integral")
        with self.assertRaises(ValueError):
            executar_pd003_ativo(integral)


if __name__ == "__main__":
    unittest.main()
