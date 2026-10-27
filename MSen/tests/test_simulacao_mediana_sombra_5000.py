from pathlib import Path
import sys
import unittest

from msen.screener import carregar_configuracao_screener

sys.path.insert(0, str(Path(__file__).resolve().parent))
from simular_mediana_sombra_5000 import executar_mediana_sombra


PADRAO = Path(__file__).resolve().parents[1] / "config" / "screener.toml"


class SimulacaoMedianaSombraTestCase(unittest.TestCase):
    def test_duas_sementes_reproduzem_marcas_sem_excluir(self):
        configuracao = carregar_configuracao_screener(PADRAO)
        esperados = {20261027: 92, 42: 91}
        for semente, esperado in esperados.items():
            with self.subTest(semente=semente):
                resultado = executar_mediana_sombra(semente, configuracao)
                self.assertEqual(5_000, resultado.total_avaliado)
                self.assertEqual(esperado, resultado.total_marcado)
                self.assertEqual(5_000, resultado.total_aprovado_real)
                self.assertEqual(0, resultado.total_excluido_real)


if __name__ == "__main__":
    unittest.main()
