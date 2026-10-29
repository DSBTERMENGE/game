import unittest
from decimal import Decimal

from msen.api import criar_app


RESPOSTA = {
    "total_recebido": 5_000,
    "total_aprovado": 4_409,
    "duracao_segundos": 0.5,
    "linhas": [],
    "validacoes": [],
    "aviso": "experimental",
}


class ApiScreenerTestCase(unittest.TestCase):
    def setUp(self):
        self.limites = []
        self.execucoes_extensiveis = []

        def executor(limite):
            self.limites.append(limite)
            return RESPOSTA

        def executor_extensivel(limite):
            self.execucoes_extensiveis.append(limite)
            return {"resumo": {"total_analisado": 5000}, "protecao": {
                "processamento_integral_bloqueado": True,
            }}

        self.cliente = criar_app({
            "TESTING": True,
            "GERAR_QUADRO_SCREENER": executor,
            "GERAR_QUADRO_SCREENER_EXTENSIVEL": executor_extensivel,
        }).test_client()

    def test_retorna_quadro_sem_acessar_banco(self):
        resposta = self.cliente.get("/api/screener/quadro?limite_validacoes=18")
        self.assertEqual(200, resposta.status_code)
        self.assertEqual(18, self.limites[0])
        self.assertEqual(4_409, resposta.get_json()["total_aprovado"])

    def test_rejeita_limite_nao_inteiro(self):
        resposta = self.cliente.get("/api/screener/quadro?limite_validacoes=x")
        self.assertEqual(400, resposta.status_code)
        self.assertEqual("LIMITE_VALIDACOES_INVALIDO", resposta.get_json()["erro"]["codigo"])

    def test_rejeita_limite_fora_da_faixa(self):
        resposta = self.cliente.get("/api/screener/quadro?limite_validacoes=201")
        self.assertEqual(400, resposta.status_code)
        self.assertEqual([], self.limites)

    def test_serve_pagina_css_e_javascript_separados(self):
        pagina = self.cliente.get("/screener.html")
        css = self.cliente.get("/css/screener.css")
        javascript = self.cliente.get("/js/screener.js")
        self.assertEqual(200, pagina.status_code)
        self.assertIn(b'id="corpo-quadro-screener"', pagina.data)
        self.assertEqual(200, css.status_code)
        self.assertEqual(200, javascript.status_code)

    def test_executa_novo_funil_somente_por_post(self):
        resposta = self.cliente.post("/api/screener/quadro-extensivel")
        self.assertEqual(200, resposta.status_code)
        self.assertEqual(5000, resposta.get_json()["resumo"]["total_analisado"])
        self.assertTrue(
            resposta.get_json()["protecao"]["processamento_integral_bloqueado"]
        )
        self.assertEqual([None], self.execucoes_extensiveis)
        self.assertNotEqual(
            200, self.cliente.get("/api/screener/quadro-extensivel").status_code
        )

    def test_recebe_limite_percentual_sem_editar_codigo(self):
        resposta = self.cliente.post(
            "/api/screener/quadro-extensivel", json={"limite_raridade": "3.25"}
        )
        self.assertEqual(200, resposta.status_code)
        self.assertEqual([Decimal("3.250000")], self.execucoes_extensiveis)

    def test_rejeita_limite_invalido_ou_parametro_desconhecido(self):
        for corpo in ({"limite_raridade": 101}, {"outro": 10}, []):
            with self.subTest(corpo=corpo):
                resposta = self.cliente.post(
                    "/api/screener/quadro-extensivel", json=corpo
                )
                self.assertEqual(400, resposta.status_code)
        malformada = self.cliente.post(
            "/api/screener/quadro-extensivel",
            data="{",
            content_type="application/json",
        )
        self.assertEqual(400, malformada.status_code)
        self.assertEqual([], self.execucoes_extensiveis)


if __name__ == "__main__":
    unittest.main()
