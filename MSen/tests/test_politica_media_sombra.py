from dataclasses import replace
from decimal import Decimal
from pathlib import Path
import unittest

from msen.screener import (
    AdaptadorMedidasEstatisticas,
    PoliticaMediaSombra,
    carregar_configuracao_screener,
    media_fora_faixa,
)


PADRAO = Path(__file__).resolve().parents[1] / "config" / "screener.toml"


class PoliticaMediaSombraTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        config = carregar_configuracao_screener(PADRAO)
        criterio = replace(
            config.criterios["medidas_estatisticas"],
            habilitado=True,
            tolerancias={
                "limite_inferior_media": 15.0,
                "limite_superior_media": 45.886666,
            },
        )
        cls.adaptador = AdaptadorMedidasEstatisticas(
            "EST_MEDIA_P01_P99", criterio, PoliticaMediaSombra()
        )

    def test_limites_exatos_permanecem_dentro_da_faixa(self):
        self.assertFalse(
            media_fora_faixa(Decimal("15"), Decimal("15"), Decimal("45.886666"))
        )
        self.assertFalse(
            media_fora_faixa(
                Decimal("45.886666"), Decimal("15"), Decimal("45.886666")
            )
        )

    def test_valores_alem_dos_limites_ficam_fora(self):
        self.assertTrue(
            media_fora_faixa(
                Decimal("14.999999"), Decimal("15"), Decimal("45.886666")
            )
        )
        self.assertTrue(
            media_fora_faixa(
                Decimal("45.886667"), Decimal("15"), Decimal("45.886666")
            )
        )

    def test_politica_marca_sem_reprovar(self):
        decisao = self.adaptador.avaliar((1, 2, 3, 4, 5, 6))
        self.assertTrue(decisao.aprovada)
        self.assertTrue(decisao.valores["marcaria_exclusao"])
        self.assertEqual("3.500000", decisao.valores["media"])

    def test_media_dentro_da_faixa_passa_sem_marca(self):
        decisao = self.adaptador.avaliar((10, 20, 30, 40, 50, 60))
        self.assertTrue(decisao.aprovada)
        self.assertFalse(decisao.valores["marcaria_exclusao"])
        self.assertEqual("35.000000", decisao.valores["media"])

    def test_limites_invertidos_sao_rejeitados(self):
        with self.assertRaises(ValueError):
            media_fora_faixa(Decimal("20"), Decimal("30"), Decimal("10"))


if __name__ == "__main__":
    unittest.main()
