"""API HTTP da pesquisa e seleção de dezenas."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import asdict
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from threading import Event, Lock, Thread
from time import monotonic
from typing import Callable
from uuid import uuid4

from flask import Blueprint, current_app, jsonify, request
import psycopg

from msen.config import carregar_configuracao_banco
from msen.database import (
    ErroRepositorioPesquisaSelecao,
    RepositorioPesquisaSelecao,
    abrir_conexao,
)
from msen.services import (
    ConfiguracaoSelecaoDezenas,
    ErroBacktestSelecao,
    ErroCombinacoesSelecao,
    atualizar_previsoes_futuras,
    calcular_previa_combinacoes,
    comparar_backtests,
    detalhar_backtest,
    executar_backtest_selecao,
    persistir_combinacoes_alvo,
    resumir_backtest,
)


selecao_dezenas_api = Blueprint("selecao_dezenas_api", __name__)
CAMPOS_CONFIGURACAO = frozenset({
    "nome", "fator_k", "fator_j", "modo_quantidade", "quantidade_dezenas",
    "horizonte_concursos", "versao_calculo",
})


class ErroApiSelecaoDezenas(ValueError):
    def __init__(self, codigo: str, mensagem: str) -> None:
        super().__init__(mensagem)
        self.codigo = codigo


class ExecucaoSelecaoEmAndamento(RuntimeError):
    def __init__(self, identificador: str) -> None:
        super().__init__(identificador)
        self.identificador = identificador


def _configuracao_json(dados: object) -> ConfiguracaoSelecaoDezenas:
    if not isinstance(dados, dict) or set(dados) != CAMPOS_CONFIGURACAO:
        raise ErroApiSelecaoDezenas(
            "CONFIGURACAO_INVALIDA",
            "A configuração deve possuir exatamente os campos documentados.",
        )
    try:
        return ConfiguracaoSelecaoDezenas(
            nome=dados["nome"],
            fator_k=Decimal(str(dados["fator_k"])),
            fator_j=Decimal(str(dados["fator_j"])),
            modo_quantidade=dados["modo_quantidade"],
            quantidade_dezenas=dados["quantidade_dezenas"],
            horizonte_concursos=dados["horizonte_concursos"],
            versao_calculo=dados["versao_calculo"],
        )
    except (TypeError, ValueError, InvalidOperation) as erro:
        raise ErroApiSelecaoDezenas("CONFIGURACAO_INVALIDA", str(erro)) from erro


def _configuracao_dict(configuracao: ConfiguracaoSelecaoDezenas) -> dict[str, object]:
    return {
        **configuracao.conteudo_assinavel(),
        "assinatura_sha256": configuracao.assinatura_sha256,
    }


def _corpo(campos: set[str]) -> dict[str, object]:
    dados = request.get_json(silent=True)
    if not isinstance(dados, dict):
        raise ErroApiSelecaoDezenas("CORPO_INVALIDO", "Envie um objeto JSON.")
    desconhecidos = set(dados) - campos
    if desconhecidos:
        raise ErroApiSelecaoDezenas(
            "CORPO_INVALIDO", "A solicitação contém campos desconhecidos."
        )
    return dados


def _inteiro(dados: dict, nome: str, *, minimo: int, obrigatorio: bool = True):
    valor = dados.get(nome)
    if valor is None and not obrigatorio:
        return None
    if isinstance(valor, bool) or not isinstance(valor, int) or valor < minimo:
        raise ErroApiSelecaoDezenas(
            "PARAMETRO_INVALIDO", f"{nome} deve ser inteiro maior ou igual a {minimo}."
        )
    return valor


def _booleano(dados: dict, nome: str, padrao: bool = False) -> bool:
    valor = dados.get(nome, padrao)
    if not isinstance(valor, bool):
        raise ErroApiSelecaoDezenas("PARAMETRO_INVALIDO", f"{nome} deve ser booleano.")
    return valor


def _serializar(valor):
    if hasattr(valor, "__dataclass_fields__"):
        return asdict(valor)
    return valor


def listar_configuracoes_no_banco():
    with abrir_conexao(carregar_configuracao_banco()) as conexao:
        itens = RepositorioPesquisaSelecao(conexao).listar_configuracoes()
        return [{
            "id_configuracao_selecao": item.id_configuracao_selecao,
            "configuracao": _configuracao_dict(item.configuracao),
            "estado": item.estado,
            "criada_em": item.criada_em,
            "arquivada_em": item.arquivada_em,
        } for item in itens]


def salvar_configuracao_no_banco(configuracao):
    with abrir_conexao(carregar_configuracao_banco()) as conexao:
        item = RepositorioPesquisaSelecao(conexao).criar_ou_buscar_configuracao(configuracao)
        return {
            "id_configuracao_selecao": item.id_configuracao_selecao,
            "configuracao": _configuracao_dict(item.configuracao),
            "estado": item.estado,
            "criada_em": item.criada_em,
        }


def preparar_pesquisa_no_banco(configuracao, concurso_inicial, concurso_final):
    with abrir_conexao(carregar_configuracao_banco()) as conexao:
        with conexao.cursor() as cursor:
            cursor.execute("SELECT MIN(numero_ap),MAX(numero_ap),COUNT(*) FROM resultados")
            primeiro, ultimo, quantidade = cursor.fetchone()
    inicio = 500 if concurso_inicial is None else concurso_inicial
    final = ultimo if concurso_final is None else concurso_final
    if ultimo is None or inicio < 500 or final < inicio or final > ultimo:
        raise ErroApiSelecaoDezenas("PERIODO_INVALIDO", "Período de backtest inválido.")
    return {
        "configuracao": _configuracao_dict(configuracao),
        "resultados": {"primeiro": primeiro, "ultimo": ultimo, "quantidade": quantidade},
        "backtest": {
            "concurso_inicial": inicio,
            "concurso_final": final,
            "quantidade_alvos": final - inicio + 1,
        },
        "previsao_futura": {
            "concurso_inicial": ultimo + 1,
            "concurso_final": ultimo + configuracao.horizonte_concursos,
            "quantidade_alvos": configuracao.horizonte_concursos,
        },
    }


def executar_backtest_no_banco(solicitacao, progresso, cancelado):
    with abrir_conexao(carregar_configuracao_banco()) as conexao:
        relatorio = executar_backtest_selecao(
            conexao,
            solicitacao["configuracao"],
            concurso_inicial=solicitacao["concurso_inicial"],
            concurso_final=solicitacao["concurso_final"],
            cancelamento_solicitado=cancelado,
            informar_progresso=lambda concluido, total: progresso(
                "Avaliando concursos", concluido, total
            ),
        )
        return asdict(relatorio)


def resumir_no_banco(identificador):
    with abrir_conexao(carregar_configuracao_banco()) as conexao:
        return asdict(resumir_backtest(conexao, identificador))


def detalhar_no_banco(identificador):
    with abrir_conexao(carregar_configuracao_banco()) as conexao:
        return [asdict(item) for item in detalhar_backtest(conexao, identificador)]


def comparar_no_banco(identificadores):
    with abrir_conexao(carregar_configuracao_banco()) as conexao:
        return asdict(comparar_backtests(conexao, identificadores))


def atualizar_previsoes_no_banco(configuracao):
    with abrir_conexao(carregar_configuracao_banco()) as conexao:
        return asdict(atualizar_previsoes_futuras(conexao, configuracao))


def previa_jogos_no_banco(id_alvo):
    with abrir_conexao(carregar_configuracao_banco()) as conexao:
        with conexao.cursor() as cursor:
            cursor.execute(
                "SELECT dezena FROM avaliacoes_dezenas_pesquisa "
                "WHERE id_alvo_selecao=%s AND retornada ORDER BY posicao_ranking",
                (id_alvo,),
            )
            dezenas = tuple(linha[0] for linha in cursor.fetchall())
        if not dezenas:
            raise ErroCombinacoesSelecao(
                "ALVO_SEM_DEZENAS", "O alvo não possui dezenas selecionadas."
            )
        return {**asdict(calcular_previa_combinacoes(dezenas)), "dezenas": dezenas}


def persistir_jogos_no_banco(id_alvo, autorizar, confirmar_volume):
    with abrir_conexao(carregar_configuracao_banco()) as conexao:
        return asdict(persistir_combinacoes_alvo(
            conexao,
            id_alvo,
            autorizar_persistencia=autorizar,
            confirmar_volume_elevado=confirmar_volume,
        ))


class GerenciadorBacktestsSelecao:
    def __init__(self, operacao: Callable | None = None) -> None:
        self._operacao = operacao or executar_backtest_no_banco
        self._trava = Lock()
        self._execucoes: dict[str, dict[str, object]] = {}
        self._cancelamentos: dict[str, Event] = {}
        self._ativa: str | None = None

    def iniciar(self, solicitacao: dict[str, object]) -> dict[str, object]:
        with self._trava:
            if self._ativa is not None and self._execucoes[self._ativa]["estado"] in {
                "AGUARDANDO", "EXECUTANDO", "CANCELAMENTO_SOLICITADO"
            }:
                raise ExecucaoSelecaoEmAndamento(self._ativa)
            identificador = str(uuid4())
            agora = datetime.now(timezone.utc)
            self._execucoes[identificador] = {
                "id": identificador, "estado": "AGUARDANDO", "etapa": "Aguardando início",
                "concluido": 0, "total": 1, "percentual": 0,
                "duracao_segundos": 0.0, "iniciada_em": agora.isoformat(),
                "terminada_em": None, "erro": None, "resultado": None,
                "_inicio": monotonic(),
            }
            self._cancelamentos[identificador] = Event()
            self._ativa = identificador
        Thread(target=self._executar, args=(identificador, solicitacao), daemon=True).start()
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
                raise ErroApiSelecaoDezenas(
                    "EXECUCAO_NAO_CANCELAVEL", "A execução já terminou."
                )
            self._cancelamentos[identificador].set()
            dados["estado"] = "CANCELAMENTO_SOLICITADO"
            dados["etapa"] = "Aguardando ponto seguro para cancelar"
        return self.obter(identificador)

    def _progresso(self, identificador, etapa, concluido, total):
        if total <= 0 or not 0 <= concluido <= total:
            raise ValueError("Progresso inválido.")
        with self._trava:
            dados = self._execucoes[identificador]
            if dados["estado"] != "CANCELAMENTO_SOLICITADO":
                dados["estado"], dados["etapa"] = "EXECUTANDO", etapa
            dados["concluido"], dados["total"] = concluido, total
            dados["percentual"] = round(concluido * 100 / total, 2)

    def _executar(self, identificador, solicitacao):
        cancelamento = self._cancelamentos[identificador]
        try:
            resultado = self._operacao(
                solicitacao,
                lambda etapa, concluido, total: self._progresso(
                    identificador, etapa, concluido, total
                ),
                cancelamento.is_set,
            )
        except Exception as falha:
            estado, etapa, resultado = "FALHOU", "Execução interrompida", None
            erro = {"codigo": getattr(falha, "codigo", "FALHA_EXECUCAO"),
                    "mensagem": "Não foi possível concluir a execução."}
        else:
            estado = "CANCELADA" if cancelamento.is_set() else "CONCLUIDA"
            etapa = "Cancelada com segurança" if cancelamento.is_set() else "Concluída"
            erro = None
        with self._trava:
            dados = self._execucoes[identificador]
            dados.update(
                estado=estado, etapa=etapa, erro=erro, resultado=resultado,
                terminada_em=datetime.now(timezone.utc).isoformat(),
                duracao_segundos=round(monotonic() - dados["_inicio"], 3),
            )
            if estado == "CONCLUIDA":
                dados["concluido"], dados["percentual"] = dados["total"], 100
            self._ativa = None


def _erro_json(erro, status=400):
    return jsonify(erro={"codigo": erro.codigo, "mensagem": str(erro)}), status


def _executar_rota(funcao):
    try:
        return funcao()
    except (
        ErroApiSelecaoDezenas,
        ErroBacktestSelecao,
        ErroCombinacoesSelecao,
        ErroRepositorioPesquisaSelecao,
    ) as erro:
        status = 404 if erro.codigo.endswith("NAO_ENCONTRADA") else 400
        return _erro_json(erro, status)
    except psycopg.Error:
        return jsonify(erro={
            "codigo": "BANCO_INDISPONIVEL",
            "mensagem": "Não foi possível concluir a operação no banco.",
        }), 503


@selecao_dezenas_api.get("/api/selecao-dezenas/configuracoes")
def rota_listar_configuracoes():
    return _executar_rota(lambda: jsonify(
        configuracoes=current_app.config["LISTAR_CONFIGURACOES_SELECAO"]()
    ))


@selecao_dezenas_api.post("/api/selecao-dezenas/configuracoes")
def rota_salvar_configuracao():
    def executar():
        dados = _corpo({"configuracao"})
        item = current_app.config["SALVAR_CONFIGURACAO_SELECAO"](
            _configuracao_json(dados.get("configuracao"))
        )
        return jsonify(item), 201
    return _executar_rota(executar)


@selecao_dezenas_api.post("/api/selecao-dezenas/previa")
def rota_previa_pesquisa():
    def executar():
        dados = _corpo({"configuracao", "concurso_inicial", "concurso_final"})
        config = _configuracao_json(dados.get("configuracao"))
        inicio = _inteiro(dados, "concurso_inicial", minimo=500, obrigatorio=False)
        final = _inteiro(dados, "concurso_final", minimo=500, obrigatorio=False)
        return jsonify(current_app.config["PREPARAR_PESQUISA_SELECAO"](
            config, inicio, final
        ))
    return _executar_rota(executar)


@selecao_dezenas_api.post("/api/selecao-dezenas/backtests")
def rota_iniciar_backtest():
    try:
        dados = _corpo({"configuracao", "concurso_inicial", "concurso_final"})
        solicitacao = {
            "configuracao": _configuracao_json(dados.get("configuracao")),
            "concurso_inicial": _inteiro(dados, "concurso_inicial", minimo=500),
            "concurso_final": _inteiro(
                dados, "concurso_final", minimo=500, obrigatorio=False
            ),
        }
        return jsonify(current_app.config["GERENCIADOR_BACKTEST_SELECAO"].iniciar(
            solicitacao
        )), 202
    except (ErroApiSelecaoDezenas, ErroBacktestSelecao) as erro:
        return _erro_json(erro)
    except ExecucaoSelecaoEmAndamento as erro:
        return jsonify(erro={
            "codigo": "EXECUCAO_EM_ANDAMENTO",
            "mensagem": "Já existe um backtest em andamento.",
            "id_execucao": erro.identificador,
        }), 409


@selecao_dezenas_api.get("/api/selecao-dezenas/execucoes/<identificador>")
def rota_consultar_execucao(identificador):
    try:
        return jsonify(current_app.config["GERENCIADOR_BACKTEST_SELECAO"].obter(identificador))
    except KeyError:
        return jsonify(erro={"codigo": "EXECUCAO_NAO_ENCONTRADA",
                             "mensagem": "A execução não foi encontrada."}), 404


@selecao_dezenas_api.post("/api/selecao-dezenas/execucoes/<identificador>/cancelamento")
def rota_cancelar_execucao(identificador):
    try:
        return jsonify(current_app.config["GERENCIADOR_BACKTEST_SELECAO"].cancelar(
            identificador
        )), 202
    except KeyError:
        return jsonify(erro={"codigo": "EXECUCAO_NAO_ENCONTRADA",
                             "mensagem": "A execução não foi encontrada."}), 404
    except ErroApiSelecaoDezenas as erro:
        return _erro_json(erro, 409)


@selecao_dezenas_api.get("/api/selecao-dezenas/backtests/<int:identificador>/resumo")
def rota_resumo_backtest(identificador):
    return _executar_rota(lambda: jsonify(
        current_app.config["RESUMIR_BACKTEST_SELECAO"](identificador)
    ))


@selecao_dezenas_api.get("/api/selecao-dezenas/backtests/<int:identificador>/detalhes")
def rota_detalhes_backtest(identificador):
    return _executar_rota(lambda: jsonify(detalhes=
        current_app.config["DETALHAR_BACKTEST_SELECAO"](identificador)
    ))


@selecao_dezenas_api.post("/api/selecao-dezenas/backtests/comparacao")
def rota_comparar_backtests():
    def executar():
        dados = _corpo({"ids_execucoes"})
        ids = dados.get("ids_execucoes")
        if not isinstance(ids, list) or any(
            isinstance(item, bool) or not isinstance(item, int) or item <= 0 for item in ids
        ):
            raise ErroApiSelecaoDezenas(
                "PARAMETRO_INVALIDO", "ids_execucoes deve ser uma lista de inteiros positivos."
            )
        return jsonify(current_app.config["COMPARAR_BACKTESTS_SELECAO"](tuple(ids)))
    return _executar_rota(executar)


@selecao_dezenas_api.post("/api/selecao-dezenas/previsoes")
def rota_atualizar_previsoes():
    def executar():
        dados = _corpo({"configuracao"})
        return jsonify(current_app.config["ATUALIZAR_PREVISOES_SELECAO"](
            _configuracao_json(dados.get("configuracao"))
        ))
    return _executar_rota(executar)


@selecao_dezenas_api.get("/api/selecao-dezenas/previsoes/<int:identificador>/detalhes")
def rota_detalhes_previsao(identificador):
    return _executar_rota(lambda: jsonify(detalhes=
        current_app.config["DETALHAR_BACKTEST_SELECAO"](identificador)
    ))


@selecao_dezenas_api.get("/api/selecao-dezenas/alvos/<int:id_alvo>/jogos/previa")
def rota_previa_jogos(id_alvo):
    return _executar_rota(lambda: jsonify(
        current_app.config["PREVIA_JOGOS_SELECAO"](id_alvo)
    ))


@selecao_dezenas_api.post("/api/selecao-dezenas/alvos/<int:id_alvo>/jogos")
def rota_persistir_jogos(id_alvo):
    def executar():
        dados = _corpo({"autorizar_persistencia", "confirmar_volume_elevado"})
        return jsonify(current_app.config["PERSISTIR_JOGOS_SELECAO"](
            id_alvo,
            _booleano(dados, "autorizar_persistencia"),
            _booleano(dados, "confirmar_volume_elevado"),
        )), 201
    return _executar_rota(executar)
