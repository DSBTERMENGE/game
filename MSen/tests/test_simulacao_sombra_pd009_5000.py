from pathlib import Path
import sys
import unittest

from msen.screener import carregar_configuracao_screener

sys.path.insert(0, str(Path(__file__).resolve().parent))
from simular_pd009_sombra_5000 import executar_pd009_sombra


PADRAO = Path(__file__).resolve().parents[1] / "config" / "screener.toml"


class SimulacaoSombraPD009AmostraTestCase(unittest.TestCase):
    def test_detecta_padrao_mas_nao_marca_acima_da_tolerancia(self):
        configuracao = carregar_configuracao_screener(PADRAO)
        esperado = {20261027: 177, 42: 154}
        for semente, detectadas_esperadas in esperado.items():
            with self.subTest(semente=semente):
                resultado, detectadas = executar_pd009_sombra(semente, configuracao)
                self.assertEqual(detectadas_esperadas, detectadas)
                self.assertEqual(0, resultado.total_marcado)
                self.assertEqual(5_000, resultado.total_aprovado_real)
                self.assertEqual(0, resultado.total_excluido_real)


if __name__ == "__main__":
    unittest.main()
