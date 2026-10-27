from dataclasses import replace
from pathlib import Path
import unittest

from msen.screener import (
    AdaptadorMedidasEstatisticas,
    PoliticaDesvioPadraoAtiva,
    carregar_configuracao_screener,
)


PADRAO = Path(__file__).resolve().parents[1] / "config" / "screener.toml"


class PoliticaDesvioAtivaTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        config = carregar_configuracao_screener(PADRAO)
        regra = config.regras_estatisticas["EST_DESVIO_P01_P99"]
        criterio = replace(
            config.criterios["medidas_estatisticas"],
            habilitado=True,
            tolerancias={
                "limite_inferior_desvio": regra.limite_inferior,
                "limite_superior_desvio": regra.limite_superior,
            },
        )
        cls.adaptador = AdaptadorMedidasEstatisticas(
            regra.codigo, criterio, PoliticaDesvioPadraoAtiva()
        )

    def test_reprova_desvio_fora_da_faixa(self):
        decisao = self.adaptador.avaliar((1, 2, 3, 4, 5, 6))
        self.assertFalse(decisao.aprovada)
        self.assertEqual("reprovou", decisao.valores["decisao"])

    def test_aprova_desvio_dentro_da_faixa(self):
        decisao = self.adaptador.avaliar((10, 20, 30, 40, 50, 60))
        self.assertTrue(decisao.aprovada)
        self.assertEqual("passou", decisao.valores["decisao"])


if __name__ == "__main__":
    unittest.main()
