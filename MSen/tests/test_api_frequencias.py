"""Testes dos contratos HTTP do módulo de frequências."""

from threading import Event
import time
import unittest
import psycopg

from msen.api import criar_app
from msen.api.frequencias import (
    GerenciadorExecucoesFrequencia,
    avaliar_assertividade_frequencia,
)
from msen.services import OperacaoFrequenciaCancelada, configuracao_frequencia_inicial


def configuracao_json():
    return configuracao_frequencia_inicial().conteudo_assinavel()


def aguardar(gerenciador, identificador, estados, limite=1):
    fim = time.monotonic() + limite
    while time.monotonic() < fim:
        dados = gerenciador.obter(identificador)
        if dados["estado"] in estados:
            return dados
        time.sleep(0.005)
    raise AssertionError("A execução não atingiu o estado esperado.")


class ApiFrequenciasTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.series = []
        self.previas = []
        self.gerenciador = GerenciadorExecucoesFrequencia(
            lambda solicitacao, progresso, cancelado: {
                "salvar": solicitacao["salvar_dados"]
            }
        )
        self.app = criar_app({
            "TESTING": True,
            "CONSULTAR_ESTADO_FREQUENCIA": lambda: {
                "resultados": {"quantidade": 3069}, "geracao_ativa": None,
            },
            "CONSULTAR_FOTOGRAFIA_FREQUENCIA": lambda tipo: {
                "tipo_evento": tipo, "dezenas": [{"dezena": 1}],
            },
            "CONSULTAR_SERIE_FREQUENCIA": lambda filtros: (
                self.series.append(filtros) or {"pontos": [], "total": 0}
            ),
            "PREPARAR_FREQUENCIA": lambda config, salvar: (
                self.previas.append((config, salvar)) or {"modo": "PRIMEIRA_CARGA"}
            ),
            "GERENCIADOR_FREQUENCIA": self.gerenciador,
        })
        self.cliente = self.app.test_client()

    def test_estado_e_fotografia_atual(self) -> None:
        estado = self.cliente.get("/api/frequencias/estado")
        fotografia = self.cliente.get("/api/frequencias/fotografia-atual")
        self.assertEqual(3069, estado.json["resultados"]["quantidade"])
        self.assertEqual("SIMPLES", fotografia.json["tipo_evento"])

    def test_fotografia_seleciona_tipo_e_rejeita_tipo_invalido(self) -> None:
        dois = self.cliente.get("/api/frequencias/fotografia-atual?tipo_evento=2vs")
        invalido = self.cliente.get(
            "/api/frequencias/fotografia-atual?tipo_evento=OUTRO"
        )
        self.assertEqual("2VS", dois.json["tipo_evento"])
        self.assertEqual(400, invalido.status_code)
        self.assertEqual("PARAMETRO_INVALIDO", invalido.json["erro"]["codigo"])

    def test_serie_normaliza_uma_dezena_tipo_e_periodo(self) -> None:
        resposta = self.cliente.get(
            "/api/frequencias/serie?dezena=10&tipo_evento=2vs"
            "&concurso_inicial=500&concurso_final=900"
        )
        self.assertEqual(200, resposta.status_code)
        self.assertEqual({
            "dezena": 10, "tipo_evento": "2VS", "concurso_inicial": 500,
            "concurso_final": 900,
        }, self.series[0])

    def test_rejeita_serie_ambigua(self) -> None:
        for consulta in (
            "", "dezena=0&tipo_evento=SIMPLES", "dezena=1&tipo_evento=OUTRO",
            "dezena=x&tipo_evento=2VS",
        ):
            with self.subTest(consulta=consulta):
                resposta = self.cliente.get(f"/api/frequencias/serie?{consulta}")
                self.assertEqual(400, resposta.status_code)
                self.assertEqual("PARAMETRO_INVALIDO", resposta.json["erro"]["codigo"])

    def test_previa_valida_configuracao_e_tick(self) -> None:
        resposta = self.cliente.post("/api/frequencias/previa", json={
            "configuracao": configuracao_json(), "salvar_dados": False,
        })
        self.assertEqual(200, resposta.status_code)
        self.assertEqual("PRIMEIRA_CARGA", resposta.json["modo"])
        self.assertFalse(self.previas[0][1])
        self.assertEqual(500, self.previas[0][0].tamanho_inicial)

    def test_rejeita_configuracao_incompleta_e_campos_desconhecidos(self) -> None:
        for corpo in (
            {"configuracao": {}},
            {"configuracao": configuracao_json(), "desconhecido": True},
            {"configuracao": configuracao_json(), "salvar_dados": "sim"},
        ):
            with self.subTest(corpo=corpo):
                resposta = self.cliente.post("/api/frequencias/previa", json=corpo)
                self.assertEqual(400, resposta.status_code)

    def test_gravacao_exige_confirmacao_antes_de_criar_tarefa(self) -> None:
        resposta = self.cliente.post("/api/frequencias/execucoes", json={
            "configuracao": configuracao_json(), "salvar_dados": True,
            "confirmacao_gravacao": False,
        })
        self.assertEqual(400, resposta.status_code)
        self.assertEqual("CONFIRMACAO_OBRIGATORIA", resposta.json["erro"]["codigo"])

    def test_inicia_e_consulta_simulacao(self) -> None:
        inicio = self.cliente.post("/api/frequencias/execucoes", json={
            "configuracao": configuracao_json(), "salvar_dados": False,
        })
        self.assertEqual(202, inicio.status_code)
        final = aguardar(self.gerenciador, inicio.json["id"], {"CONCLUIDA"})
        self.assertEqual(100, final["percentual"])
        consulta = self.cliente.get(f"/api/frequencias/execucoes/{inicio.json['id']}")
        self.assertEqual(200, consulta.status_code)
        self.assertFalse(consulta.json["resultado"]["salvar"])

    def test_id_inexistente(self) -> None:
        consulta = self.cliente.get("/api/frequencias/execucoes/inexistente")
        cancelamento = self.cliente.post(
            "/api/frequencias/execucoes/inexistente/cancelamento"
        )
        self.assertEqual(404, consulta.status_code)
        self.assertEqual(404, cancelamento.status_code)

    def test_indisponibilidade_do_banco_e_controlada(self) -> None:
        def indisponivel(*_args):
            raise psycopg.OperationalError("indisponível")
        app = criar_app({
            "TESTING": True,
            "CONSULTAR_ESTADO_FREQUENCIA": indisponivel,
            "PREPARAR_FREQUENCIA": indisponivel,
        })
        cliente = app.test_client()
        estado = cliente.get("/api/frequencias/estado")
        previa = cliente.post("/api/frequencias/previa", json={
            "configuracao": configuracao_json(), "salvar_dados": False,
        })
        self.assertEqual(503, estado.status_code)
        self.assertEqual(503, previa.status_code)
        self.assertEqual("BANCO_INDISPONIVEL", estado.json["erro"]["codigo"])


class GerenciadorFrequenciasTestCase(unittest.TestCase):
    def test_progresso_e_resultado(self) -> None:
        def operacao(_solicitacao, progresso, _cancelado):
            progresso("Calculando", 1, 2)
            progresso("Gravando", 2, 2)
            return {"linhas": 180}
        gerenciador = GerenciadorExecucoesFrequencia(operacao)
        inicio = gerenciador.iniciar({})
        final = aguardar(gerenciador, inicio["id"], {"CONCLUIDA"})
        self.assertEqual({"linhas": 180}, final["resultado"])
        self.assertEqual(100, final["percentual"])

    def test_execucao_dupla_e_cancelamento(self) -> None:
        iniciou = Event()
        def operacao(_solicitacao, progresso, cancelado):
            progresso("Executando", 1, 2)
            iniciou.set()
            while not cancelado():
                time.sleep(0.001)
            raise OperacaoFrequenciaCancelada()
        gerenciador = GerenciadorExecucoesFrequencia(operacao)
        primeira = gerenciador.iniciar({})
        self.assertTrue(iniciou.wait(1))
        app = criar_app({"TESTING": True, "GERENCIADOR_FREQUENCIA": gerenciador})
        cliente = app.test_client()
        dupla = cliente.post("/api/frequencias/execucoes", json={
            "configuracao": configuracao_json(), "salvar_dados": False,
        })
        self.assertEqual(409, dupla.status_code)
        cancelar = cliente.post(
            f"/api/frequencias/execucoes/{primeira['id']}/cancelamento"
        )
        self.assertEqual(202, cancelar.status_code)
        final = aguardar(gerenciador, primeira["id"], {"CANCELADA"})
        self.assertEqual("CANCELADA", final["estado"])


class AssertividadeFrequenciasTestCase(unittest.TestCase):
    def test_acerto_erro_percentual_e_censura(self) -> None:
        pontos = [
            {"numero_do_concurso": 80, "previsao_central": "90",
             "concurso_limite_inferior": 85, "concurso_limite_superior": 95},
            {"numero_do_concurso": 100, "previsao_central": "112",
             "concurso_limite_inferior": 105, "concurso_limite_superior": 115},
            {"numero_do_concurso": 110, "previsao_central": "120",
             "concurso_limite_inferior": 115, "concurso_limite_superior": 125},
            {"numero_do_concurso": 140, "previsao_central": "150",
             "concurso_limite_inferior": 145, "concurso_limite_superior": 155},
        ]
        resultado = avaliar_assertividade_frequencia(pontos, [90, 110, 140])
        self.assertEqual((2, 1, 1, 2), (
            resultado["avaliaveis"], resultado["acertos"],
            resultado["erros"], resultado["censurados"],
        ))
        self.assertEqual("50", resultado["percentual_acerto"])
        self.assertEqual("10", resultado["avaliacoes"][1]["erro_percentual"])
        self.assertEqual("ERRO_ACIMA", resultado["avaliacoes"][2]["estado"])
        self.assertEqual("66.66666666666666666666666667",
                         resultado["avaliacoes"][2]["erro_percentual"])

    def test_limites_sao_inclusivos(self) -> None:
        pontos = [{
            "numero_do_concurso": 10, "previsao_central": "20",
            "concurso_limite_inferior": 20, "concurso_limite_superior": 25,
        }]
        resultado = avaliar_assertividade_frequencia(pontos, [5, 20])
        self.assertEqual("ACERTO", resultado["avaliacoes"][0]["estado"])


if __name__ == "__main__":
    unittest.main()
