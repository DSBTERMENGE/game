import time
import unittest
from threading import Event

from msen.api import criar_app
from msen.api.execucoes_validacao import GerenciadorExecucoesValidacao


def _aguardar(gerenciador, identificador, estados, limite=1.0):
    fim = time.monotonic() + limite
    while time.monotonic() < fim:
        dados = gerenciador.obter(identificador)
        if dados["estado"] in estados:
            return dados
        time.sleep(0.005)
    raise AssertionError("A execução não alcançou o estado esperado.")


class TestGerenciadorExecucoesValidacao(unittest.TestCase):
    def test_sucesso_publica_progresso_real_e_resultado(self):
        def operacao(progresso):
            progresso("Sincronizando", 1, 2)
            progresso("Comparando", 2, 2)
            return {"aprovadas": 3800}

        gerenciador = GerenciadorExecucoesValidacao(operacao)
        iniciada = gerenciador.iniciar()
        concluida = _aguardar(gerenciador, iniciada["id"], {"CONCLUIDA"})
        self.assertEqual(100, concluida["percentual"])
        self.assertEqual({"aprovadas": 3800}, concluida["resultado"])
        self.assertIsNone(concluida["erro"])

    def test_falha_fica_consultavel(self):
        def operacao(_progresso):
            raise RuntimeError("falha controlada")

        gerenciador = GerenciadorExecucoesValidacao(operacao)
        iniciada = gerenciador.iniciar()
        falhou = _aguardar(gerenciador, iniciada["id"], {"FALHOU"})
        self.assertEqual("RuntimeError", falhou["erro"]["tipo"])
        self.assertEqual("falha controlada", falhou["erro"]["mensagem"])

    def test_impede_execucao_dupla(self):
        liberar = Event()

        def operacao(progresso):
            progresso("Em curso", 1, 2)
            liberar.wait(1)
            progresso("Fim", 2, 2)
            return {}

        gerenciador = GerenciadorExecucoesValidacao(operacao)
        primeira = gerenciador.iniciar()
        _aguardar(gerenciador, primeira["id"], {"EXECUTANDO"})
        app = criar_app({"TESTING": True, "GERENCIADOR_VALIDACAO": gerenciador})
        resposta = app.test_client().post("/api/validacao/execucoes")
        self.assertEqual(409, resposta.status_code)
        self.assertEqual("EXECUCAO_EM_ANDAMENTO", resposta.json["erro"]["codigo"])
        liberar.set()
        _aguardar(gerenciador, primeira["id"], {"CONCLUIDA"})

    def test_rotas_iniciam_consultam_e_rejeitam_id_ausente(self):
        gerenciador = GerenciadorExecucoesValidacao(lambda progresso: {})
        app = criar_app({"TESTING": True, "GERENCIADOR_VALIDACAO": gerenciador})
        cliente = app.test_client()
        inicio = cliente.post("/api/validacao/execucoes")
        self.assertEqual(202, inicio.status_code)
        identificador = inicio.json["id"]
        consulta = cliente.get(f"/api/validacao/execucoes/{identificador}")
        self.assertEqual(200, consulta.status_code)
        ausente = cliente.get("/api/validacao/execucoes/inexistente")
        self.assertEqual(404, ausente.status_code)


if __name__ == "__main__":
    unittest.main()
