import unittest

from msen.api.screener_extensivel_service import (
    PadraoAtivoScreener,
    _detalhar_padroes_ativos,
)


class DetalhamentoPadroesScreenerTests(unittest.TestCase):
    def setUp(self):
        self.padroes = (
            PadraoAtivoScreener(2, "PD_002", "Padrão 2", "PG_001", "Grupo 1", lambda _: False),
            PadraoAtivoScreener(3, "PD_003", "Padrão 3", "PG_001", "Grupo 1", lambda _: False),
            PadraoAtivoScreener(5, "PD_005", "Padrão 5", "PG_002", "Grupo 2", lambda _: False),
        )
        self.familia = {
            "entrada": 100, "exclusoes": 15, "saldo": 85,
            "filtros": [
                {"codigo": "PAD_PD_002", "entrada": 100, "avaliacoes": 100, "exclusoes": 10, "saldo": 90},
                {"codigo": "PAD_PD_003", "entrada": 90, "avaliacoes": 90, "exclusoes": 0, "saldo": 90},
                {"codigo": "PAD_PD_005", "entrada": 90, "avaliacoes": 90, "exclusoes": 5, "saldo": 85},
            ],
        }

    def test_exibe_todos_os_padroes_ativos_e_fecha_os_grupos(self):
        dados = _detalhar_padroes_ativos(
            padroes=self.padroes, familia_serializada=self.familia
        )

        self.assertEqual(3, sum(len(item["padroes"]) for item in dados["grupos"]))
        self.assertEqual(100, dados["grupos"][0]["entrada"])
        self.assertEqual(10, dados["grupos"][0]["exclusoes"])
        self.assertEqual(90, dados["grupos"][0]["saldo"])
        self.assertEqual(5, dados["grupos"][1]["exclusoes"])
        self.assertEqual(85, dados["grupos"][1]["saldo"])
        self.assertEqual(2, dados["grupos"][0]["padroes"][0]["id_padrao"])
        self.assertEqual(100, dados["grupos"][0]["padroes"][0]["avaliacoes"])

    def test_ignora_filtro_categorico_legado_no_detalhamento(self):
        familia = {
            **self.familia,
            "filtros": [
                *self.familia["filtros"],
                {"codigo": "PAD_PG_004", "entrada": 85, "avaliacoes": 85, "exclusoes": 2, "saldo": 83},
            ],
        }
        dados = _detalhar_padroes_ativos(
            padroes=self.padroes, familia_serializada=familia
        )
        self.assertEqual(3, sum(len(item["padroes"]) for item in dados["grupos"]))


if __name__ == "__main__":
    unittest.main()
