"""API CRUD dos grupos conceituais usados para organizar padrões."""

import re
from typing import Callable

import psycopg
from flask import Blueprint, current_app, jsonify, request

from msen.config import ErroConfiguracaoBanco, carregar_configuracao_banco
from msen.database import (
    ErroConexaoBanco,
    ErroRepositorioGrupoPadrao,
    GrupoPadraoPersistido,
    RepositorioGruposPadroes,
    abrir_conexao,
)


grupos_padroes_api = Blueprint("grupos_padroes_api", __name__)
FORMATO_CODIGO_GRUPO = re.compile(r"PG_[0-9]{3,}")
CAMPOS_EDITAVEIS_GRUPO = frozenset({"grupo_nome", "grupo_descr"})
CAMPOS_PROTEGIDOS_GRUPO = frozenset({"id_grupo", "grupo_cod"})


class ErroEntradaGrupoPadrao(ValueError):
    """Representa conteúdo inválido recebido pelo CRUD de grupos."""

    def __init__(self, codigo: str, mensagem: str) -> None:
        """Cria um erro com código apropriado para a resposta HTTP."""

        super().__init__(mensagem)
        self.codigo = codigo


def listar_grupos_padroes_do_banco() -> tuple[GrupoPadraoPersistido, ...]:
    """Abre uma conexão curta e lista os grupos de padrões."""

    with abrir_conexao(carregar_configuracao_banco()) as conexao:
        return RepositorioGruposPadroes(conexao).listar()


def criar_grupo_padrao_no_banco(
    nome: str, descricao: str
) -> GrupoPadraoPersistido:
    """Abre uma conexão curta e cria um grupo com código automático."""

    with abrir_conexao(carregar_configuracao_banco()) as conexao:
        return RepositorioGruposPadroes(conexao).criar(nome, descricao)


def editar_grupo_padrao_no_banco(
    codigo: str, nome: str, descricao: str
) -> GrupoPadraoPersistido:
    """Abre uma conexão curta e altera nome e descrição do grupo."""

    with abrir_conexao(carregar_configuracao_banco()) as conexao:
        return RepositorioGruposPadroes(conexao).atualizar_textos(
            codigo, nome, descricao
        )


def excluir_grupo_padrao_no_banco(codigo: str) -> GrupoPadraoPersistido:
    """Abre uma conexão curta e exclui um grupo que não possua padrões."""

    with abrir_conexao(carregar_configuracao_banco()) as conexao:
        return RepositorioGruposPadroes(conexao).excluir(codigo)


def serializar_grupo_padrao(grupo: GrupoPadraoPersistido) -> dict[str, object]:
    """Converte um grupo persistido no contrato JSON da interface."""

    return {
        "id_grupo": grupo.id_grupo,
        "grupo_cod": grupo.grupo_cod,
        "grupo_nome": grupo.grupo_nome,
        "grupo_descr": grupo.grupo_descr,
    }


def _erro(codigo: str, mensagem: str, status: int):
    return jsonify(erro={"codigo": codigo, "mensagem": mensagem}), status


def _validar_codigo(codigo: str) -> str:
    if FORMATO_CODIGO_GRUPO.fullmatch(codigo) is None:
        raise ErroEntradaGrupoPadrao(
            "CODIGO_INVALIDO", "O código deve seguir o formato PG_001."
        )
    return codigo


def _textos_da_requisicao() -> tuple[str, str]:
    dados = request.get_json(silent=True)
    if not isinstance(dados, dict):
        raise ErroEntradaGrupoPadrao(
            "JSON_INVALIDO", "O corpo deve ser um objeto JSON."
        )

    if CAMPOS_PROTEGIDOS_GRUPO.intersection(dados):
        raise ErroEntradaGrupoPadrao(
            "CAMPOS_PROTEGIDOS",
            "Código e identificador do grupo são controlados pelo sistema.",
        )
    if set(dados).difference(CAMPOS_EDITAVEIS_GRUPO):
        raise ErroEntradaGrupoPadrao(
            "CAMPOS_DESCONHECIDOS", "O corpo contém campos não reconhecidos."
        )

    nome = dados.get("grupo_nome")
    descricao = dados.get("grupo_descr")
    if not isinstance(nome, str) or not nome.strip() or len(nome.strip()) > 200:
        raise ErroEntradaGrupoPadrao(
            "NOME_INVALIDO",
            "O nome deve ser preenchido e aceitar no máximo 200 caracteres.",
        )
    if (
        not isinstance(descricao, str)
        or not descricao.strip()
        or len(descricao.strip()) > 4_000
    ):
        raise ErroEntradaGrupoPadrao(
            "DESCRICAO_INVALIDA",
            "A descrição deve ser preenchida e aceitar no máximo 4.000 caracteres.",
        )
    return nome.strip(), descricao.strip()


def _tratar_erro_repositorio(erro: ErroRepositorioGrupoPadrao):
    if erro.codigo == "GRUPO_NAO_ENCONTRADO":
        return _erro(erro.codigo, "O grupo de padrões não foi encontrado.", 404)
    if erro.codigo == "GRUPO_DUPLICADO":
        return _erro(erro.codigo, "Já existe um grupo com esse nome.", 409)
    if erro.codigo == "GRUPO_EM_USO":
        return _erro(
            erro.codigo,
            "O grupo possui padrões e não pode ser excluído.",
            409,
        )
    return _erro(
        "BANCO_INDISPONIVEL", "Não foi possível concluir a operação.", 503
    )


@grupos_padroes_api.get("/api/grupos-padroes")
def listar_grupos_padroes():
    """Lista os grupos em ordem crescente de código."""

    servico: Callable[[], tuple[GrupoPadraoPersistido, ...]] = current_app.config[
        "LISTAR_GRUPOS_PADROES"
    ]
    try:
        itens = servico()
    except (
        ErroConfiguracaoBanco,
        ErroConexaoBanco,
        ErroRepositorioGrupoPadrao,
        psycopg.Error,
    ):
        return _erro(
            "BANCO_INDISPONIVEL", "Não foi possível consultar os grupos.", 503
        )
    grupos = [serializar_grupo_padrao(item) for item in itens]
    return jsonify(grupos=grupos, total=len(grupos))


@grupos_padroes_api.post("/api/grupos-padroes")
def criar_grupo_padrao():
    """Cria um grupo textual com código automático protegido."""

    try:
        nome, descricao = _textos_da_requisicao()
        criado = current_app.config["CRIAR_GRUPO_PADRAO"](nome, descricao)
    except ErroEntradaGrupoPadrao as erro:
        return _erro(erro.codigo, str(erro), 400)
    except ErroRepositorioGrupoPadrao as erro:
        return _tratar_erro_repositorio(erro)
    except (ErroConfiguracaoBanco, ErroConexaoBanco, psycopg.Error):
        return _erro(
            "BANCO_INDISPONIVEL", "Não foi possível cadastrar o grupo.", 503
        )
    return jsonify(grupo=serializar_grupo_padrao(criado)), 201


@grupos_padroes_api.put("/api/grupos-padroes/<codigo>")
def editar_grupo_padrao(codigo: str):
    """Edita somente o nome e a descrição do grupo informado."""

    try:
        codigo_valido = _validar_codigo(codigo)
        nome, descricao = _textos_da_requisicao()
        editado = current_app.config["EDITAR_GRUPO_PADRAO"](
            codigo_valido, nome, descricao
        )
    except ErroEntradaGrupoPadrao as erro:
        return _erro(erro.codigo, str(erro), 400)
    except ErroRepositorioGrupoPadrao as erro:
        return _tratar_erro_repositorio(erro)
    except (ErroConfiguracaoBanco, ErroConexaoBanco, psycopg.Error):
        return _erro(
            "BANCO_INDISPONIVEL", "Não foi possível atualizar o grupo.", 503
        )
    return jsonify(grupo=serializar_grupo_padrao(editado))


@grupos_padroes_api.delete("/api/grupos-padroes/<codigo>")
def excluir_grupo_padrao(codigo: str):
    """Exclui um grupo vazio; a confirmação visual pertence ao frontend."""

    try:
        codigo_valido = _validar_codigo(codigo)
        excluido = current_app.config["EXCLUIR_GRUPO_PADRAO"](codigo_valido)
    except ErroEntradaGrupoPadrao as erro:
        return _erro(erro.codigo, str(erro), 400)
    except ErroRepositorioGrupoPadrao as erro:
        return _tratar_erro_repositorio(erro)
    except (ErroConfiguracaoBanco, ErroConexaoBanco, psycopg.Error):
        return _erro(
            "BANCO_INDISPONIVEL", "Não foi possível excluir o grupo.", 503
        )
    return jsonify(
        grupo=serializar_grupo_padrao(excluido), mensagem="Grupo excluído."
    )
