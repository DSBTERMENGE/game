import unittest

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

        def executor(limite):
            self.limites.append(limite)
            return RESPOSTA

        self.cliente = criar_app({
            "TESTING": True,
            "GERAR_QUADRO_SCREENER": executor,
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


if __name__ == "__main__":
    unittest.main()
