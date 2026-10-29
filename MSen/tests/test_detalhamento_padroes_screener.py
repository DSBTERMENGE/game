from datetime import date
from decimal import Decimal
import unittest

from msen.api.screener_extensivel_service import ErroEnsaioExtensivel, _detalhar_padroes
from msen.database import PadraoPersistido
from msen.screener import FrequenciaPadraoFotografada, criar_grupo_padroes_fotografado


class DetalhamentoPadroesScreenerTests(unittest.TestCase):
    def setUp(self):
        selecionados = {2, 3, 5, 6, 9}
        self.padroes = tuple(
            PadraoPersistido(
                numero, f"PD_{numero:03d}", f"Padrão {numero}", "Descrição",
                numero, None, None, numero // 3 + 1,
                f"PG_{((numero - 1) // 3) + 1:03d}",
                f"Grupo {((numero - 1) // 3) + 1}", 100, Decimal(numero),
            )
            for numero in range(1, 10) if numero in selecionados
        )
        raros = {
            "PG_001": ("PD_002", "PD_003"),
            "PG_002": ("PD_005", "PD_006"),
            "PG_003": ("PD_009",),
        }
        self.grupos = tuple(
            criar_grupo_padroes_fotografado(
                grupo_cod=grupo, limite_raridade=10, operador="<",
                numero_ap_inicial=1, numero_ap_final=100,
                data_inicial=date(2020, 1, 1), data_final=date(2026, 10, 29),
                denominador=100,
                frequencias=tuple(
                    FrequenciaPadraoFotografada(
                        codigo, int(codigo[-3:]), Decimal(int(codigo[-3:]))
                    )
                    for codigo in codigos
                ),
            )
            for grupo, codigos in raros.items()
        )
        self.familia = {
            "entrada": 100, "exclusoes": 18, "saldo": 82,
            "filtros": [
                {"codigo": "PAD_PD_002", "entrada": 100, "avaliacoes": 100, "exclusoes": 10, "saldo": 90},
                {"codigo": "PAD_PD_003", "entrada": 90, "avaliacoes": 90, "exclusoes": 0, "saldo": 90},
                {"codigo": "PAD_PD_005", "entrada": 90, "avaliacoes": 90, "exclusoes": 5, "saldo": 85},
                {"codigo": "PAD_PD_006", "entrada": 85, "avaliacoes": 85, "exclusoes": 0, "saldo": 85},
                {"codigo": "PAD_PD_009", "entrada": 85, "avaliacoes": 85, "exclusoes": 3, "saldo": 82},
            ],
        }

    def test_exibe_somente_selecionados_e_fecha_grupos_familia_e_total(self):
        dados = _detalhar_padroes(
            padroes=self.padroes,
            grupos_fotografados=self.grupos,
            familia_serializada=self.familia,
            limite=Decimal(10),
            operador="<",
        )

        self.assertEqual(5, sum(len(item["padroes"]) for item in dados["grupos"]))
        self.assertTrue(all(item["reconciliado"] for item in dados["grupos"]))
        self.assertEqual(
            ("APLICADO_RARO", "APLICADO_RARO"),
            tuple(item["estado"] for item in dados["grupos"][0]["padroes"]),
        )
        self.assertEqual(10, dados["grupos"][0]["padroes"][0]["correspondencias"])
        self.assertEqual(100, dados["grupos"][0]["padroes"][0]["avaliacoes"])
        self.assertEqual(90, dados["grupos"][0]["padroes"][0]["saldo"])
        self.assertEqual(
            {"entrada": 100, "exclusoes": 18, "saldo": 82, "valido": True},
            dados["fechamento"],
        )

    def test_recusa_entrada_de_padrao_adulterada(self):
        adulterada = {**self.familia, "filtros": [dict(item) for item in self.familia["filtros"]]}
        adulterada["filtros"][1]["entrada"] = 999
        with self.assertRaises(ErroEnsaioExtensivel) as contexto:
            _detalhar_padroes(
                padroes=self.padroes,
                grupos_fotografados=self.grupos,
                familia_serializada=adulterada,
                limite=Decimal(10),
                operador="<",
            )
        self.assertEqual("ENTRADA_PADRAO_DIVERGENTE", contexto.exception.codigo)


if __name__ == "__main__":
    unittest.main()
