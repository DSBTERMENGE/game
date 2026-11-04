"""Testes do contrato HTTP da Seleção de dezenas."""

from threading import Event
import time
import unittest

import psycopg

from msen.api import criar_app
from msen.api.selecao_dezenas import GerenciadorBacktestsSelecao
from msen.services import configuracao_selecao_inicial


def configuracao_json():
    return configuracao_selecao_inicial().conteudo_assinavel()


def aguardar(gerenciador, identificador, estados, limite=1):
    fim = time.monotonic() + limite
    while time.monotonic() < fim:
        dados = gerenciador.obter(identificador)
        if dados["estado"] in estados:
            return dados
        time.sleep(0.005)
    raise AssertionError("A execução não atingiu o estado esperado.")


class ApiSelecaoDezenasTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.salvas = []
        self.previas = []
        self.comparacoes = []
        self.previsoes = []
        self.persistencias = []
        self.gerenciador = GerenciadorBacktestsSelecao(
            lambda solicitacao, progresso, cancelado: (
                progresso("Avaliando", 2, 2) or {
                    "inicio": solicitacao["concurso_inicial"],
                    "cancelado": cancelado(),
                }
            )
        )
        self.app = criar_app({
            "TESTING": True,
            "LISTAR_CONFIGURACOES_SELECAO": lambda: [{"id_configuracao_selecao": 1}],
            "SALVAR_CONFIGURACAO_SELECAO": lambda config: (
                self.salvas.append(config) or {"id_configuracao_selecao": 1}
            ),
            "PREPARAR_PESQUISA_SELECAO": lambda config, inicio, final: (
                self.previas.append((config, inicio, final)) or {"quantidade_alvos": 10}
            ),
            "GERENCIADOR_BACKTEST_SELECAO": self.gerenciador,
            "RESUMIR_BACKTEST_SELECAO": lambda identificador: {
                "id_execucao_selecao": identificador, "avaliados": 100
            },
            "DETALHAR_BACKTEST_SELECAO": lambda identificador: [
                {"id": identificador, "concurso": 500}
            ],
            "COMPARAR_BACKTESTS_SELECAO": lambda ids: (
                self.comparacoes.append(ids) or {"comparavel": True}
            ),
            "ATUALIZAR_PREVISOES_SELECAO": lambda config: (
                self.previsoes.append(config) or {"concurso_corte": 3069}
            ),
            "PREVIA_JOGOS_SELECAO": lambda alvo: {
                "id_alvo": alvo, "quantidade_combinacoes": 7
            },
            "PERSISTIR_JOGOS_SELECAO": lambda alvo, autorizar, confirmar: (
                self.persistencias.append((alvo, autorizar, confirmar))
                or {"id_lote_jogos": 4}
            ),
        })
        self.cliente = self.app.test_client()

    def test_lista_e_cria_configuracao(self) -> None:
        lista = self.cliente.get("/api/selecao-dezenas/configuracoes")
        criada = self.cliente.post("/api/selecao-dezenas/configuracoes", json={
            "configuracao": configuracao_json()
        })
        self.assertEqual(200, lista.status_code)
        self.assertEqual(1, lista.json["configuracoes"][0]["id_configuracao_selecao"])
        self.assertEqual(201, criada.status_code)
        self.assertEqual("MAX", self.salvas[0].modo_quantidade)

    def test_previa_normaliza_periodo_e_configuracao(self) -> None:
        resposta = self.cliente.post("/api/selecao-dezenas/previa", json={
            "configuracao": configuracao_json(),
            "concurso_inicial": 500, "concurso_final": 700,
        })
        self.assertEqual(200, resposta.status_code)
        self.assertEqual(10, resposta.json["quantidade_alvos"])
        self.assertEqual((500, 700), self.previas[0][1:])

    def test_rejeita_configuracao_incompleta_e_campo_desconhecido(self) -> None:
        for corpo in (
            {"configuracao": {}},
            {"configuracao": configuracao_json(), "intruso": True},
            {"configuracao": configuracao_json(), "concurso_inicial": 499},
        ):
            with self.subTest(corpo=corpo):
                resposta = self.cliente.post("/api/selecao-dezenas/previa", json=corpo)
                self.assertEqual(400, resposta.status_code)

    def test_inicia_e_consulta_backtest_assincrono(self) -> None:
        inicio = self.cliente.post("/api/selecao-dezenas/backtests", json={
            "configuracao": configuracao_json(), "concurso_inicial": 500,
        })
        self.assertEqual(202, inicio.status_code)
        final = aguardar(self.gerenciador, inicio.json["id"], {"CONCLUIDA"})
        self.assertEqual(100, final["percentual"])
        consulta = self.cliente.get(
            f"/api/selecao-dezenas/execucoes/{inicio.json['id']}"
        )
        self.assertEqual(500, consulta.json["resultado"]["inicio"])

    def test_execucao_inexistente(self) -> None:
        consulta = self.cliente.get("/api/selecao-dezenas/execucoes/inexistente")
        cancelar = self.cliente.post(
            "/api/selecao-dezenas/execucoes/inexistente/cancelamento"
        )
        self.assertEqual(404, consulta.status_code)
        self.assertEqual(404, cancelar.status_code)

    def test_resumo_detalhe_e_comparacao(self) -> None:
        resumo = self.cliente.get("/api/selecao-dezenas/backtests/3/resumo")
        detalhe = self.cliente.get("/api/selecao-dezenas/backtests/3/detalhes")
        comparacao = self.cliente.post(
            "/api/selecao-dezenas/backtests/comparacao",
            json={"ids_execucoes": [3, 4]},
        )
        self.assertEqual(100, resumo.json["avaliados"])
        self.assertEqual(500, detalhe.json["detalhes"][0]["concurso"])
        self.assertTrue(comparacao.json["comparavel"])
        self.assertEqual((3, 4), self.comparacoes[0])

    def test_comparacao_rejeita_identificadores_invalidos(self) -> None:
        for ids in (None, [1, "2"], [True, 2]):
            resposta = self.cliente.post(
                "/api/selecao-dezenas/backtests/comparacao",
                json={"ids_execucoes": ids},
            )
            self.assertEqual(400, resposta.status_code)

    def test_atualiza_e_consulta_previsao_futura(self) -> None:
        atualizada = self.cliente.post("/api/selecao-dezenas/previsoes", json={
            "configuracao": configuracao_json()
        })
        detalhes = self.cliente.get(
            "/api/selecao-dezenas/previsoes/8/detalhes"
        )
        self.assertEqual(3069, atualizada.json["concurso_corte"])
        self.assertEqual(8, detalhes.json["detalhes"][0]["id"])

    def test_previa_e_persistencia_de_jogos(self) -> None:
        previa = self.cliente.get(
            "/api/selecao-dezenas/alvos/9/jogos/previa"
        )
        gravacao = self.cliente.post(
            "/api/selecao-dezenas/alvos/9/jogos",
            json={
                "autorizar_persistencia": True,
                "confirmar_volume_elevado": False,
            },
        )
        self.assertEqual(7, previa.json["quantidade_combinacoes"])
        self.assertEqual(201, gravacao.status_code)
        self.assertEqual((9, True, False), self.persistencias[0])

    def test_rejeita_flags_de_persistencia_invalidas(self) -> None:
        resposta = self.cliente.post(
            "/api/selecao-dezenas/alvos/9/jogos",
            json={"autorizar_persistencia": "sim"},
        )
        self.assertEqual(400, resposta.status_code)

    def test_indisponibilidade_do_banco_nao_expoe_detalhes(self) -> None:
        def indisponivel(*_args):
            raise psycopg.OperationalError("senha secreta e host interno")
        app = criar_app({
            "TESTING": True,
            "LISTAR_CONFIGURACOES_SELECAO": indisponivel,
        })
        resposta = app.test_client().get("/api/selecao-dezenas/configuracoes")
        self.assertEqual(503, resposta.status_code)
        self.assertEqual("BANCO_INDISPONIVEL", resposta.json["erro"]["codigo"])
        self.assertNotIn("senha", resposta.get_data(as_text=True))


class GerenciadorBacktestsSelecaoTestCase(unittest.TestCase):
    def test_cancelamento_e_bloqueio_de_execucao_dupla(self) -> None:
        iniciou = Event()
        def operacao(_solicitacao, progresso, cancelado):
            progresso("Executando", 1, 2)
            iniciou.set()
            while not cancelado():
                time.sleep(0.001)
            return {"estado": "CANCELADA"}
        gerenciador = GerenciadorBacktestsSelecao(operacao)
        primeira = gerenciador.iniciar({})
        self.assertTrue(iniciou.wait(1))
        with self.assertRaises(Exception):
            gerenciador.iniciar({})
        gerenciador.cancelar(primeira["id"])
        final = aguardar(gerenciador, primeira["id"], {"CANCELADA"})
        self.assertEqual("CANCELADA", final["estado"])


if __name__ == "__main__":
    unittest.main()
