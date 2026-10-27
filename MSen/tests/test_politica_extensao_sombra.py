from dataclasses import replace
from decimal import Decimal
from pathlib import Path
import unittest

from msen.screener import (
    AdaptadorMedidasGeometricas,
    PoliticaExtensaoSombra,
    carregar_configuracao_screener,
    extensao_fora_faixa,
)


PADRAO = Path(__file__).resolve().parents[1] / "config" / "screener.toml"


class PoliticaExtensaoSombraTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        config = carregar_configuracao_screener(PADRAO)
        criterio = replace(
            config.criterios["medidas_geometricas"],
            habilitado=True,
            tolerancias={
                "limite_inferior_extensao": 8.650282,
                "limite_superior_extensao": 32.300058,
            },
        )
        cls.adaptador = AdaptadorMedidasGeometricas(
            "GEO_EXTENSAO_P01_P99", criterio, PoliticaExtensaoSombra()
        )

    def test_limites_exatos_permanecem_dentro_da_faixa(self):
        inferior = Decimal("8.650282")
        superior = Decimal("32.300058")
        self.assertFalse(extensao_fora_faixa(inferior, inferior, superior))
        self.assertFalse(extensao_fora_faixa(superior, inferior, superior))

    def test_valores_alem_dos_limites_ficam_fora(self):
        inferior = Decimal("8.650282")
        superior = Decimal("32.300058")
        self.assertTrue(extensao_fora_faixa(Decimal("8.650281"), inferior, superior))
        self.assertTrue(extensao_fora_faixa(Decimal("32.300059"), inferior, superior))

    def test_politica_marca_extensao_baixa_sem_reprovar(self):
        decisao = self.adaptador.avaliar((1, 2, 3, 4, 5, 6))
        self.assertTrue(decisao.aprovada)
        self.assertTrue(decisao.valores["marcaria_exclusao"])
        self.assertEqual("5.000000000000", decisao.valores["extensao_aberta"])

    def test_extensao_dentro_da_faixa_passa_sem_marca(self):
        decisao = self.adaptador.avaliar((1, 5, 12, 18, 24, 30))
        self.assertTrue(decisao.aprovada)
        self.assertFalse(decisao.valores["marcaria_exclusao"])


if __name__ == "__main__":
    unittest.main()
