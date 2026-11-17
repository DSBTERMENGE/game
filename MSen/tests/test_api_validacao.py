import unittest

from msen.api import criar_app
from msen.api.validacao import _hipotese_diagnostica
from msen.services import ReferenciaAprovada


class TestApiValidacao(unittest.TestCase):
    def setUp(self):
        self.recebidos = []

        def consultar(filtros):
            self.recebidos.append(filtros)
            return {
                "estado_global": {"atualizado": False},
                "resumo": {"total": 3800}, "avaliacoes": [],
            }

        self.app = criar_app({
            "TESTING": True, "CONSULTAR_VALIDACAO": consultar,
            "CONSULTAR_RELATORIO_VALIDACAO": lambda: {
                "fechamento": {"exigidas": 3800, "valido": True},
                "criterios": [], "divergencias": [],
            },
            "EXPORTAR_VALIDACAO": lambda: {
                "formato": "msen-validacao-auditoria", "versao_esquema": 1,
                "gerado_em": "2026-10-30T00:00:00+00:00",
                "conjunto_referencias": {"algoritmo": "sha256", "identificador": "abc", "quantidade": 0},
                "registros": [],
            },
            "APROVAR_REFERENCIA_CATEGORICA": lambda dados: ReferenciaAprovada(
                dados["id_resultado"], dados["id_criterio"], "PAD_PG_004",
                "CATEGORIA_IDENTIFICADA", None, None, dados["origem"],
                dados["revisor"], dados["categoria_esperada"],
            ),
        })
        self.cliente = self.app.test_client()

    def test_consulta_normaliza_filtros_e_paginacao(self):
        resposta = self.cliente.get(
            "/api/validacao/quadro?categoria=PADRAO&criterio=PAD_PD_003"
            "&grupo=PG_001&subgrupo=PD_003&situacao=S&pagina=2&limite=25"
        )
        self.assertEqual(200, resposta.status_code)
        self.assertEqual(3800, resposta.json["resumo"]["total"])
        self.assertEqual({
            "categoria": "PADRAO", "criterio": "PAD_PD_003",
            "grupo": "PG_001", "subgrupo": "PD_003", "situacao": "S",
            "pagina": 2, "limite": 25,
        }, self.recebidos[0])

    def test_padrao_paginacao_e_filtros_vazios(self):
        resposta = self.cliente.get("/api/validacao/quadro")
        self.assertEqual(200, resposta.status_code)
        self.assertEqual(1, self.recebidos[0]["pagina"])
        self.assertEqual(50, self.recebidos[0]["limite"])
        self.assertIsNone(self.recebidos[0]["categoria"])

    def test_rejeita_categoria_situacao_e_paginacao_invalidas(self):
        for consulta in (
            "categoria=OUTRA", "situacao=X", "pagina=0", "limite=101", "pagina=abc",
        ):
            with self.subTest(consulta=consulta):
                resposta = self.cliente.get(f"/api/validacao/quadro?{consulta}")
                self.assertEqual(400, resposta.status_code)
                self.assertEqual("PARAMETRO_INVALIDO", resposta.json["erro"]["codigo"])

    def test_relatorio_fecha_total_exigido(self):
        resposta = self.cliente.get("/api/validacao/relatorio")
        self.assertEqual(200, resposta.status_code)
        self.assertEqual(3800, resposta.json["fechamento"]["exigidas"])
        self.assertTrue(resposta.json["fechamento"]["valido"])

    def test_hipotese_prioriza_assinatura_estado_padrao_e_valor(self):
        base = dict(
            assinatura_atual="a", assinatura_executada="a",
            estado_esperado="VALOR_IDENTIFICADO", estado_calculado="VALOR_IDENTIFICADO",
            valor_esperado="1", valor_calculado="1",
            subgrupo_esperado=None, subgrupo_calculado=None,
        )
        self.assertIn("assinatura", _hipotese_diagnostica(**{**base, "assinatura_executada": "b"}))
        self.assertIn("existência", _hipotese_diagnostica(**{**base, "estado_calculado": "SEM_VALOR"}))
        self.assertIn("subgrupo", _hipotese_diagnostica(**{
            **base, "subgrupo_esperado": "PD_001", "subgrupo_calculado": "PD_002",
        }))
        self.assertIn("numérico", _hipotese_diagnostica(**{**base, "valor_calculado": "2"}))

    def test_exporta_json_csv_e_rejeita_formato_desconhecido(self):
        json_resposta = self.cliente.get("/api/validacao/exportacao?formato=json")
        self.assertEqual(200, json_resposta.status_code)
        self.assertIn("validacao-auditoria.json", json_resposta.headers["Content-Disposition"])
        self.assertEqual(1, json_resposta.json["versao_esquema"])
        csv_resposta = self.cliente.get("/api/validacao/exportacao?formato=csv")
        self.assertEqual(200, csv_resposta.status_code)
        self.assertTrue(csv_resposta.data.startswith(b"\xef\xbb\xbf"))
        invalida = self.cliente.get("/api/validacao/exportacao?formato=xlsx")
        self.assertEqual(400, invalida.status_code)
        self.assertEqual("FORMATO_INVALIDO", invalida.json["erro"]["codigo"])

    def test_registra_referencia_categorica(self):
        resposta = self.cliente.post(
            "/api/validacao/referencias/categoricas",
            json={
                "id_resultado": 7,
                "id_criterio": 20,
                "categoria_esperada": "0D0E|1D1E",
                "origem": "HUMANO",
                "revisor": "Revisor",
            },
        )

        self.assertEqual(201, resposta.status_code)
        self.assertEqual("PAD_PG_004", resposta.json["referencia"]["codigo_criterio"])
        self.assertEqual("0D0E|1D1E", resposta.json["referencia"]["categoria"])

    def test_rejeita_corpo_categorico_incompleto_ou_com_campo_extra(self):
        for corpo in (
            {},
            {
                "id_resultado": 7, "id_criterio": 20,
                "categoria_esperada": "0D0E", "origem": "HUMANO",
                "revisor": "R", "campo_extra": True,
            },
        ):
            with self.subTest(corpo=corpo):
                resposta = self.cliente.post(
                    "/api/validacao/referencias/categoricas", json=corpo
                )
                self.assertEqual(400, resposta.status_code)
                self.assertEqual("JSON_INVALIDO", resposta.json["erro"]["codigo"])


if __name__ == "__main__":
    unittest.main()
