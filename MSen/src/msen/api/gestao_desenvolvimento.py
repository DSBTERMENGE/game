"""API explícita da Gestão do desenvolvimento."""

from dataclasses import asdict
from datetime import date, datetime
import re

from flask import Blueprint, current_app, jsonify, request

from msen.config import ErroConfiguracaoBanco, carregar_configuracao_banco
from msen.database.connection import ErroConexaoBanco, abrir_conexao
from msen.database.gestao_desenvolvimento_repository import (
    ErroRepositorioGestaoDesenvolvimento,
    RepositorioGestaoDesenvolvimento,
)
from msen.services.gestao_desenvolvimento import (
    DadosManutencao, ErroGestaoDesenvolvimento,
    STATUS_PUBLICACAO, STATUS_TRABALHO, TIPOS,
)


gestao_desenvolvimento_api = Blueprint("gestao_desenvolvimento_api", __name__)
CHAVE_IDEMPOTENCIA = re.compile(r"^[0-9a-f]{64}$")


def _repositorio():
    return abrir_conexao(carregar_configuracao_banco())


def listar_no_banco(**consulta):
    with _repositorio() as conexao:
        return RepositorioGestaoDesenvolvimento(conexao).listar(**consulta)


def consultar_no_banco(identificador):
    with _repositorio() as conexao:
        return RepositorioGestaoDesenvolvimento(conexao).consultar(identificador)


def historico_no_banco(identificador):
    with _repositorio() as conexao:
        return RepositorioGestaoDesenvolvimento(conexao).listar_historico(identificador)


def criar_no_banco(dados, chave):
    with _repositorio() as conexao:
        return RepositorioGestaoDesenvolvimento(conexao).criar(dados, chave)


def atualizar_no_banco(identificador, versao, dados):
    with _repositorio() as conexao:
        return RepositorioGestaoDesenvolvimento(conexao).atualizar(identificador, versao, dados)


def arquivar_no_banco(identificador, versao, arquivar):
    with _repositorio() as conexao:
        return RepositorioGestaoDesenvolvimento(conexao).definir_arquivamento(identificador, versao, arquivar)


def _serializar(registro):
    dados = asdict(registro)
    for chave, valor in tuple(dados.items()):
        if isinstance(valor, (date, datetime)):
            dados[chave] = valor.isoformat()
    return dados


def _erro(codigo, mensagem, status):
    return jsonify(erro={"codigo": codigo, "mensagem": mensagem}), status


def _inteiro(nome, valor, minimo=1, maximo=None):
    try:
        numero = int(valor)
    except (TypeError, ValueError):
        raise ErroGestaoDesenvolvimento("PARAMETRO_INVALIDO", f"{nome} deve ser inteiro.") from None
    if numero < minimo or (maximo is not None and numero > maximo):
        raise ErroGestaoDesenvolvimento("PARAMETRO_INVALIDO", f"{nome} está fora do intervalo permitido.")
    return numero


def _filtro(nome, valor, permitidos):
    if valor is None or valor == "":
        return None
    normalizado = valor.strip().upper()
    if normalizado not in permitidos:
        raise ErroGestaoDesenvolvimento("PARAMETRO_INVALIDO", f"{nome} possui valor inválido.")
    return normalizado


def _tratar(erro):
    if isinstance(erro, ErroGestaoDesenvolvimento):
        return _erro(erro.codigo, str(erro), 400)
    if isinstance(erro, ErroRepositorioGestaoDesenvolvimento):
        if erro.codigo == "NAO_ENCONTRADO":
            return _erro(erro.codigo, "O registro não foi encontrado.", 404)
        if erro.codigo == "CONFLITO_VERSAO":
            return _erro(erro.codigo, "O registro foi alterado. Atualize a consulta antes de tentar novamente.", 409)
    return _erro("SERVICO_INDISPONIVEL", "Não foi possível concluir a operação.", 503)


@gestao_desenvolvimento_api.get("/api/gestao-desenvolvimento")
def listar():
    try:
        pagina = _inteiro("pagina", request.args.get("pagina", 1))
        por_pagina = _inteiro("por_pagina", request.args.get("por_pagina", 20), 1, 100)
        arquivados = request.args.get("arquivados", "false").lower()
        if arquivados not in {"true", "false"}:
            raise ErroGestaoDesenvolvimento("PARAMETRO_INVALIDO", "arquivados deve ser true ou false.")
        busca = request.args.get("busca", "").strip()
        if len(busca) > 200:
            raise ErroGestaoDesenvolvimento("PARAMETRO_INVALIDO", "busca aceita no máximo 200 caracteres.")
        registros, total = current_app.config["LISTAR_GESTAO_DESENVOLVIMENTO"](
            busca=busca, tipo=_filtro("tipo", request.args.get("tipo"), TIPOS),
            status_trabalho=_filtro("status_trabalho", request.args.get("status_trabalho"), STATUS_TRABALHO),
            status_publicacao=_filtro("status_publicacao", request.args.get("status_publicacao"), STATUS_PUBLICACAO),
            arquivados=arquivados == "true",
            pagina=pagina, por_pagina=por_pagina,
        )
        return jsonify(registros=[_serializar(item) for item in registros], total=total,
                       pagina=pagina, por_pagina=por_pagina)
    except (ErroGestaoDesenvolvimento, ErroRepositorioGestaoDesenvolvimento,
            ErroConfiguracaoBanco, ErroConexaoBanco) as erro:
        return _tratar(erro)


@gestao_desenvolvimento_api.get("/api/gestao-desenvolvimento/<int:identificador>")
def consultar(identificador):
    try:
        return jsonify(registro=_serializar(current_app.config["CONSULTAR_GESTAO_DESENVOLVIMENTO"](identificador)))
    except (ErroRepositorioGestaoDesenvolvimento, ErroConfiguracaoBanco, ErroConexaoBanco) as erro:
        return _tratar(erro)


@gestao_desenvolvimento_api.get("/api/gestao-desenvolvimento/<int:identificador>/historico")
def historico(identificador):
    try:
        eventos = current_app.config["HISTORICO_GESTAO_DESENVOLVIMENTO"](identificador)
        return jsonify(eventos=[_serializar(evento) for evento in eventos])
    except (ErroRepositorioGestaoDesenvolvimento, ErroConfiguracaoBanco, ErroConexaoBanco) as erro:
        return _tratar(erro)


@gestao_desenvolvimento_api.post("/api/gestao-desenvolvimento")
def criar():
    try:
        corpo = request.get_json(silent=True)
        if not isinstance(corpo, dict) or set(corpo) != {"dados", "chave_idempotencia"}:
            raise ErroGestaoDesenvolvimento("JSON_INVALIDO", "Informe dados e chave_idempotencia.")
        chave = corpo["chave_idempotencia"]
        if not isinstance(chave, str) or not CHAVE_IDEMPOTENCIA.fullmatch(chave):
            raise ErroGestaoDesenvolvimento("CHAVE_INVALIDA", "A chave de idempotência deve possuir 64 caracteres hexadecimais.")
        registro, criado = current_app.config["CRIAR_GESTAO_DESENVOLVIMENTO"](DadosManutencao.validar(corpo["dados"]), chave)
        return jsonify(registro=_serializar(registro), criado=criado), 201 if criado else 200
    except (ErroGestaoDesenvolvimento, ErroRepositorioGestaoDesenvolvimento,
            ErroConfiguracaoBanco, ErroConexaoBanco) as erro:
        return _tratar(erro)


@gestao_desenvolvimento_api.put("/api/gestao-desenvolvimento/<int:identificador>")
def atualizar(identificador):
    try:
        corpo = request.get_json(silent=True)
        if not isinstance(corpo, dict) or set(corpo) != {"dados", "versao_registro"}:
            raise ErroGestaoDesenvolvimento("JSON_INVALIDO", "Informe dados e versao_registro.")
        versao = _inteiro("versao_registro", corpo["versao_registro"])
        registro = current_app.config["ATUALIZAR_GESTAO_DESENVOLVIMENTO"](
            identificador, versao, DadosManutencao.validar(corpo["dados"])
        )
        return jsonify(registro=_serializar(registro))
    except (ErroGestaoDesenvolvimento, ErroRepositorioGestaoDesenvolvimento,
            ErroConfiguracaoBanco, ErroConexaoBanco) as erro:
        return _tratar(erro)


def _alterar_arquivo(identificador, arquivar):
    try:
        corpo = request.get_json(silent=True)
        if not isinstance(corpo, dict) or set(corpo) != {"versao_registro"}:
            raise ErroGestaoDesenvolvimento("JSON_INVALIDO", "Informe versao_registro.")
        registro = current_app.config["ARQUIVAR_GESTAO_DESENVOLVIMENTO"](
            identificador, _inteiro("versao_registro", corpo["versao_registro"]), arquivar
        )
        return jsonify(registro=_serializar(registro))
    except (ErroGestaoDesenvolvimento, ErroRepositorioGestaoDesenvolvimento,
            ErroConfiguracaoBanco, ErroConexaoBanco) as erro:
        return _tratar(erro)


@gestao_desenvolvimento_api.post("/api/gestao-desenvolvimento/<int:identificador>/arquivamento")
def arquivar(identificador):
    return _alterar_arquivo(identificador, True)


@gestao_desenvolvimento_api.delete("/api/gestao-desenvolvimento/<int:identificador>/arquivamento")
def desarquivar(identificador):
    return _alterar_arquivo(identificador, False)
