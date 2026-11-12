"""Testes do contrato HTTP da Seleção de dezenas."""

from threading import Event
import time
import unittest

import psycopg

from msen.api import criar_app
from msen.api.selecao_dezenas import GerenciadorBacktests
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
        self.previsoes = []
        self.persistencias = []
        self.previas_backtest = []
        self.gerenciador_backtest = GerenciadorBacktests(
            lambda solicitacao, progresso, cancelado: (
                progresso("Calculando relatório do Backtest", 3, 3) or {
                    "id_configuracao_selecao": solicitacao[
                        "id_configuracao_selecao"
                    ],
                    "pontos": [{
                        "concurso": solicitacao["concurso_inicial"],
                        "quantidade_dezenas": 12,
                        "quantidade_acertos": 3,
                    }],
                    "persistido": False,
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
            "PREPARAR_BACKTEST_SELECAO": (
                lambda identificador, inicio, final: (
                    self.previas_backtest.append(
                        (identificador, inicio, final)
                    ) or {
                        "id_configuracao_selecao": identificador,
                        "periodo": {
                            "concurso_inicial": inicio,
                            "concurso_final": 3069 if final is None else final,
                            "quantidade_concursos": (
                                (3069 if final is None else final) - inicio + 1
                            ),
                        },
                        "persistira_resultados": False,
                    }
                )
            ),
            "GERENCIADOR_BACKTEST_SELECAO": (
                self.gerenciador_backtest
            ),
            "DETALHAR_PREVISAO_SELECAO": lambda identificador: [
                {"id": identificador, "concurso": 500}
            ],
            "ATUALIZAR_PREVISOES_SELECAO": lambda identificador: (
                self.previsoes.append(identificador) or {"concurso_corte": 3069}
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

    def test_rejeita_campo_legado_de_horizonte(self) -> None:
        resposta = self.cliente.post("/api/selecao-dezenas/configuracoes", json={
            "configuracao": configuracao_json() | {"horizonte_concursos": 1},
        })

        self.assertEqual(400, resposta.status_code)

    def test_previa_inicia_e_consulta_backtest(self) -> None:
        corpo = {
            "id_configuracao_selecao": 7,
            "concurso_inicial": 500,
        }
        previa = self.cliente.post(
            "/api/selecao-dezenas/backtests/previa", json=corpo
        )
        inicio = self.cliente.post(
            "/api/selecao-dezenas/backtests", json=corpo
        )

        self.assertEqual(200, previa.status_code)
        self.assertFalse(previa.json["persistira_resultados"])
        self.assertEqual((7, 500, None), self.previas_backtest[0])
        self.assertEqual(202, inicio.status_code)
        final = aguardar(
            self.gerenciador_backtest, inicio.json["id"], {"CONCLUIDA"}
        )
        consulta = self.cliente.get(
            f"/api/selecao-dezenas/backtests/{inicio.json['id']}"
        )
        self.assertEqual(100, final["percentual"])
        self.assertFalse(consulta.json["resultado"]["persistido"])
        self.assertEqual(500, consulta.json["resultado"]["pontos"][0]["concurso"])

    def test_previa_backtest_adota_ultimo_concurso(self) -> None:
        previa = self.cliente.post(
            "/api/selecao-dezenas/backtests/previa",
            json={
                "id_configuracao_selecao": 7,
                "concurso_inicial": 500,
            },
        )

        self.assertEqual(200, previa.status_code)
        self.assertEqual((7, 500, None), self.previas_backtest[0])
        self.assertEqual(3069, previa.json["periodo"]["concurso_final"])
        self.assertEqual(2570, previa.json["periodo"]["quantidade_concursos"])

    def test_backtest_exige_id_salvo_e_periodo_valido(self) -> None:
        for corpo in (
            {
                "configuracao": configuracao_json(),
                "concurso_inicial": 500,
            },
            {
                "id_configuracao_selecao": 0,
                "concurso_inicial": 500,
            },
            {
                "id_configuracao_selecao": 1,
                "concurso_inicial": 499,
            },
            {
                "id_configuracao_selecao": 1,
                "concurso_inicial": 500,
                "concurso_final": 500,
            },
        ):
            with self.subTest(corpo=corpo):
                resposta = self.cliente.post(
                    "/api/selecao-dezenas/backtests/previa",
                    json=corpo,
                )
                self.assertEqual(400, resposta.status_code)

    def test_nova_execucao_temporaria_descarta_relatorio_anterior(self) -> None:
        corpo = {
            "id_configuracao_selecao": 1,
            "concurso_inicial": 500,
        }
        primeira = self.cliente.post(
            "/api/selecao-dezenas/backtests", json=corpo
        )
        aguardar(self.gerenciador_backtest, primeira.json["id"], {"CONCLUIDA"})
        segunda = self.cliente.post(
            "/api/selecao-dezenas/backtests", json=corpo
        )
        aguardar(self.gerenciador_backtest, segunda.json["id"], {"CONCLUIDA"})

        antiga = self.cliente.get(
            f"/api/selecao-dezenas/backtests/{primeira.json['id']}"
        )
        self.assertEqual(404, antiga.status_code)
        self.assertEqual(
            "BACKTEST_NAO_ENCONTRADO", antiga.json["erro"]["codigo"]
        )

    def test_descarta_relatorio_backtest_concluido(self) -> None:
        corpo = {
            "id_configuracao_selecao": 1,
            "concurso_inicial": 500,
        }
        inicio = self.cliente.post(
            "/api/selecao-dezenas/backtests", json=corpo
        )
        aguardar(self.gerenciador_backtest, inicio.json["id"], {"CONCLUIDA"})

        descarte = self.cliente.delete(
            f"/api/selecao-dezenas/backtests/{inicio.json['id']}"
        )
        consulta = self.cliente.get(
            f"/api/selecao-dezenas/backtests/{inicio.json['id']}"
        )
        self.assertEqual(204, descarte.status_code)
        self.assertEqual(404, consulta.status_code)

    def test_atualiza_e_consulta_previsao_futura(self) -> None:
        atualizada = self.cliente.post("/api/selecao-dezenas/previsoes", json={
            "id_configuracao_selecao": 7
        })
        detalhes = self.cliente.get(
            "/api/selecao-dezenas/previsoes/8/detalhes"
        )
        self.assertEqual(3069, atualizada.json["concurso_corte"])
        self.assertEqual([7], self.previsoes)
        self.assertEqual(8, detalhes.json["detalhes"][0]["id"])

    def test_previsao_exige_identificador_de_configuracao_salva(self) -> None:
        for corpo in (
            {"configuracao": configuracao_json()},
            {"id_configuracao_selecao": 0},
            {"id_configuracao_selecao": "1"},
        ):
            with self.subTest(corpo=corpo):
                resposta = self.cliente.post(
                    "/api/selecao-dezenas/previsoes", json=corpo
                )
                self.assertEqual(400, resposta.status_code)

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


class GerenciadorBacktestsTestCase(unittest.TestCase):
    def test_cancelamento_e_bloqueio_de_execucao_dupla(self) -> None:
        iniciou = Event()
        def operacao(_solicitacao, progresso, cancelado):
            progresso("Executando", 1, 2)
            iniciou.set()
            while not cancelado():
                time.sleep(0.001)
            return {"estado": "CANCELADA"}
        gerenciador = GerenciadorBacktests(operacao)
        primeira = gerenciador.iniciar({})
        self.assertTrue(iniciou.wait(1))
        with self.assertRaises(Exception):
            gerenciador.iniciar({})
        gerenciador.cancelar(primeira["id"])
        final = aguardar(gerenciador, primeira["id"], {"CANCELADA"})
        self.assertEqual("CANCELADA", final["estado"])


if __name__ == "__main__":
    unittest.main()
