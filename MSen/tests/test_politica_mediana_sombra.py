from dataclasses import replace
from decimal import Decimal
from pathlib import Path
import unittest

from msen.screener import (
    AdaptadorMedidasEstatisticas,
    PoliticaMedianaSombra,
    carregar_configuracao_screener,
    mediana_fora_faixa,
)


PADRAO = Path(__file__).resolve().parents[1] / "config" / "screener.toml"


class PoliticaMedianaSombraTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        config = carregar_configuracao_screener(PADRAO)
        criterio = replace(
            config.criterios["medidas_estatisticas"],
            habilitado=True,
            tolerancias={
                "limite_inferior_mediana": 10.5,
                "limite_superior_mediana": 50.5,
            },
        )
        cls.adaptador = AdaptadorMedidasEstatisticas(
            "EST_MEDIANA_P01_P99", criterio, PoliticaMedianaSombra()
        )

    def test_limites_exatos_permanecem_dentro_da_faixa(self):
        inferior = Decimal("10.5")
        superior = Decimal("50.5")
        self.assertFalse(mediana_fora_faixa(inferior, inferior, superior))
        self.assertFalse(mediana_fora_faixa(superior, inferior, superior))

    def test_valores_alem_dos_limites_ficam_fora(self):
        inferior = Decimal("10.5")
        superior = Decimal("50.5")
        self.assertTrue(mediana_fora_faixa(Decimal("10.0"), inferior, superior))
        self.assertTrue(mediana_fora_faixa(Decimal("51.0"), inferior, superior))

    def test_politica_marca_sem_reprovar(self):
        decisao = self.adaptador.avaliar((1, 2, 3, 4, 5, 6))
        self.assertTrue(decisao.aprovada)
        self.assertTrue(decisao.valores["marcaria_exclusao"])
        self.assertEqual("3.5", decisao.valores["mediana"])

    def test_mediana_dentro_da_faixa_passa_sem_marca(self):
        decisao = self.adaptador.avaliar((10, 20, 30, 40, 50, 60))
        self.assertTrue(decisao.aprovada)
        self.assertFalse(decisao.valores["marcaria_exclusao"])
        self.assertEqual("35", decisao.valores["mediana"])


if __name__ == "__main__":
    unittest.main()
