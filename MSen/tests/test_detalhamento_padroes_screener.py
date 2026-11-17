from datetime import date
from decimal import Decimal
import unittest
from types import SimpleNamespace

from msen.api.screener_extensivel_service import (
    ErroEnsaioExtensivel,
    _detalhar_padroes,
    _grupos_raros_fotografados,
)
from msen.database import PadraoPersistido
from msen.screener import FrequenciaPadraoFotografada, criar_grupo_padroes_fotografado
from msen.services.selecao_padroes import SelecaoPadroesRaros


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

    def test_fecha_padroes_individuais_antes_de_filtro_categorico(self):
        familia = {
            **self.familia,
            "exclusoes": 20,
            "saldo": 80,
            "filtros": [
                *self.familia["filtros"],
                {
                    "codigo": "PAD_PG_004", "entrada": 82,
                    "avaliacoes": 82, "exclusoes": 2, "saldo": 80,
                },
            ],
        }
        dados = _detalhar_padroes(
            padroes=self.padroes,
            grupos_fotografados=self.grupos,
            familia_serializada=familia,
            limite=Decimal(10),
            operador="<",
        )
        self.assertEqual(
            {"entrada": 100, "exclusoes": 18, "saldo": 82, "valido": True},
            dados["fechamento"],
        )

    def test_aceita_grupo_novo_quando_padrao_ja_foi_selecionado(self):
        padrao = PadraoPersistido(
            17, "PD_011", "Dezenas em duas linhas", "Descrição", 32,
            Decimal("84.709677"), Decimal("67.912274"), 8,
            "PG_007", "Dezenas em duas linhas", 3069, Decimal("1.042685"),
        )
        perfil = SimpleNamespace(
            total_resultados=3069,
            numero_ap_inicial=1,
            numero_ap_final=3069,
            data_inicial=date(1996, 3, 11),
            data_final=date(2026, 11, 14),
        )
        selecao = SelecaoPadroesRaros(
            Decimal("10"), 3069, "<", (padrao,)
        )

        grupos = _grupos_raros_fotografados(perfil, selecao)

        self.assertEqual(1, len(grupos))
        self.assertEqual("PG_007", grupos[0].grupo_cod)
        self.assertEqual(("PD_011",), grupos[0].padroes_excludentes)


if __name__ == "__main__":
    unittest.main()
