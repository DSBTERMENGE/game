"""API de leitura do quadro experimental do screener."""

from copy import deepcopy
from datetime import datetime, timezone
from threading import Event, Lock, Thread
from time import monotonic
from typing import Callable
from uuid import uuid4

from flask import Blueprint, current_app, jsonify, request

from msen.screener import (
    ErroConfiguracaoScreener,
    validar_limite_raridade,
)


screener_api = Blueprint("screener_api", __name__)


class ExecucaoScreenerEmAndamento(RuntimeError):
    pass


class GerenciadorExecucoesScreener:
    """Mantém tarefas momentâneas do Screener somente na memória do processo."""

    def __init__(self, operacao: Callable | None = None) -> None:
        self._operacao = operacao
        self._trava = Lock()
        self._execucoes: dict[str, dict[str, object]] = {}
        self._cancelamentos: dict[str, Event] = {}
        self._ativa: str | None = None

    def iniciar(self, limite_raridade, operacao: Callable | None = None) -> dict[str, object]:
        executar = operacao or self._operacao
        if executar is None:
            raise RuntimeError("Operação do Screener não configurada.")
        with self._trava:
            if self._ativa is not None and self._execucoes[self._ativa]["estado"] in {
                "AGUARDANDO", "EXECUTANDO", "CANCELAMENTO_SOLICITADO"
            }:
                raise ExecucaoScreenerEmAndamento(self._ativa)
            identificador = str(uuid4())
            agora = datetime.now(timezone.utc)
            self._execucoes[identificador] = {
                "id": identificador, "estado": "AGUARDANDO",
                "etapa": "Aguardando início", "concluido": 0, "total": 10_000,
                "percentual": 0, "duracao_segundos": 0.0,
                "iniciada_em": agora.isoformat(), "terminada_em": None,
                "erro": None, "resultado": None, "_inicio": monotonic(),
            }
            self._cancelamentos[identificador] = Event()
            self._ativa = identificador
        Thread(
            target=self._executar,
            args=(identificador, limite_raridade, executar),
            daemon=True,
        ).start()
        return self.obter(identificador)

    def obter(self, identificador: str) -> dict[str, object]:
        with self._trava:
            if identificador not in self._execucoes:
                raise KeyError(identificador)
            dados = deepcopy(self._execucoes[identificador])
            if dados["estado"] in {"AGUARDANDO", "EXECUTANDO", "CANCELAMENTO_SOLICITADO"}:
                dados["duracao_segundos"] = round(monotonic() - dados["_inicio"], 3)
            dados.pop("_inicio", None)
            return dados

    def cancelar(self, identificador: str) -> dict[str, object]:
        with self._trava:
            if identificador not in self._execucoes:
                raise KeyError(identificador)
            dados = self._execucoes[identificador]
            if dados["estado"] not in {"AGUARDANDO", "EXECUTANDO"}:
                raise RuntimeError("A execução já terminou.")
            self._cancelamentos[identificador].set()
            dados["estado"] = "CANCELAMENTO_SOLICITADO"
            dados["etapa"] = "Aguardando ponto seguro para cancelar"
        return self.obter(identificador)

    def _progresso(self, identificador: str, etapa: str, concluido: int, total: int):
        with self._trava:
            dados = self._execucoes[identificador]
            if dados["estado"] != "CANCELAMENTO_SOLICITADO":
                dados["estado"] = "EXECUTANDO"
                dados["etapa"] = etapa
            dados["concluido"] = concluido
            dados["total"] = total
            dados["percentual"] = round(concluido * 100 / total, 2)

    def _executar(self, identificador: str, limite_raridade, operacao: Callable):
        cancelamento = self._cancelamentos[identificador]
        try:
            resultado = operacao(
                limite_raridade,
                lambda etapa, concluido, total: self._progresso(
                    identificador, etapa, concluido, total
                ),
                cancelamento.is_set,
            )
        except InterruptedError:
            estado, etapa, erro, resultado = (
                "CANCELADA", "Cancelada com segurança; resultados parciais descartados", None, None
            )
        except Exception as falha:
            estado, etapa, resultado = "FALHOU", "Execução interrompida", None
            erro = {"tipo": type(falha).__name__, "mensagem": str(falha)}
        else:
            estado, etapa, erro = "CONCLUIDA", "Teste concluído", None
        with self._trava:
            dados = self._execucoes[identificador]
            dados.update(
                estado=estado, etapa=etapa, erro=erro, resultado=resultado,
                terminada_em=datetime.now(timezone.utc).isoformat(),
                duracao_segundos=round(monotonic() - dados["_inicio"], 3),
            )
            if estado == "CONCLUIDA":
                dados["concluido"] = dados["total"]
                dados["percentual"] = 100
            self._ativa = None


@screener_api.post("/api/screener/quadro")
def obter_quadro_screener():
    """Executa somente a amostra fixa do funil oficial em três níveis."""

    dados = request.get_json(silent=True)
    if dados is None and request.data:
        return jsonify(erro={
            "codigo": "CONFIGURACAO_RARIDADE_INVALIDA",
            "mensagem": "O corpo deve ser um objeto JSON válido.",
        }), 400
    if dados is None:
        dados = {}
    if not isinstance(dados, dict) or set(dados).difference({"limite_raridade"}):
        return jsonify(erro={
            "codigo": "CONFIGURACAO_RARIDADE_INVALIDA",
            "mensagem": "Informe somente o limite percentual de raridade.",
        }), 400
    try:
        limite = (
            None
            if "limite_raridade" not in dados
            else validar_limite_raridade(dados["limite_raridade"])
        )
    except ErroConfiguracaoScreener as erro:
        return jsonify(erro={"codigo": erro.codigo, "mensagem": str(erro)}), 400
    try:
        executor = current_app.config["GERAR_QUADRO_SCREENER"]
        return jsonify(executor(limite))
    except Exception as erro:
        codigo = getattr(erro, "codigo", "ENSAIO_EXTENSIVEL_INDISPONIVEL")
        current_app.logger.exception("Falha no ensaio extensível")
        return jsonify(erro={
            "codigo": codigo,
            "mensagem": "Não foi possível executar a amostra protegida.",
        }), 503


@screener_api.post("/api/screener/execucoes")
def iniciar_execucao_screener():
    dados = request.get_json(silent=True) or {}
    try:
        limite = validar_limite_raridade(dados.get("limite_raridade", "10"))
        gerenciador = current_app.config["GERENCIADOR_SCREENER"]
        return jsonify(gerenciador.iniciar(
            limite, current_app.config["GERAR_QUADRO_SCREENER"]
        )), 202
    except ExecucaoScreenerEmAndamento as erro:
        return jsonify(erro={"codigo": "EXECUCAO_EM_ANDAMENTO", "mensagem": str(erro)}), 409
    except ErroConfiguracaoScreener as erro:
        return jsonify(erro={"codigo": erro.codigo, "mensagem": str(erro)}), 400


@screener_api.get("/api/screener/execucoes/<identificador>")
def consultar_execucao_screener(identificador):
    try:
        return jsonify(current_app.config["GERENCIADOR_SCREENER"].obter(identificador))
    except KeyError:
        return jsonify(erro={"codigo": "EXECUCAO_NAO_ENCONTRADA", "mensagem": "Execução não encontrada."}), 404


@screener_api.post("/api/screener/execucoes/<identificador>/cancelamento")
def cancelar_execucao_screener(identificador):
    try:
        return jsonify(current_app.config["GERENCIADOR_SCREENER"].cancelar(identificador)), 202
    except KeyError:
        return jsonify(erro={"codigo": "EXECUCAO_NAO_ENCONTRADA", "mensagem": "Execução não encontrada."}), 404
    except RuntimeError as erro:
        return jsonify(erro={"codigo": "EXECUCAO_NAO_CANCELAVEL", "mensagem": str(erro)}), 409
