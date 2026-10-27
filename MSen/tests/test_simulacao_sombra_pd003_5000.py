from pathlib import Path
import sys
import unittest

from msen.screener import carregar_configuracao_screener

sys.path.insert(0, str(Path(__file__).resolve().parent))
from simular_pd003_sombra_5000 import _executar


PADRAO = Path(__file__).resolve().parents[1] / "config" / "screener.toml"


class SimulacaoSombraPD003AmostraTestCase(unittest.TestCase):
    def test_duas_sementes_reproduzem_contagens_sem_exclusao(self):
        configuracao = carregar_configuracao_screener(PADRAO)
        resultados = {
            semente: _executar(semente, configuracao) for semente in (20261027, 42)
        }
        self.assertEqual(11, resultados[20261027].total_marcado)
        self.assertEqual(5, resultados[42].total_marcado)
        for resultado in resultados.values():
            self.assertEqual(5_000, resultado.total_avaliado)
            self.assertEqual(5_000, resultado.total_aprovado_real)
            self.assertEqual(0, resultado.total_excluido_real)


if __name__ == "__main__":
    unittest.main()
