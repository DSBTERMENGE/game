"""API do estudo de frequência das dezenas."""

from __future__ import annotations

from copy import deepcopy
from bisect import bisect_right
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
    RepositorioConfiguracaoFrequencia,
    abrir_conexao,
)
from msen.services import (
    ConfiguracaoFrequencia,
    ErroCargaHistoricoFrequencia,
    OperacaoFrequenciaCancelada,
    atualizar_historico_frequencia,
    preparar_operacao_historico_frequencia,
    simular_historico_frequencia,
)


frequencias_api = Blueprint("frequencias_api", __name__)
TIPOS_EVENTO = frozenset({"SIMPLES", "2VS", "3VS"})
CAMPOS_CONFIGURACAO = frozenset({
    "nome", "concurso_inicial", "tamanho_inicial", "regra_janela",
    "tipo_evento", "metodo_faixa", "parametro_faixa", "unidade_parametro",
    "regra_arredondamento", "versao_calculo",
})


class ErroApiFrequencia(ValueError):
    def __init__(self, codigo: str, mensagem: str) -> None:
        super().__init__(mensagem)
        self.codigo = codigo


class ExecucaoFrequenciaEmAndamento(RuntimeError):
    def __init__(self, identificador: str) -> None:
        super().__init__(identificador)
        self.identificador = identificador


def _decimal_texto(valor) -> str | None:
    return None if valor is None else format(valor, "f")


def _consultar_ocorrencias_reais(
    cursor, *, dezena: int, tipo_evento: str, inicio: int, fim: int
) -> list[int]:
    condicoes = [
        "%s IN (r.res_01, r.res_02, r.res_03, r.res_04, r.res_05, r.res_06)"
    ]
    parametros = [dezena]
    for deslocamento in range(1, {"SIMPLES": 1, "2VS": 2, "3VS": 3}[tipo_evento]):
        alias = f"r{deslocamento}"
        condicoes.append(
            f"EXISTS (SELECT 1 FROM resultados AS {alias} "
            f"WHERE {alias}.numero_ap=r.numero_ap-{deslocamento} "
            f"AND %s IN ({alias}.res_01, {alias}.res_02, {alias}.res_03, "
            f"{alias}.res_04, {alias}.res_05, {alias}.res_06))"
        )
        parametros.append(dezena)
    cursor.execute(
        "SELECT r.numero_ap FROM resultados AS r WHERE "
        + " AND ".join(condicoes)
        + " AND r.numero_ap BETWEEN %s AND %s ORDER BY r.numero_ap",
        (*parametros, inicio, fim),
    )
    return [linha[0] for linha in cursor.fetchall()]


def avaliar_assertividade_frequencia(
    pontos: list[dict[str, object]], ocorrencias_reais: list[int]
) -> dict[str, object]:
    avaliacoes = []
    acertos = erros = censurados = 0
    soma_absoluta = Decimal("0")
    soma_percentual = Decimal("0")
    for ponto in pontos:
        corte = int(ponto["numero_do_concurso"])
        posicao = bisect_right(ocorrencias_reais, corte)
        anterior = ocorrencias_reais[posicao - 1] if posicao > 0 else None
        proxima = ocorrencias_reais[posicao] if posicao < len(ocorrencias_reais) else None
        inferior = ponto.get("concurso_limite_inferior")
        superior = ponto.get("concurso_limite_superior")
        central_texto = ponto.get("previsao_central")
        if None in (anterior, proxima, inferior, superior, central_texto):
            censurados += 1
            avaliacoes.append({
                "numero_do_concurso": corte, "estado": "CENSURADO",
                "concurso_anterior": anterior, "concurso_real": proxima,
                "limite_inferior": inferior, "limite_superior": superior,
                "previsao_central": central_texto,
                "erro_absoluto": None, "erro_percentual": None,
            })
            continue
        central = Decimal(str(central_texto))
        erro_absoluto = abs(Decimal(proxima) - central)
        intervalo_real = Decimal(proxima - anterior)
        erro_percentual = erro_absoluto * Decimal("100") / intervalo_real
        if inferior <= proxima <= superior:
            estado = "ACERTO"
            acertos += 1
        elif proxima < inferior:
            estado = "ERRO_ABAIXO"
            erros += 1
        else:
            estado = "ERRO_ACIMA"
            erros += 1
        soma_absoluta += erro_absoluto
        soma_percentual += erro_percentual
        avaliacoes.append({
            "numero_do_concurso": corte, "estado": estado,
            "concurso_anterior": anterior, "concurso_real": proxima,
            "limite_inferior": inferior, "limite_superior": superior,
            "previsao_central": _decimal_texto(central),
            "erro_absoluto": _decimal_texto(erro_absoluto),
            "erro_percentual": _decimal_texto(erro_percentual),
        })
    avaliaveis = acertos + erros
    return {
        "regra_denominador": "INTERVALO_REAL_ENTRE_EVENTOS",
        "limites_inclusivos": True,
        "total": len(avaliacoes), "avaliaveis": avaliaveis,
        "acertos": acertos, "erros": erros, "censurados": censurados,
        "percentual_acerto": None if not avaliaveis else _decimal_texto(
            Decimal(acertos) * Decimal("100") / Decimal(avaliaveis)
        ),
        "erro_absoluto_medio": None if not avaliaveis else _decimal_texto(
            soma_absoluta / Decimal(avaliaveis)
        ),
        "erro_percentual_medio": None if not avaliaveis else _decimal_texto(
            soma_percentual / Decimal(avaliaveis)
        ),
        "avaliacoes": avaliacoes,
    }


def _configuracao_dict(config: ConfiguracaoFrequencia) -> dict[str, object]:
    return {
        **config.conteudo_assinavel(),
        "assinatura_sha256": config.assinatura_sha256,
    }


def _configuracao_json(dados: object) -> ConfiguracaoFrequencia:
    if not isinstance(dados, dict):
        raise ErroApiFrequencia(
            "CORPO_INVALIDO", "configuracao deve ser um objeto JSON."
        )
    desconhecidos = set(dados) - CAMPOS_CONFIGURACAO
    ausentes = CAMPOS_CONFIGURACAO - set(dados)
    if desconhecidos or ausentes:
        raise ErroApiFrequencia(
            "CONFIGURACAO_INVALIDA",
            "A configuração deve possuir exatamente os campos documentados.",
        )
    try:
        parametro = Decimal(str(dados["parametro_faixa"]))
        return ConfiguracaoFrequencia(
            nome=dados["nome"],
            concurso_inicial=dados["concurso_inicial"],
            tamanho_inicial=dados["tamanho_inicial"],
            regra_janela=dados["regra_janela"],
            tipo_evento=dados["tipo_evento"],
            metodo_faixa=dados["metodo_faixa"],
            parametro_faixa=parametro,
            unidade_parametro=dados["unidade_parametro"],
            regra_arredondamento=dados["regra_arredondamento"],
            versao_calculo=dados["versao_calculo"],
        )
    except (TypeError, ValueError, InvalidOperation) as erro:
        raise ErroApiFrequencia("CONFIGURACAO_INVALIDA", str(erro)) from erro


def _booleano(dados: dict, nome: str, padrao: bool) -> bool:
    valor = dados.get(nome, padrao)
    if not isinstance(valor, bool):
        raise ErroApiFrequencia("CORPO_INVALIDO", f"{nome} deve ser booleano.")
    return valor


def _inteiro_consulta(nome: str, texto: str | None, *, minimo: int, maximo: int) -> int | None:
    if texto is None or texto == "":
        return None
    try:
        valor = int(texto)
    except ValueError as erro:
        raise ErroApiFrequencia("PARAMETRO_INVALIDO", f"{nome} deve ser inteiro.") from erro
    if not minimo <= valor <= maximo:
        raise ErroApiFrequencia(
            "PARAMETRO_INVALIDO", f"{nome} deve estar entre {minimo} e {maximo}."
        )
    return valor


def consultar_estado_frequencia(conexao) -> dict[str, object]:
    persistida = RepositorioConfiguracaoFrequencia(conexao).buscar_ativa()
    with conexao.cursor() as cursor:
        cursor.execute("SELECT count(*), min(numero_ap), max(numero_ap) FROM resultados")
        quantidade, minimo, maximo = cursor.fetchone()
        cursor.execute(
            "SELECT id_geracao, estado, concurso_inicial, concurso_final, "
            "quantidade_fotografias, quantidade_resultados, "
            "assinatura_configuracao, criada_em, concluida_em "
            "FROM geracoes_frequencia_dezenas WHERE estado='ATIVA'"
        )
        geracao = cursor.fetchone()
        cursor.execute("SELECT count(*) FROM historico_frequencia_dezenas")
        linhas = cursor.fetchone()[0]
    return {
        "configuracao_ativa": _configuracao_dict(persistida.configuracao),
        "configuracao_atualizada_em": persistida.atualizado_em.isoformat(),
        "resultados": {
            "quantidade": quantidade, "concurso_inicial": minimo,
            "concurso_final": maximo,
        },
        "geracao_ativa": None if geracao is None else {
            "id": geracao[0], "estado": geracao[1], "concurso_inicial": geracao[2],
            "concurso_final": geracao[3], "quantidade_fotografias": geracao[4],
            "quantidade_resultados": geracao[5],
            "assinatura_configuracao": geracao[6].strip(),
            "criada_em": geracao[7].isoformat(),
            "concluida_em": geracao[8].isoformat(),
        },
        "linhas_historicas": linhas,
    }


def consultar_fotografia_atual_frequencia(
    conexao, *, tipo_evento: str = "SIMPLES"
) -> dict[str, object]:
    if tipo_evento not in TIPOS_EVENTO:
        raise ErroApiFrequencia(
            "PARAMETRO_INVALIDO", "tipo_evento deve ser SIMPLES, 2VS ou 3VS."
        )
    with conexao.cursor() as cursor:
        cursor.execute(
            "SELECT id_geracao, concurso_inicial, concurso_final, "
            "quantidade_resultados, concluida_em "
            "FROM geracoes_frequencia_dezenas WHERE estado='ATIVA'"
        )
        geracao = cursor.fetchone()
        if geracao is None:
            return {
                "tipo_evento": tipo_evento, "unidade_intervalos": "CONCURSOS",
                "concurso_inicial": None, "concurso_final": None,
                "quantidade_resultados": 0, "atualizado_em": None, "dezenas": [],
            }
        cursor.execute(
            "SELECT dezena, quantidade_ocorrencias, quantidade_intervalos, "
            "intervalo_minimo, intervalo_maximo, media_intervalos, "
            "mediana_intervalos, desvio_padrao_intervalos "
            "FROM historico_frequencia_dezenas WHERE id_geracao=%s "
            "AND numero_do_concurso=%s AND tipo_evento=%s ORDER BY dezena",
            (geracao[0], geracao[2], tipo_evento),
        )
        linhas = cursor.fetchall()
    return {
        "tipo_evento": tipo_evento,
        "unidade_intervalos": "CONCURSOS",
        "concurso_inicial": geracao[1],
        "concurso_final": geracao[2],
        "quantidade_resultados": geracao[3],
        "atualizado_em": geracao[4].isoformat(),
        "dezenas": [{
            "dezena": linha[0], "quantidade_ocorrencias": linha[1],
            "quantidade_intervalos": linha[2], "intervalo_minimo": linha[3],
            "intervalo_maximo": linha[4],
            "media_intervalos": _decimal_texto(linha[5]),
            "mediana_intervalos": _decimal_texto(linha[6]),
            "desvio_padrao_intervalos": _decimal_texto(linha[7]),
        } for linha in linhas],
    }


def consultar_serie_frequencia(
    conexao, *, dezena: int, tipo_evento: str,
    concurso_inicial: int | None, concurso_final: int | None,
) -> dict[str, object]:
    with conexao.cursor() as cursor:
        cursor.execute(
            "SELECT id_geracao, concurso_inicial, concurso_final "
            "FROM geracoes_frequencia_dezenas WHERE estado='ATIVA'"
        )
        geracao = cursor.fetchone()
        if geracao is None:
            return {"dezena": dezena, "tipo_evento": tipo_evento, "pontos": [],
                    "ocorrencias_reais": [], "total": 0, "geracao": None}
        inicio = geracao[1] if concurso_inicial is None else concurso_inicial
        fim = geracao[2] if concurso_final is None else concurso_final
        if inicio > fim:
            raise ErroApiFrequencia(
                "PARAMETRO_INVALIDO", "concurso_inicial não pode superar concurso_final."
            )
        if fim - inicio + 1 > 5000:
            raise ErroApiFrequencia(
                "PERIODO_MUITO_LONGO", "A série está limitada a 5.000 concursos."
            )
        cursor.execute(
            "SELECT numero_do_concurso, quantidade_ocorrencias, "
            "quantidade_intervalos, intervalo_minimo, intervalo_maximo, "
            "media_intervalos, mediana_intervalos, desvio_padrao_intervalos, "
            "previsao_central, limite_inferior_exato, limite_superior_exato, "
            "concurso_limite_inferior, concurso_limite_superior "
            "FROM historico_frequencia_dezenas WHERE id_geracao=%s "
            "AND dezena=%s AND tipo_evento=%s AND numero_do_concurso BETWEEN %s AND %s "
            "ORDER BY numero_do_concurso LIMIT 5000",
            (geracao[0], dezena, tipo_evento, inicio, fim),
        )
        linhas = cursor.fetchall()
        todas_ocorrencias = _consultar_ocorrencias_reais(
            cursor, dezena=dezena, tipo_evento=tipo_evento,
            inicio=1, fim=geracao[2],
        )
        ocorrencias_reais = [x for x in todas_ocorrencias if inicio <= x <= fim]
    pontos = [{
        "numero_do_concurso": x[0], "quantidade_ocorrencias": x[1],
        "quantidade_intervalos": x[2], "intervalo_minimo": x[3],
        "intervalo_maximo": x[4], "media_intervalos": _decimal_texto(x[5]),
        "mediana_intervalos": _decimal_texto(x[6]),
        "desvio_padrao_intervalos": _decimal_texto(x[7]),
        "previsao_central": _decimal_texto(x[8]),
        "limite_inferior_exato": _decimal_texto(x[9]),
        "limite_superior_exato": _decimal_texto(x[10]),
        "concurso_limite_inferior": x[11], "concurso_limite_superior": x[12],
    } for x in linhas]
    return {
        "dezena": dezena, "tipo_evento": tipo_evento,
        "unidade_intervalos": "CONCURSOS", "total": len(linhas),
        "geracao": {"id": geracao[0], "concurso_inicial": geracao[1],
                    "concurso_final": geracao[2]},
        "periodo": {"concurso_inicial": inicio, "concurso_final": fim},
        "ocorrencias_reais": ocorrencias_reais,
        "assertividade": avaliar_assertividade_frequencia(pontos, todas_ocorrencias),
        "pontos": pontos,
    }


def _previa_dict(previa) -> dict[str, object]:
    dados = asdict(previa)
    dados["divergencias_configuracao"] = [
        asdict(item) for item in previa.divergencias_configuracao
    ]
    return dados


def consultar_estado_no_banco():
    with abrir_conexao(carregar_configuracao_banco()) as conexao:
        return consultar_estado_frequencia(conexao)


def consultar_fotografia_no_banco(tipo_evento="SIMPLES"):
    with abrir_conexao(carregar_configuracao_banco()) as conexao:
        return consultar_fotografia_atual_frequencia(
            conexao, tipo_evento=tipo_evento
        )


def consultar_serie_no_banco(filtros):
    with abrir_conexao(carregar_configuracao_banco()) as conexao:
        return consultar_serie_frequencia(conexao, **filtros)


def preparar_no_banco(configuracao, salvar_dados):
    with abrir_conexao(carregar_configuracao_banco()) as conexao:
        return _previa_dict(preparar_operacao_historico_frequencia(
            conexao, configuracao, salvar_dados=salvar_dados
        ))


def executar_no_banco(solicitacao, progresso, cancelado):
    with abrir_conexao(carregar_configuracao_banco()) as conexao:
        if solicitacao["salvar_dados"]:
            relatorio = atualizar_historico_frequencia(
                conexao, solicitacao["configuracao"],
                reconstruir_origem_alterada=solicitacao["reconstruir_origem"],
                confirmacao_gravacao=solicitacao["confirmacao_gravacao"],
                informar_progresso=progresso,
                cancelamento_solicitado=cancelado,
            )
            return {"tipo": "GRAVACAO", **asdict(relatorio)}
        relatorio = simular_historico_frequencia(
            conexao, solicitacao["configuracao"], informar_progresso=progresso,
            cancelamento_solicitado=cancelado,
        )
        return {
            "tipo": "SIMULACAO", "fotografias_calculadas": relatorio.fotografias_calculadas,
            "linhas_calculadas": relatorio.linhas_calculadas,
            "duracao_segundos": relatorio.duracao_segundos,
            "previa": _previa_dict(relatorio.previa),
        }


class GerenciadorExecucoesFrequencia:
    def __init__(self, operacao: Callable | None = None) -> None:
        self._operacao = operacao or executar_no_banco
        self._trava = Lock()
        self._execucoes: dict[str, dict[str, object]] = {}
        self._cancelamentos: dict[str, Event] = {}
        self._ativa: str | None = None

    def iniciar(self, solicitacao: dict[str, object]) -> dict[str, object]:
        with self._trava:
            if self._ativa is not None and self._execucoes[self._ativa]["estado"] in {
                "AGUARDANDO", "EXECUTANDO", "CANCELAMENTO_SOLICITADO"
            }:
                raise ExecucaoFrequenciaEmAndamento(self._ativa)
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
                raise ErroApiFrequencia(
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
                dados["estado"] = "EXECUTANDO"
                dados["etapa"] = etapa
            dados["concluido"] = concluido
            dados["total"] = total
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
        except OperacaoFrequenciaCancelada:
            estado, etapa, erro = "CANCELADA", "Cancelada com segurança", None
            resultado = None
        except Exception as falha:
            estado, etapa = "FALHOU", "Execução interrompida"
            erro = {"tipo": type(falha).__name__, "mensagem": str(falha)}
            resultado = None
        else:
            estado, etapa, erro = "CONCLUIDA", "Concluída", None
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


def _erro_json(erro, status=400):
    return jsonify(erro={"codigo": erro.codigo, "mensagem": str(erro)}), status


@frequencias_api.get("/api/frequencias/estado")
def rota_estado_frequencia():
    try:
        return jsonify(current_app.config["CONSULTAR_ESTADO_FREQUENCIA"]())
    except psycopg.Error:
        return jsonify(erro={"codigo": "BANCO_INDISPONIVEL",
                             "mensagem": "Não foi possível consultar o banco."}), 503


@frequencias_api.get("/api/frequencias/fotografia-atual")
def rota_fotografia_atual():
    try:
        tipo = (request.args.get("tipo_evento") or "SIMPLES").upper()
        if tipo not in TIPOS_EVENTO:
            raise ErroApiFrequencia(
                "PARAMETRO_INVALIDO", "tipo_evento deve ser SIMPLES, 2VS ou 3VS."
            )
        return jsonify(
            current_app.config["CONSULTAR_FOTOGRAFIA_FREQUENCIA"](tipo)
        )
    except ErroApiFrequencia as erro:
        return _erro_json(erro)
    except psycopg.Error:
        return jsonify(erro={"codigo": "BANCO_INDISPONIVEL",
                             "mensagem": "Não foi possível consultar o banco."}), 503


@frequencias_api.get("/api/frequencias/serie")
def rota_serie_frequencia():
    try:
        dezena = _inteiro_consulta("dezena", request.args.get("dezena"), minimo=1, maximo=60)
        if dezena is None:
            raise ErroApiFrequencia("PARAMETRO_INVALIDO", "dezena é obrigatória.")
        tipo = (request.args.get("tipo_evento") or "").upper()
        if tipo not in TIPOS_EVENTO:
            raise ErroApiFrequencia(
                "PARAMETRO_INVALIDO", "tipo_evento deve ser SIMPLES, 2VS ou 3VS."
            )
        filtros = {
            "dezena": dezena, "tipo_evento": tipo,
            "concurso_inicial": _inteiro_consulta(
                "concurso_inicial", request.args.get("concurso_inicial"),
                minimo=1, maximo=10_000_000,
            ),
            "concurso_final": _inteiro_consulta(
                "concurso_final", request.args.get("concurso_final"),
                minimo=1, maximo=10_000_000,
            ),
        }
        return jsonify(current_app.config["CONSULTAR_SERIE_FREQUENCIA"](filtros))
    except ErroApiFrequencia as erro:
        return _erro_json(erro)
    except psycopg.Error:
        return jsonify(erro={"codigo": "BANCO_INDISPONIVEL",
                             "mensagem": "Não foi possível consultar o banco."}), 503


@frequencias_api.post("/api/frequencias/previa")
def rota_previa_frequencia():
    try:
        dados = request.get_json(silent=True)
        if not isinstance(dados, dict):
            raise ErroApiFrequencia("CORPO_INVALIDO", "Envie um objeto JSON.")
        if set(dados) - {"configuracao", "salvar_dados"}:
            raise ErroApiFrequencia("CORPO_INVALIDO", "A prévia contém campos desconhecidos.")
        config = _configuracao_json(dados.get("configuracao"))
        salvar = _booleano(dados, "salvar_dados", True)
        return jsonify(current_app.config["PREPARAR_FREQUENCIA"](config, salvar))
    except ErroApiFrequencia as erro:
        return _erro_json(erro)
    except psycopg.Error:
        return jsonify(erro={"codigo": "BANCO_INDISPONIVEL",
                             "mensagem": "Não foi possível consultar o banco."}), 503


@frequencias_api.post("/api/frequencias/execucoes")
def rota_iniciar_execucao_frequencia():
    try:
        dados = request.get_json(silent=True)
        if not isinstance(dados, dict):
            raise ErroApiFrequencia("CORPO_INVALIDO", "Envie um objeto JSON.")
        if set(dados) - {
            "configuracao", "salvar_dados", "confirmacao_gravacao",
            "reconstruir_origem",
        }:
            raise ErroApiFrequencia("CORPO_INVALIDO", "A execução contém campos desconhecidos.")
        solicitacao = {
            "configuracao": _configuracao_json(dados.get("configuracao")),
            "salvar_dados": _booleano(dados, "salvar_dados", True),
            "confirmacao_gravacao": _booleano(dados, "confirmacao_gravacao", False),
            "reconstruir_origem": _booleano(dados, "reconstruir_origem", False),
        }
        if solicitacao["salvar_dados"] and not solicitacao["confirmacao_gravacao"]:
            raise ErroApiFrequencia(
                "CONFIRMACAO_OBRIGATORIA",
                "Confirme explicitamente a gravação antes de iniciar.",
            )
        gerenciador = current_app.config["GERENCIADOR_FREQUENCIA"]
        return jsonify(gerenciador.iniciar(solicitacao)), 202
    except ErroApiFrequencia as erro:
        return _erro_json(erro)
    except ExecucaoFrequenciaEmAndamento as erro:
        return jsonify(erro={"codigo": "EXECUCAO_EM_ANDAMENTO",
                             "mensagem": "Já existe uma operação em andamento.",
                             "id_execucao": erro.identificador}), 409


@frequencias_api.get("/api/frequencias/execucoes/<identificador>")
def rota_consultar_execucao_frequencia(identificador):
    try:
        return jsonify(current_app.config["GERENCIADOR_FREQUENCIA"].obter(identificador))
    except KeyError:
        return jsonify(erro={"codigo": "EXECUCAO_NAO_ENCONTRADA",
                             "mensagem": "A execução não foi encontrada."}), 404


@frequencias_api.post("/api/frequencias/execucoes/<identificador>/cancelamento")
def rota_cancelar_execucao_frequencia(identificador):
    try:
        return jsonify(current_app.config["GERENCIADOR_FREQUENCIA"].cancelar(identificador)), 202
    except KeyError:
        return jsonify(erro={"codigo": "EXECUCAO_NAO_ENCONTRADA",
                             "mensagem": "A execução não foi encontrada."}), 404
    except ErroApiFrequencia as erro:
        return _erro_json(erro, 409)
