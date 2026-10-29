import unittest
from decimal import Decimal

from msen.api import criar_app


class ApiScreenerTestCase(unittest.TestCase):
    def setUp(self):
        self.execucoes = []

        def executor(limite):
            self.execucoes.append(limite)
            return {"resumo": {"total_analisado": 5000}, "protecao": {
                "processamento_integral_bloqueado": True,
            }}

        self.cliente = criar_app({
            "TESTING": True,
            "GERAR_QUADRO_SCREENER": executor,
        }).test_client()

    def test_serve_pagina_css_e_javascript_separados(self):
        pagina = self.cliente.get("/screener.html")
        css = self.cliente.get("/css/screener.css")
        javascript = self.cliente.get("/js/screener-extensivel.js")
        self.assertEqual(200, pagina.status_code)
        self.assertIn(b'id="extensivel-niveis"', pagina.data)
        self.assertNotIn(b'Valida\xc3\xa7\xc3\xa3o humana', pagina.data)
        self.assertEqual(200, css.status_code)
        self.assertEqual(200, javascript.status_code)

    def test_interfaces_e_rotas_transitorias_nao_estao_mais_publicadas(self):
        self.assertEqual(404, self.cliente.get("/screener-extensivel.html").status_code)
        self.assertEqual(404, self.cliente.get("/screener-prototipo.html").status_code)
        self.assertEqual(404, self.cliente.get("/js/screener.js").status_code)
        self.assertNotEqual(
            200, self.cliente.post("/api/screener/quadro-extensivel").status_code
        )
        self.assertNotEqual(200, self.cliente.get("/api/screener/quadro").status_code)

    def test_executa_funil_oficial_somente_por_post(self):
        resposta = self.cliente.post("/api/screener/quadro")
        self.assertEqual(200, resposta.status_code)
        self.assertEqual(5000, resposta.get_json()["resumo"]["total_analisado"])
        self.assertTrue(
            resposta.get_json()["protecao"]["processamento_integral_bloqueado"]
        )
        self.assertEqual([None], self.execucoes)
        self.assertNotEqual(
            200, self.cliente.get("/api/screener/quadro").status_code
        )

    def test_recebe_limite_percentual_sem_editar_codigo(self):
        resposta = self.cliente.post(
            "/api/screener/quadro", json={"limite_raridade": "3.25"}
        )
        self.assertEqual(200, resposta.status_code)
        self.assertEqual([Decimal("3.250000")], self.execucoes)

    def test_rejeita_limite_invalido_ou_parametro_desconhecido(self):
        for corpo in ({"limite_raridade": 101}, {"outro": 10}, []):
            with self.subTest(corpo=corpo):
                resposta = self.cliente.post(
                    "/api/screener/quadro", json=corpo
                )
                self.assertEqual(400, resposta.status_code)
        malformada = self.cliente.post(
            "/api/screener/quadro",
            data="{",
            content_type="application/json",
        )
        self.assertEqual(400, malformada.status_code)
        self.assertEqual([], self.execucoes)


if __name__ == "__main__":
    unittest.main()
