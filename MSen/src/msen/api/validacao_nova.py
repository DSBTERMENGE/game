"""API e controle da nova validação e auditoria de filtros."""

from collections.abc import Callable, Iterable
from copy import deepcopy
from datetime import datetime, timezone
from threading import Event, Lock, Thread
from time import monotonic
from uuid import uuid4

from flask import Blueprint, current_app, jsonify, request

from msen.config import carregar_configuracao_banco
from msen.database import abrir_conexao
from msen.modelos import ResultadoEntrada
from msen.padroes import criar_fotografia_historica_diagonal
from msen.services import (
    ErroCatalogoFiltrosValidacao,
    GrupoFiltrosValidacao,
    carregar_catalogo_filtros_validacao,
    OperacaoValidacaoNovaCancelada,
    OcorrenciaFiltroValidacaoNova,
    ErroProcessamentoValidacaoNova,
    processar_validacao_nova_no_banco,
    carregar_executor_filtro_validacao,
    ErroTesteDirigidoValidacaoNova,
    gerar_colecao_dirigida_no_banco,
    carregar_desenho_ocorrencia_validacao,
)


validacao_nova_api = Blueprint("validacao_nova_api", __name__)


class ExecucaoValidacaoNovaEmAndamento(RuntimeError):
    pass


class GerenciadorExecucoesValidacaoNova:
    """Mantém uma execução ativa, seu progresso mínimo e o relatório em memória."""

    def __init__(self, operacao: Callable) -> None:
        if not callable(operacao):
            raise TypeError("A operação da validação nova deve ser chamável.")
        self._operacao = operacao
        self._trava = Lock()
        self._execucoes: dict[str, dict[str, object]] = {}
        self._continuacoes: dict[str, Event] = {}
        self._ativa: str | None = None

    def iniciar(self, ids_filtros: Iterable[int] | None = None) -> dict[str, object]:
        selecao = None if ids_filtros is None else tuple(ids_filtros)
        with self._trava:
            if self._ativa is not None:
                ativa = self._execucoes[self._ativa]
                if ativa["estado"] in {"AGUARDANDO", "EXECUTANDO", "CANCELANDO"}:
                    raise ExecucaoValidacaoNovaEmAndamento(self._ativa)
            identificador = str(uuid4())
            agora = datetime.now(timezone.utc)
            self._execucoes[identificador] = {
                "id": identificador,
                "estado": "AGUARDANDO",
                "concluido": 0,
                "total": 0,
                "percentual": 0,
                "grupo_atual": None,
                "filtro_atual": None,
                "resultado": None,
                "ocorrencia_atual": None,
                "erro": None,
                "iniciada_em": agora.isoformat(),
                "terminada_em": None,
                "duracao_segundos": 0.0,
                "_inicio": monotonic(),
                "_cancelar": False,
                "_inspecionar_ocorrencias": True,
            }
            self._ativa = identificador
            self._continuacoes[identificador] = Event()
        Thread(
            target=self._executar,
            args=(identificador, selecao),
            daemon=True,
        ).start()
        return self.obter(identificador)

    def obter(self, identificador: str) -> dict[str, object]:
        with self._trava:
            if identificador not in self._execucoes:
                raise KeyError(identificador)
            dados = deepcopy(self._execucoes[identificador])
            if dados["estado"] in {
                "AGUARDANDO", "EXECUTANDO", "CANCELANDO", "AGUARDANDO_CONFIRMACAO"
            }:
                dados["duracao_segundos"] = round(
                    monotonic() - float(dados["_inicio"]), 3
                )
            dados.pop("_inicio", None)
            dados.pop("_cancelar", None)
            dados.pop("_inspecionar_ocorrencias", None)
            return dados

    def cancelar(self, identificador: str) -> dict[str, object]:
        with self._trava:
            if identificador not in self._execucoes:
                raise KeyError(identificador)
            dados = self._execucoes[identificador]
            if dados["estado"] in {
                "AGUARDANDO", "EXECUTANDO", "AGUARDANDO_CONFIRMACAO"
            }:
                dados["_cancelar"] = True
                dados["estado"] = "CANCELANDO"
                self._continuacoes[identificador].set()
        return self.obter(identificador)

    def continuar(self, identificador: str) -> dict[str, object]:
        with self._trava:
            if identificador not in self._execucoes:
                raise KeyError(identificador)
            dados = self._execucoes[identificador]
            if dados["estado"] != "AGUARDANDO_CONFIRMACAO":
                raise ErroProcessamentoValidacaoNova(
                    "EXECUCAO_NAO_PAUSADA",
                    "O teste não está aguardando confirmação de uma ocorrência.",
                )
            dados["estado"] = "EXECUTANDO"
            dados["ocorrencia_atual"] = None
            self._continuacoes[identificador].set()
        return self.obter(identificador)

    def concluir(self, identificador: str) -> dict[str, object]:
        """Retoma a execução sem pausar nas ocorrências restantes."""
        with self._trava:
            if identificador not in self._execucoes:
                raise KeyError(identificador)
            dados = self._execucoes[identificador]
            if dados["estado"] != "AGUARDANDO_CONFIRMACAO":
                raise ErroProcessamentoValidacaoNova(
                    "EXECUCAO_NAO_PAUSADA",
                    "O teste não está aguardando confirmação de uma ocorrência.",
                )
            dados["_inspecionar_ocorrencias"] = False
            dados["estado"] = "EXECUTANDO"
            dados["ocorrencia_atual"] = None
            self._continuacoes[identificador].set()
        return self.obter(identificador)

    def _cancelado(self, identificador: str) -> bool:
        with self._trava:
            return bool(self._execucoes[identificador]["_cancelar"])

    def _progresso(
        self,
        identificador: str,
        concluido: int,
        total: int,
        grupo: str,
        filtro: str,
    ) -> None:
        if total <= 0 or not 0 <= concluido <= total:
            raise ValueError("Progresso inválido.")
        with self._trava:
            dados = self._execucoes[identificador]
            if dados["estado"] != "CANCELANDO":
                dados["estado"] = "EXECUTANDO"
            dados.update(
                concluido=concluido,
                total=total,
                percentual=round(concluido * 100 / total, 2),
                grupo_atual=grupo,
                filtro_atual=filtro,
                duracao_segundos=round(monotonic() - float(dados["_inicio"]), 3),
            )

    def _pausar_na_ocorrencia(
        self, identificador: str, ocorrencia: OcorrenciaFiltroValidacaoNova
    ) -> None:
        evento = self._continuacoes[identificador]
        evento.clear()
        with self._trava:
            dados = self._execucoes[identificador]
            if not dados["_inspecionar_ocorrencias"]:
                return
            dados["estado"] = "AGUARDANDO_CONFIRMACAO"
            dados["ocorrencia_atual"] = {
                "id_grupo": ocorrencia.id_grupo,
                "nome_grupo": ocorrencia.nome_grupo,
                "id_filtro": ocorrencia.id_filtro,
                "nome_filtro": ocorrencia.nome_filtro,
                "indice_combinacao": ocorrencia.indice_combinacao,
                "combinacao": list(ocorrencia.combinacao),
                "desenho": getattr(ocorrencia, "desenho", None),
            }
        evento.wait()
        if self._cancelado(identificador):
            raise OperacaoValidacaoNovaCancelada(
                "O teste foi cancelado durante a análise de uma ocorrência."
            )

    def _executar(self, identificador: str, ids_filtros) -> None:
        try:
            resultado = self._operacao(
                ids_filtros,
                lambda concluido, total, grupo, filtro: self._progresso(
                    identificador, concluido, total, grupo, filtro
                ),
                lambda: self._cancelado(identificador),
                lambda ocorrencia: self._pausar_na_ocorrencia(
                    identificador, ocorrencia
                ),
            )
        except OperacaoValidacaoNovaCancelada:
            self._finalizar(identificador, "CANCELADA")
            return
        except Exception as erro:
            self._finalizar(
                identificador,
                "FALHOU",
                erro={"tipo": type(erro).__name__, "mensagem": str(erro)},
            )
            return
        self._finalizar(identificador, "CONCLUIDA", resultado=resultado)

    def _finalizar(self, identificador, estado, *, resultado=None, erro=None) -> None:
        with self._trava:
            dados = self._execucoes[identificador]
            dados.update(
                estado=estado,
                resultado=resultado,
                erro=erro,
                terminada_em=datetime.now(timezone.utc).isoformat(),
                duracao_segundos=round(monotonic() - float(dados["_inicio"]), 3),
            )
            if estado == "CONCLUIDA":
                dados["concluido"] = dados["total"]
                dados["percentual"] = 100
            self._ativa = None


class GerenciadorTestesDirigidosValidacaoNova:
    """Mantém as coleções dirigidas somente na memória do processo atual."""

    def __init__(self, preparar: Callable, testar: Callable) -> None:
        if not callable(preparar) or not callable(testar):
            raise TypeError("Preparação e teste dirigido devem ser chamáveis.")
        self._preparar = preparar
        self._testar = testar
        self._trava = Lock()
        self._testes: dict[str, dict[str, object]] = {}
        self._avaliacoes: dict[str, tuple[dict[str, object], ...]] = {}
        self._posicoes: dict[str, int] = {}

    def criar(self, id_grupo: int, id_filtro: int) -> dict[str, object]:
        preparado = self._preparar(id_grupo, id_filtro)
        identificador = str(uuid4())
        registro = {
            "id": identificador,
            "estado": "GERADO",
            "id_grupo": preparado["id_grupo"],
            "nome_grupo": preparado["nome_grupo"],
            "id_filtro": preparado["id_filtro"],
            "nome_filtro": preparado["nome_filtro"],
            "tentativas_geracao": preparado["tentativas_geracao"],
            "total_combinacoes": len(preparado["combinacoes"]),
            "combinacoes": tuple(tuple(item) for item in preparado["combinacoes"]),
            "resultado": None,
            "ocorrencia_atual": None,
        }
        with self._trava:
            self._testes[identificador] = registro
        return self.obter(identificador)

    def obter(self, identificador: str) -> dict[str, object]:
        with self._trava:
            if identificador not in self._testes:
                raise KeyError(identificador)
            return deepcopy(self._testes[identificador])

    def testar(self, identificador: str) -> dict[str, object]:
        with self._trava:
            if identificador not in self._testes:
                raise KeyError(identificador)
            registro = deepcopy(self._testes[identificador])
        resultado_bruto = self._testar(
            registro["id_filtro"], tuple(registro["combinacoes"])
        )
        avaliacoes = tuple(resultado_bruto["avaliacoes"])
        if len(avaliacoes) != registro["total_combinacoes"]:
            raise RuntimeError("O teste dirigido não avaliou todas as combinações geradas.")
        with self._trava:
            atual = self._testes[identificador]
            self._avaliacoes[identificador] = avaliacoes
            self._posicoes[identificador] = 0
            atual["estado"] = "AGUARDANDO_CONFIRMACAO"
            atual["ocorrencia_atual"] = deepcopy(avaliacoes[0])
            return deepcopy(atual)

    def continuar(self, identificador: str) -> dict[str, object]:
        with self._trava:
            if identificador not in self._testes:
                raise KeyError(identificador)
            atual = self._testes[identificador]
            if atual["estado"] != "AGUARDANDO_CONFIRMACAO":
                raise ErroTesteDirigidoValidacaoNova(
                    "TESTE_NAO_PAUSADO",
                    "O teste dirigido não está aguardando confirmação.",
                )
            proxima = self._posicoes[identificador] + 1
            avaliacoes = self._avaliacoes[identificador]
            if proxima < len(avaliacoes):
                self._posicoes[identificador] = proxima
                atual["ocorrencia_atual"] = deepcopy(avaliacoes[proxima])
            else:
                detectadas = sum(bool(item["detectada"]) for item in avaliacoes)
                atual["estado"] = "TESTADO"
                atual["ocorrencia_atual"] = None
                atual["resultado"] = {
                    "total_testado": len(avaliacoes),
                    "ocorrencias_detectadas": detectadas,
                }
            return deepcopy(atual)

    def concluir(self, identificador: str) -> dict[str, object]:
        """Conclui a inspeção dirigida com as avaliações já realizadas."""
        with self._trava:
            if identificador not in self._testes:
                raise KeyError(identificador)
            atual = self._testes[identificador]
            if atual["estado"] != "AGUARDANDO_CONFIRMACAO":
                raise ErroTesteDirigidoValidacaoNova(
                    "TESTE_NAO_PAUSADO",
                    "O teste dirigido não está aguardando confirmação.",
                )
            avaliacoes = self._avaliacoes[identificador]
            detectadas = sum(bool(item["detectada"]) for item in avaliacoes)
            atual["estado"] = "TESTADO"
            atual["ocorrencia_atual"] = None
            atual["resultado"] = {
                "total_testado": len(avaliacoes),
                "ocorrencias_detectadas": detectadas,
            }
            return deepcopy(atual)


    def cancelar(self, identificador: str) -> dict[str, object]:
        with self._trava:
            if identificador not in self._testes:
                raise KeyError(identificador)
            atual = self._testes[identificador]
            if atual["estado"] != "AGUARDANDO_CONFIRMACAO":
                raise ErroTesteDirigidoValidacaoNova(
                    "TESTE_NAO_PAUSADO",
                    "O teste dirigido não está aguardando confirmação.",
                )
            atual["estado"] = "CANCELADO"
            atual["ocorrencia_atual"] = None
            self._avaliacoes.pop(identificador, None)
            self._posicoes.pop(identificador, None)
            return deepcopy(atual)


def consultar_catalogo_validacao_nova_no_banco() -> tuple[GrupoFiltrosValidacao, ...]:
    with abrir_conexao(carregar_configuracao_banco()) as conexao:
        return carregar_catalogo_filtros_validacao(conexao)


def _fotografia_diagonal(conexao):
    with conexao.cursor() as cursor:
        cursor.execute(
            "SELECT data_resultado,numero_ap,res_01,res_02,res_03,res_04,res_05,res_06 "
            "FROM resultados ORDER BY numero_ap"
        )
        historico = tuple(
            ResultadoEntrada.criar(
                data_resultado=linha[0],
                numero_ap=linha[1],
                resultados=linha[2:],
            )
            for linha in cursor.fetchall()
        )
    if not historico:
        raise ErroProcessamentoValidacaoNova(
            "HISTORICO_VAZIO", "O histórico necessário ao filtro diagonal está vazio."
        )
    return criar_fotografia_historica_diagonal(historico)


def executar_teste_validacao_nova_no_banco(
    ids_filtros, progresso, cancelado, informar_ocorrencia
):
    """Executa a coleção fixa e devolve um relatório serializável para a API."""

    with abrir_conexao(carregar_configuracao_banco()) as conexao:
        relatorio = processar_validacao_nova_no_banco(
            conexao,
            ids_filtros=ids_filtros,
            fotografia_diagonal=_fotografia_diagonal(conexao),
            informar_progresso=progresso,
            cancelamento_solicitado=cancelado,
            informar_ocorrencia=informar_ocorrencia,
            construir_desenho=lambda id_filtro, combinacao: (
                carregar_desenho_ocorrencia_validacao(
                    conexao, id_filtro, combinacao
                ).como_dict()
            ),
        )
    return {
        "total_combinacoes": relatorio.total_combinacoes,
        "total_filtros": relatorio.total_filtros,
        "total_avaliacoes": relatorio.total_avaliacoes,
        "resultados": [
            {
                "id_grupo": item.id_grupo,
                "nome_grupo": item.nome_grupo,
                "id_filtro": item.id_filtro,
                "nome_filtro": item.nome_filtro,
                "total_testado": item.total_testado,
                "ocorrencias": item.ocorrencias,
                "incidencia_percentual": str(item.incidencia_percentual),
            }
            for item in relatorio.resultados
        ],
    }


def preparar_teste_dirigido_no_banco(id_grupo: int, id_filtro: int):
    with abrir_conexao(carregar_configuracao_banco()) as conexao:
        catalogo = carregar_catalogo_filtros_validacao(conexao)
        localizado = next(
            (
                (grupo, filtro)
                for grupo in catalogo
                for filtro in grupo.filtros
                if grupo.id_grupo == id_grupo and filtro.id_filtro == id_filtro
            ),
            None,
        )
        if localizado is None:
            raise ErroTesteDirigidoValidacaoNova(
                "FILTRO_INDISPONIVEL",
                "O grupo e o filtro selecionados não correspondem a um filtro executável.",
            )
        grupo, filtro = localizado
        colecao = gerar_colecao_dirigida_no_banco(
            conexao,
            id_filtro,
            fotografia_diagonal=_fotografia_diagonal(conexao),
        )
    return {
        "id_grupo": grupo.id_grupo,
        "nome_grupo": grupo.nome,
        "id_filtro": filtro.id_filtro,
        "nome_filtro": filtro.nome,
        "tentativas_geracao": colecao.tentativas,
        "combinacoes": colecao.combinacoes,
    }


def testar_colecao_dirigida_no_banco(id_filtro: int, combinacoes):
    with abrir_conexao(carregar_configuracao_banco()) as conexao:
        executor = carregar_executor_filtro_validacao(
            conexao,
            id_filtro,
            fotografia_diagonal=_fotografia_diagonal(conexao),
        )
        avaliacoes = tuple({
            "numero": indice,
            "combinacao": list(item),
            "detectada": executor(tuple(item)),
            "desenho": carregar_desenho_ocorrencia_validacao(
                conexao, id_filtro, tuple(item)
            ).como_dict(),
        } for indice, item in enumerate(combinacoes, start=1))
    return {
        "avaliacoes": avaliacoes,
    }


def _serializar(grupos: tuple[GrupoFiltrosValidacao, ...]) -> dict[str, object]:
    return {
        "total_grupos": len(grupos),
        "total_filtros": sum(len(grupo.filtros) for grupo in grupos),
        "grupos": [
            {
                "id_grupo": grupo.id_grupo,
                "nome_grupo": grupo.nome,
                "filtros": [
                    {
                        "id_filtro": filtro.id_filtro,
                        "nome_filtro": filtro.nome,
                        "descricao": filtro.descricao,
                    }
                    for filtro in grupo.filtros
                ],
            }
            for grupo in grupos
        ],
    }


@validacao_nova_api.get("/api/validacao-nova/filtros")
def listar_filtros_validacao_nova():
    if request.args:
        return jsonify(erro={
            "codigo": "PARAMETROS_NAO_PERMITIDOS",
            "mensagem": "A consulta do catálogo não recebe parâmetros.",
        }), 400
    try:
        grupos = current_app.config["CONSULTAR_CATALOGO_VALIDACAO_NOVA"]()
        return jsonify(_serializar(tuple(grupos)))
    except ErroCatalogoFiltrosValidacao:
        return jsonify(erro={
            "codigo": "CATALOGO_INDISPONIVEL",
            "mensagem": "Não foi possível consultar os filtros disponíveis.",
        }), 503


def _ids_solicitados():
    dados = request.get_json(silent=True)
    if dados is None:
        return None
    if not isinstance(dados, dict) or set(dados) - {"ids_filtros"}:
        raise ErroProcessamentoValidacaoNova(
            "SOLICITACAO_INVALIDA", "A solicitação do teste possui campos inválidos."
        )
    ids = dados.get("ids_filtros")
    if ids is None:
        return None
    if not isinstance(ids, list):
        raise ErroProcessamentoValidacaoNova(
            "SELECAO_INVALIDA", "A seleção de filtros deve ser uma lista de IDs."
        )
    if not ids:
        raise ErroProcessamentoValidacaoNova(
            "SELECAO_VAZIA", "Selecione ao menos um filtro para realizar o teste."
        )
    if any(isinstance(item, bool) or not isinstance(item, int) or item <= 0 for item in ids):
        raise ErroProcessamentoValidacaoNova(
            "IDENTIFICADOR_INVALIDO", "A seleção contém identificador de filtro inválido."
        )
    if len(set(ids)) != len(ids):
        raise ErroProcessamentoValidacaoNova(
            "FILTRO_REPETIDO", "Um mesmo filtro não pode ser selecionado mais de uma vez."
        )
    return tuple(ids)


@validacao_nova_api.post("/api/validacao-nova/execucoes")
def iniciar_teste_validacao_nova():
    try:
        ids = _ids_solicitados()
        estado = current_app.config["GERENCIADOR_VALIDACAO_NOVA"].iniciar(ids)
        return jsonify(estado), 202
    except ErroProcessamentoValidacaoNova as erro:
        return jsonify(erro={"codigo": erro.codigo, "mensagem": str(erro)}), 400
    except ExecucaoValidacaoNovaEmAndamento as erro:
        return jsonify(erro={
            "codigo": "EXECUCAO_EM_ANDAMENTO",
            "mensagem": "Já existe um teste da nova validação em andamento.",
            "id_execucao": str(erro),
        }), 409


@validacao_nova_api.get("/api/validacao-nova/execucoes/<identificador>")
def consultar_teste_validacao_nova(identificador: str):
    try:
        return jsonify(
            current_app.config["GERENCIADOR_VALIDACAO_NOVA"].obter(identificador)
        )
    except KeyError:
        return jsonify(erro={
            "codigo": "EXECUCAO_NAO_ENCONTRADA",
            "mensagem": "O teste informado não foi encontrado.",
        }), 404


@validacao_nova_api.post("/api/validacao-nova/execucoes/<identificador>/cancelamento")
def cancelar_teste_validacao_nova(identificador: str):
    try:
        return jsonify(
            current_app.config["GERENCIADOR_VALIDACAO_NOVA"].cancelar(identificador)
        ), 202
    except KeyError:
        return jsonify(erro={
            "codigo": "EXECUCAO_NAO_ENCONTRADA",
            "mensagem": "O teste informado não foi encontrado.",
        }), 404


@validacao_nova_api.post("/api/validacao-nova/execucoes/<identificador>/continuacao")
def continuar_teste_validacao_nova(identificador: str):
    try:
        estado = current_app.config["GERENCIADOR_VALIDACAO_NOVA"].continuar(
            identificador
        )
        return jsonify(estado), 202
    except KeyError:
        return jsonify(erro={
            "codigo": "EXECUCAO_NAO_ENCONTRADA",
            "mensagem": "O teste informado não foi encontrado.",
        }), 404
    except ErroProcessamentoValidacaoNova as erro:
        return jsonify(erro={"codigo": erro.codigo, "mensagem": str(erro)}), 409


@validacao_nova_api.post("/api/validacao-nova/execucoes/<identificador>/conclusao")
def concluir_teste_validacao_nova(identificador: str):
    try:
        estado = current_app.config["GERENCIADOR_VALIDACAO_NOVA"].concluir(
            identificador
        )
        return jsonify(estado), 202
    except KeyError:
        return jsonify(erro={
            "codigo": "EXECUCAO_NAO_ENCONTRADA",
            "mensagem": "O teste informado não foi encontrado.",
        }), 404
    except ErroProcessamentoValidacaoNova as erro:
        return jsonify(erro={"codigo": erro.codigo, "mensagem": str(erro)}), 409


def _id_especifico(dados, nome):
    valor = dados.get(nome)
    if isinstance(valor, bool) or not isinstance(valor, int) or valor <= 0:
        raise ErroTesteDirigidoValidacaoNova(
            "SELECAO_INVALIDA", "Selecione um grupo e um filtro específicos."
        )
    return valor


@validacao_nova_api.post("/api/validacao-nova/testes-dirigidos")
def gerar_teste_dirigido_validacao_nova():
    dados = request.get_json(silent=True)
    if not isinstance(dados, dict) or set(dados) != {"id_grupo", "id_filtro"}:
        return jsonify(erro={
            "codigo": "SOLICITACAO_INVALIDA",
            "mensagem": "Informe um grupo e um filtro específicos.",
        }), 400
    try:
        gerenciador = current_app.config["GERENCIADOR_TESTES_DIRIGIDOS_VALIDACAO_NOVA"]
        registro = gerenciador.criar(
            _id_especifico(dados, "id_grupo"),
            _id_especifico(dados, "id_filtro"),
        )
        return jsonify(registro), 201
    except ErroTesteDirigidoValidacaoNova as erro:
        status = 422 if erro.codigo == "OCORRENCIAS_INSUFICIENTES" else 400
        return jsonify(erro={"codigo": erro.codigo, "mensagem": str(erro)}), status


@validacao_nova_api.get("/api/validacao-nova/testes-dirigidos/<identificador>")
def consultar_teste_dirigido_validacao_nova(identificador: str):
    try:
        gerenciador = current_app.config["GERENCIADOR_TESTES_DIRIGIDOS_VALIDACAO_NOVA"]
        return jsonify(gerenciador.obter(identificador))
    except KeyError:
        return jsonify(erro={
            "codigo": "TESTE_DIRIGIDO_NAO_ENCONTRADO",
            "mensagem": "O teste dirigido informado não está disponível em memória.",
        }), 404


@validacao_nova_api.post("/api/validacao-nova/testes-dirigidos/<identificador>/execucao")
def executar_teste_dirigido_validacao_nova(identificador: str):
    try:
        gerenciador = current_app.config["GERENCIADOR_TESTES_DIRIGIDOS_VALIDACAO_NOVA"]
        return jsonify(gerenciador.testar(identificador))
    except KeyError:
        return jsonify(erro={
            "codigo": "TESTE_DIRIGIDO_NAO_ENCONTRADO",
            "mensagem": "O teste dirigido informado não está disponível em memória.",
        }), 404


@validacao_nova_api.post(
    "/api/validacao-nova/testes-dirigidos/<identificador>/continuacao"
)
def continuar_teste_dirigido_validacao_nova(identificador: str):
    try:
        gerenciador = current_app.config["GERENCIADOR_TESTES_DIRIGIDOS_VALIDACAO_NOVA"]
        return jsonify(gerenciador.continuar(identificador)), 202
    except KeyError:
        return jsonify(erro={
            "codigo": "TESTE_DIRIGIDO_NAO_ENCONTRADO",
            "mensagem": "O teste dirigido informado não está disponível em memória.",
        }), 404
    except ErroTesteDirigidoValidacaoNova as erro:
        return jsonify(erro={"codigo": erro.codigo, "mensagem": str(erro)}), 409


@validacao_nova_api.post(
    "/api/validacao-nova/testes-dirigidos/<identificador>/conclusao"
)
def concluir_teste_dirigido_validacao_nova(identificador: str):
    try:
        gerenciador = current_app.config["GERENCIADOR_TESTES_DIRIGIDOS_VALIDACAO_NOVA"]
        return jsonify(gerenciador.concluir(identificador)), 202
    except KeyError:
        return jsonify(erro={
            "codigo": "TESTE_DIRIGIDO_NAO_ENCONTRADO",
            "mensagem": "O teste dirigido informado não está disponível em memória.",
        }), 404
    except ErroTesteDirigidoValidacaoNova as erro:
        return jsonify(erro={"codigo": erro.codigo, "mensagem": str(erro)}), 409


@validacao_nova_api.post(
    "/api/validacao-nova/testes-dirigidos/<identificador>/cancelamento"
)
def cancelar_teste_dirigido_validacao_nova(identificador: str):
    try:
        gerenciador = current_app.config["GERENCIADOR_TESTES_DIRIGIDOS_VALIDACAO_NOVA"]
        return jsonify(gerenciador.cancelar(identificador)), 202
    except KeyError:
        return jsonify(erro={
            "codigo": "TESTE_DIRIGIDO_NAO_ENCONTRADO",
            "mensagem": "O teste dirigido informado não está disponível em memória.",
        }), 404
    except ErroTesteDirigidoValidacaoNova as erro:
        return jsonify(erro={"codigo": erro.codigo, "mensagem": str(erro)}), 409
