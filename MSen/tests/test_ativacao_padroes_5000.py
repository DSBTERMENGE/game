from dataclasses import replace
from pathlib import Path
import unittest

from msen.screener import carregar_configuracao_screener, executar_padroes_ativos


PADRAO = Path(__file__).resolve().parents[1] / "config" / "screener.toml"


class AtivacaoPadroesTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.configuracao = carregar_configuracao_screener(PADRAO)
        cls.relatorio = executar_padroes_ativos(cls.configuracao)

    def test_contabiliza_cada_regra_e_o_saldo(self):
        self.assertEqual(5_000, self.relatorio.total_recebido)
        self.assertEqual(11, self.relatorio.exclusoes_por_criterio["PD_003"])
        self.assertEqual(162, self.relatorio.exclusoes_por_criterio["PD_002"])
        self.assertEqual(5, self.relatorio.exclusoes_por_criterio["PD_006"])
        self.assertEqual(110, self.relatorio.exclusoes_por_criterio["PD_005"])
        self.assertEqual(
            89, self.relatorio.exclusoes_por_criterio["EST_MEDIA_P01_P99"]
        )
        self.assertEqual(
            95, self.relatorio.exclusoes_por_criterio["EST_DESVIO_P01_P99"]
        )
        self.assertEqual(
            44, self.relatorio.exclusoes_por_criterio["EST_MEDIANA_P01_P99"]
        )
        self.assertEqual(
            75, self.relatorio.exclusoes_por_criterio["GEO_EXTENSAO_P01_P99"]
        )
        self.assertEqual(4_409, self.relatorio.total_aprovado)
        self.assertEqual(5_000, 11 + 162 + 5 + 110 + 89 + 95 + 44 + 75 + 4_409)
        self.assertEqual(4_989, self.relatorio.saldo_apos_criterio["PD_003"])
        self.assertEqual(4_827, self.relatorio.saldo_apos_criterio["PD_002"])
        self.assertEqual(4_822, self.relatorio.saldo_apos_criterio["PD_006"])
        self.assertEqual(4_712, self.relatorio.saldo_apos_criterio["PD_005"])
        self.assertEqual(
            4_623, self.relatorio.saldo_apos_criterio["EST_MEDIA_P01_P99"]
        )
        self.assertEqual(
            4_528, self.relatorio.saldo_apos_criterio["EST_DESVIO_P01_P99"]
        )
        self.assertEqual(
            4_484, self.relatorio.saldo_apos_criterio["EST_MEDIANA_P01_P99"]
        )
        self.assertEqual(
            4_409, self.relatorio.saldo_apos_criterio["GEO_EXTENSAO_P01_P99"]
        )

    def test_respeita_ordem_e_interrompe_apos_exclusao(self):
        self.assertEqual(
            (
                "PD_003",
                "PD_002",
                "PD_006",
                "PD_005",
                "EST_MEDIA_P01_P99",
                "EST_DESVIO_P01_P99",
                "EST_MEDIANA_P01_P99",
                "GEO_EXTENSAO_P01_P99",
            ),
            self.relatorio.ordem_criterios,
        )
        self.assertEqual(5_000, self.relatorio.avaliacoes_por_criterio["PD_003"])
        self.assertEqual(4_989, self.relatorio.avaliacoes_por_criterio["PD_002"])
        self.assertEqual(4_827, self.relatorio.avaliacoes_por_criterio["PD_006"])
        self.assertEqual(4_822, self.relatorio.avaliacoes_por_criterio["PD_005"])
        self.assertEqual(
            4_712, self.relatorio.avaliacoes_por_criterio["EST_MEDIA_P01_P99"]
        )
        self.assertEqual(
            4_623, self.relatorio.avaliacoes_por_criterio["EST_DESVIO_P01_P99"]
        )
        self.assertEqual(
            4_528, self.relatorio.avaliacoes_por_criterio["EST_MEDIANA_P01_P99"]
        )
        self.assertEqual(
            4_484, self.relatorio.avaliacoes_por_criterio["GEO_EXTENSAO_P01_P99"]
        )

    def test_processamento_integral_permanece_bloqueado(self):
        integral = replace(self.configuracao, modo="integral")
        with self.assertRaises(ValueError):
            executar_padroes_ativos(integral)


if __name__ == "__main__":
    unittest.main()
