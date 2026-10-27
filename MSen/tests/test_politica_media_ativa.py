from dataclasses import replace
from pathlib import Path
import unittest

from msen.screener import (
    AdaptadorMedidasEstatisticas,
    PoliticaMediaAtiva,
    carregar_configuracao_screener,
)


PADRAO = Path(__file__).resolve().parents[1] / "config" / "screener.toml"


class PoliticaMediaAtivaTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        config = carregar_configuracao_screener(PADRAO)
        regra = config.regras_estatisticas["EST_MEDIA_P01_P99"]
        criterio = replace(
            config.criterios["medidas_estatisticas"],
            habilitado=True,
            tolerancias={
                "limite_inferior_media": regra.limite_inferior,
                "limite_superior_media": regra.limite_superior,
            },
        )
        cls.adaptador = AdaptadorMedidasEstatisticas(
            regra.codigo, criterio, PoliticaMediaAtiva()
        )

    def test_reprova_media_fora_da_faixa(self):
        decisao = self.adaptador.avaliar((1, 2, 3, 4, 5, 6))
        self.assertFalse(decisao.aprovada)
        self.assertEqual("reprovou", decisao.valores["decisao"])

    def test_aprova_media_dentro_da_faixa(self):
        decisao = self.adaptador.avaliar((10, 20, 30, 40, 50, 60))
        self.assertTrue(decisao.aprovada)
        self.assertEqual("passou", decisao.valores["decisao"])


if __name__ == "__main__":
    unittest.main()
