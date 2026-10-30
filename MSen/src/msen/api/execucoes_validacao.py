"""Tarefas assíncronas e rotas de progresso da Validação e auditoria."""

from copy import deepcopy
from datetime import datetime, timezone
from threading import Lock, Thread
from time import monotonic
from typing import Callable
from uuid import uuid4

from flask import Blueprint, current_app, jsonify

from msen.config import carregar_configuracao_banco
from msen.database import abrir_conexao
from msen.services import atualizar_validacao_e_auditoria


execucoes_validacao_api = Blueprint("execucoes_validacao_api", __name__)


class ExecucaoEmAndamento(RuntimeError):
    pass


class GerenciadorExecucoesValidacao:
    """Mantém uma única execução ativa e instantâneos consultáveis."""

    def __init__(self, operacao: Callable | None = None) -> None:
        self._operacao = operacao or executar_motor_no_banco
        self._trava = Lock()
        self._execucoes: dict[str, dict[str, object]] = {}
        self._ativa: str | None = None

    def iniciar(self) -> dict[str, object]:
        with self._trava:
            if self._ativa is not None:
                ativa = self._execucoes[self._ativa]
                if ativa["estado"] in {"AGUARDANDO", "EXECUTANDO"}:
                    raise ExecucaoEmAndamento(self._ativa)
            identificador = str(uuid4())
            agora = datetime.now(timezone.utc)
            self._execucoes[identificador] = {
                "id": identificador, "estado": "AGUARDANDO",
                "etapa": "Aguardando início", "concluido": 0, "total": 4,
                "percentual": 0, "duracao_segundos": 0.0,
                "iniciada_em": agora.isoformat(), "terminada_em": None,
                "erro": None, "resultado": None, "_inicio": monotonic(),
            }
            self._ativa = identificador
        Thread(target=self._executar, args=(identificador,), daemon=True).start()
        return self.obter(identificador)

    def obter(self, identificador: str) -> dict[str, object]:
        with self._trava:
            if identificador not in self._execucoes:
                raise KeyError(identificador)
            dados = deepcopy(self._execucoes[identificador])
            if dados["estado"] in {"AGUARDANDO", "EXECUTANDO"}:
                dados["duracao_segundos"] = round(
                    monotonic() - float(dados["_inicio"]), 3
                )
            dados.pop("_inicio", None)
            return dados

    def _progresso(self, identificador: str, etapa: str, concluido: int, total: int):
        if total <= 0 or not 0 <= concluido <= total:
            raise ValueError("Progresso inválido.")
        with self._trava:
            dados = self._execucoes[identificador]
            dados.update(
                estado="EXECUTANDO", etapa=etapa, concluido=concluido, total=total,
                percentual=round(concluido * 100 / total, 2),
                duracao_segundos=round(monotonic() - float(dados["_inicio"]), 3),
            )

    def _executar(self, identificador: str) -> None:
        try:
            resultado = self._operacao(
                lambda etapa, concluido, total: self._progresso(
                    identificador, etapa, concluido, total
                )
            )
        except Exception as erro:  # a tarefa precisa transformar falha em estado consultável
            with self._trava:
                dados = self._execucoes[identificador]
                dados.update(
                    estado="FALHOU", etapa="Execução interrompida",
                    erro={"tipo": type(erro).__name__, "mensagem": str(erro)},
                    terminada_em=datetime.now(timezone.utc).isoformat(),
                    duracao_segundos=round(monotonic() - float(dados["_inicio"]), 3),
                )
                self._ativa = None
            return
        with self._trava:
            dados = self._execucoes[identificador]
            dados.update(
                estado="CONCLUIDA", etapa="Concluída", concluido=dados["total"],
                percentual=100, resultado=resultado,
                terminada_em=datetime.now(timezone.utc).isoformat(),
                duracao_segundos=round(monotonic() - float(dados["_inicio"]), 3),
            )
            self._ativa = None


def executar_motor_no_banco(informar_progresso):
    configuracao = carregar_configuracao_banco()
    with abrir_conexao(configuracao) as conexao:
        relatorio = atualizar_validacao_e_auditoria(
            conexao, informar_progresso=informar_progresso
        )
    return {
        "homologacao_concluida": relatorio.homologacao_concluida,
        "criterios": relatorio.total_criterios,
        "avaliacoes": relatorio.total_avaliacoes,
        "aprovadas": relatorio.aprovadas,
        "reprovadas": relatorio.reprovadas,
        "pendentes": relatorio.pendentes,
        "motivo_estado_global": relatorio.motivo_estado_global,
        "sincronizacao": {
            "incluidos": list(relatorio.sincronizacao.incluidos),
            "implementacoes_alteradas": list(
                relatorio.sincronizacao.implementacoes_alteradas
            ),
            "regras_alteradas": list(relatorio.sincronizacao.regras_alteradas),
            "excluidos": list(relatorio.sincronizacao.excluidos),
            "avaliacoes_criadas": relatorio.sincronizacao.avaliacoes_criadas,
        },
    }


@execucoes_validacao_api.post("/api/validacao/execucoes")
def iniciar_execucao_validacao():
    gerenciador = current_app.config["GERENCIADOR_VALIDACAO"]
    try:
        return jsonify(gerenciador.iniciar()), 202
    except ExecucaoEmAndamento as erro:
        return jsonify(erro={
            "codigo": "EXECUCAO_EM_ANDAMENTO",
            "mensagem": "Já existe uma atualização de validação em andamento.",
            "id_execucao": str(erro),
        }), 409


@execucoes_validacao_api.get("/api/validacao/execucoes/<identificador>")
def consultar_execucao_validacao(identificador: str):
    gerenciador = current_app.config["GERENCIADOR_VALIDACAO"]
    try:
        return jsonify(gerenciador.obter(identificador))
    except KeyError:
        return jsonify(erro={
            "codigo": "EXECUCAO_NAO_ENCONTRADA",
            "mensagem": "A execução informada não foi encontrada.",
        }), 404
