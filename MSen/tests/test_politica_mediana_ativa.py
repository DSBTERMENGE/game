from dataclasses import replace
from pathlib import Path
import unittest

from msen.screener import (
    AdaptadorMedidasEstatisticas,
    PoliticaMedianaAtiva,
    carregar_configuracao_screener,
)


PADRAO = Path(__file__).resolve().parents[1] / "config" / "screener.toml"


class PoliticaMedianaAtivaTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        config = carregar_configuracao_screener(PADRAO)
        regra = config.regras_estatisticas["EST_MEDIANA_P01_P99"]
        criterio = replace(
            config.criterios["medidas_estatisticas"],
            habilitado=True,
            tolerancias={
                "limite_inferior_mediana": regra.limite_inferior,
                "limite_superior_mediana": regra.limite_superior,
            },
        )
        cls.adaptador = AdaptadorMedidasEstatisticas(
            regra.codigo, criterio, PoliticaMedianaAtiva()
        )

    def test_reprova_mediana_fora_da_faixa(self):
        decisao = self.adaptador.avaliar((1, 2, 3, 4, 5, 6))
        self.assertFalse(decisao.aprovada)
        self.assertEqual("reprovou", decisao.valores["decisao"])

    def test_aprova_mediana_dentro_da_faixa(self):
        decisao = self.adaptador.avaliar((10, 20, 30, 40, 50, 60))
        self.assertTrue(decisao.aprovada)
        self.assertEqual("passou", decisao.valores["decisao"])


if __name__ == "__main__":
    unittest.main()
