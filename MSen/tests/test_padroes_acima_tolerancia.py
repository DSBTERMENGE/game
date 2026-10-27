from pathlib import Path
import sys
import unittest

from msen.screener import carregar_configuracao_screener

sys.path.insert(0, str(Path(__file__).resolve().parent))
from avaliar_padroes_acima_tolerancia import simular_padroes


PADRAO = Path(__file__).resolve().parents[1] / "config" / "screener.toml"
OCORRENCIAS = {"PD_001": 1192, "PD_004": 1037, "PD_007": 2053, "PD_008": 863}
DETECCOES = {
    20261027: {"PD_001": 1937, "PD_004": 1708, "PD_007": 3305, "PD_008": 1431},
    42: {"PD_001": 1963, "PD_004": 1721, "PD_007": 3393, "PD_008": 1361},
}


class PadroesAcimaToleranciaTestCase(unittest.TestCase):
    def test_detectores_encontram_mas_politica_nao_marca(self):
        configuracao = carregar_configuracao_screener(PADRAO)
        for semente, deteccoes in DETECCOES.items():
            resultados = simular_padroes(semente, configuracao, OCORRENCIAS)
            for codigo, detectadas in deteccoes.items():
                with self.subTest(semente=semente, codigo=codigo):
                    self.assertEqual(detectadas, resultados[codigo]["total_detectado_bruto"])
                    self.assertEqual(0, resultados[codigo]["total_marcado"])
                    self.assertEqual(5_000, resultados[codigo]["total_aprovado_real"])
                    self.assertEqual(0, resultados[codigo]["total_excluido_real"])


if __name__ == "__main__":
    unittest.main()
