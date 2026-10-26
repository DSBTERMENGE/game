import unittest

from flask import Flask

from msen.api import criar_app


class ConfiguracaoApiTestCase(unittest.TestCase):
    def test_fabrica_retorna_aplicacao_flask(self):
        self.assertIsInstance(criar_app(), Flask)

    def test_fabrica_aceita_configuracao_de_teste(self):
        app = criar_app({"TESTING": True, "CHAVE_TESTE": "valor"})
        self.assertTrue(app.testing)
        self.assertEqual("valor", app.config["CHAVE_TESTE"])

    def test_fabrica_cria_instancias_independentes(self):
        primeira = criar_app({"CHAVE_TESTE": "primeira"})
        segunda = criar_app({"CHAVE_TESTE": "segunda"})
        self.assertIsNot(primeira, segunda)
        self.assertNotEqual(primeira.config["CHAVE_TESTE"], segunda.config["CHAVE_TESTE"])

    def test_endpoint_de_saude_responde_json(self):
        cliente = criar_app({"TESTING": True}).test_client()
        resposta = cliente.get("/api/saude")
        self.assertEqual(200, resposta.status_code)
        self.assertEqual({"aplicacao": "MSen", "status": "ok"}, resposta.get_json())

    def test_criar_aplicacao_nao_exige_conexao_com_banco(self):
        app = criar_app({"TESTING": True})
        self.assertTrue(any(regra.rule == "/api/resultados" for regra in app.url_map.iter_rules()))

    def test_entrada_wsgi_expoe_aplicacao_sem_iniciar_servidor(self):
        from wsgi import application

        self.assertIsInstance(application, Flask)


if __name__ == "__main__":
    unittest.main()
