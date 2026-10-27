from dataclasses import replace
from decimal import Decimal
from pathlib import Path
import unittest

from msen.screener import (
    AdaptadorMedidasEstatisticas,
    PoliticaDesvioPadraoSombra,
    carregar_configuracao_screener,
    desvio_fora_faixa,
)


PADRAO = Path(__file__).resolve().parents[1] / "config" / "screener.toml"


class PoliticaDesvioSombraTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        config = carregar_configuracao_screener(PADRAO)
        criterio = replace(
            config.criterios["medidas_estatisticas"],
            habilitado=True,
            tolerancias={
                "limite_inferior_desvio": 7.145546,
                "limite_superior_desvio": 22.774694,
            },
        )
        cls.adaptador = AdaptadorMedidasEstatisticas(
            "EST_DESVIO_P01_P99", criterio, PoliticaDesvioPadraoSombra()
        )

    def test_limites_exatos_permanecem_dentro_da_faixa(self):
        inferior = Decimal("7.145546")
        superior = Decimal("22.774694")
        self.assertFalse(desvio_fora_faixa(inferior, inferior, superior))
        self.assertFalse(desvio_fora_faixa(superior, inferior, superior))

    def test_valores_alem_dos_limites_ficam_fora(self):
        inferior = Decimal("7.145546")
        superior = Decimal("22.774694")
        self.assertTrue(desvio_fora_faixa(Decimal("7.145545"), inferior, superior))
        self.assertTrue(desvio_fora_faixa(Decimal("22.774695"), inferior, superior))

    def test_politica_marca_sem_reprovar(self):
        decisao = self.adaptador.avaliar((1, 2, 3, 4, 5, 6))
        self.assertTrue(decisao.aprovada)
        self.assertTrue(decisao.valores["marcaria_exclusao"])
        self.assertEqual("1.707825", decisao.valores["desvio_padrao"])

    def test_desvio_dentro_da_faixa_passa_sem_marca(self):
        decisao = self.adaptador.avaliar((10, 20, 30, 40, 50, 60))
        self.assertTrue(decisao.aprovada)
        self.assertFalse(decisao.valores["marcaria_exclusao"])
        self.assertEqual("17.078251", decisao.valores["desvio_padrao"])


if __name__ == "__main__":
    unittest.main()
