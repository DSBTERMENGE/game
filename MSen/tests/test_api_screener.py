import unittest
from decimal import Decimal
from time import sleep

from msen.api import criar_app
from msen.api.screener import GerenciadorExecucoesScreener


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


class GerenciadorExecucoesScreenerTestCase(unittest.TestCase):
    def test_informa_progresso_e_conclui_sem_persistencia(self):
        def operacao(limite, progresso, cancelado):
            self.assertEqual(Decimal("7.500000"), limite)
            self.assertFalse(cancelado())
            progresso("Aplicando filtros", 2500, 10000)
            progresso("Comparando resultados", 10000, 10000)
            return {"resumo": {"total_analisado": 5000}}

        gerenciador = GerenciadorExecucoesScreener(operacao)
        inicial = gerenciador.iniciar(Decimal("7.500000"))
        final = inicial
        for _ in range(100):
            final = gerenciador.obter(inicial["id"])
            if final["estado"] == "CONCLUIDA":
                break
            sleep(0.005)
        self.assertEqual("CONCLUIDA", final["estado"])
        self.assertEqual(100, final["percentual"])
        self.assertEqual(5000, final["resultado"]["resumo"]["total_analisado"])

    def test_cancelamento_interrompe_e_descarta_resultado_parcial(self):
        def operacao(_limite, progresso, cancelado):
            for indice in range(1, 1001):
                if cancelado():
                    raise InterruptedError
                progresso("Aplicando filtros", indice, 1000)
                sleep(0.001)
            return {"indevido": True}

        gerenciador = GerenciadorExecucoesScreener(operacao)
        inicial = gerenciador.iniciar(Decimal("10"))
        sleep(0.01)
        gerenciador.cancelar(inicial["id"])
        final = inicial
        for _ in range(200):
            final = gerenciador.obter(inicial["id"])
            if final["estado"] == "CANCELADA":
                break
            sleep(0.005)
        self.assertEqual("CANCELADA", final["estado"])
        self.assertIsNone(final["resultado"])
        self.assertLess(final["percentual"], 100)


if __name__ == "__main__":
    unittest.main()
