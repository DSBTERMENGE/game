"""API CRUD do cadastro de padrões, com estatísticas protegidas."""

from decimal import Decimal
import re
from typing import Callable

import psycopg
from flask import Blueprint, current_app, jsonify, request

from msen.config import ErroConfiguracaoBanco, carregar_configuracao_banco
from msen.database import (
    ErroConexaoBanco,
    ErroRepositorioPadrao,
    PadraoPersistido,
    RepositorioPadroes,
    abrir_conexao,
)
from msen.padroes import criar_registro_detectores_iniciais


padroes_api = Blueprint("padroes_api", __name__)
FORMATO_CODIGO = re.compile(r"PD_[0-9]{3,}")
CAMPOS_EDITAVEIS = frozenset({"padrao_nome", "padrao_descr"})
CAMPOS_PROTEGIDOS = frozenset(
    {"id_padrao", "padrao_cod", "num_oco", "intervalo_medio", "desv_padrao"}
)


class ErroEntradaPadrao(ValueError):
    """Representa conteúdo inválido recebido pelo CRUD de padrões."""

    def __init__(self, codigo: str, mensagem: str) -> None:
        """Cria um erro com código apropriado para a resposta HTTP."""

        super().__init__(mensagem)
        self.codigo = codigo


def listar_padroes_do_banco() -> tuple[PadraoPersistido, ...]:
    """Abre uma conexão curta e lista o cadastro de padrões."""

    with abrir_conexao(carregar_configuracao_banco()) as conexao:
        return RepositorioPadroes(conexao).listar()


def criar_padrao_no_banco(nome: str, descricao: str) -> PadraoPersistido:
    """Abre uma conexão curta e cria um padrão com código automático."""

    with abrir_conexao(carregar_configuracao_banco()) as conexao:
        return RepositorioPadroes(conexao).criar(nome, descricao)


def editar_padrao_no_banco(
    codigo: str, nome: str, descricao: str
) -> PadraoPersistido:
    """Abre uma conexão curta e altera somente os textos do padrão."""

    with abrir_conexao(carregar_configuracao_banco()) as conexao:
        return RepositorioPadroes(conexao).atualizar_textos(codigo, nome, descricao)


def excluir_padrao_no_banco(codigo: str) -> PadraoPersistido:
    """Abre uma conexão curta e exclui o padrão sem reutilizar seu código."""

    with abrir_conexao(carregar_configuracao_banco()) as conexao:
        return RepositorioPadroes(conexao).excluir(codigo)


def _decimal_texto(valor: Decimal | None) -> str | None:
    return None if valor is None else format(valor, "f")


def serializar_padrao(padrao: PadraoPersistido) -> dict[str, object]:
    """Converte uma linha persistida no contrato JSON do frontend."""

    registro = criar_registro_detectores_iniciais()
    return {
        "id_padrao": padrao.id_padrao,
        "padrao_cod": padrao.padrao_cod,
        "padrao_nome": padrao.padrao_nome,
        "padrao_descr": padrao.padrao_descr,
        "num_oco": padrao.num_oco,
        "intervalo_medio": _decimal_texto(padrao.intervalo_medio),
        "desv_padrao": _decimal_texto(padrao.desv_padrao),
        "detector_implementado": registro.contem(padrao.padrao_cod),
    }


def _erro(codigo: str, mensagem: str, status: int):
    return jsonify(erro={"codigo": codigo, "mensagem": mensagem}), status


def _validar_codigo(codigo: str) -> str:
    if FORMATO_CODIGO.fullmatch(codigo) is None:
        raise ErroEntradaPadrao(
            "CODIGO_INVALIDO", "O código deve seguir o formato PD_001."
        )
    return codigo


def _textos_da_requisicao() -> tuple[str, str]:
    dados = request.get_json(silent=True)
    if not isinstance(dados, dict):
        raise ErroEntradaPadrao("JSON_INVALIDO", "O corpo deve ser um objeto JSON.")

    protegidos = CAMPOS_PROTEGIDOS.intersection(dados)
    if protegidos:
        raise ErroEntradaPadrao(
            "CAMPOS_PROTEGIDOS",
            "Código, identificador e estatísticas são controlados pelo sistema.",
        )
    desconhecidos = set(dados).difference(CAMPOS_EDITAVEIS)
    if desconhecidos:
        raise ErroEntradaPadrao(
            "CAMPOS_DESCONHECIDOS", "O corpo contém campos não reconhecidos."
        )

    nome = dados.get("padrao_nome")
    descricao = dados.get("padrao_descr")
    if not isinstance(nome, str) or not nome.strip():
        raise ErroEntradaPadrao(
            "NOME_INVALIDO", "O nome do padrão deve ser preenchido."
        )
    if len(nome.strip()) > 200:
        raise ErroEntradaPadrao(
            "NOME_INVALIDO", "O nome do padrão aceita no máximo 200 caracteres."
        )
    if not isinstance(descricao, str) or not descricao.strip():
        raise ErroEntradaPadrao(
            "DESCRICAO_INVALIDA", "A descrição do padrão deve ser preenchida."
        )
    if len(descricao.strip()) > 4_000:
        raise ErroEntradaPadrao(
            "DESCRICAO_INVALIDA",
            "A descrição do padrão aceita no máximo 4.000 caracteres.",
        )
    return nome.strip(), descricao.strip()


def _tratar_erro_repositorio(erro: ErroRepositorioPadrao):
    if erro.codigo == "PADRAO_NAO_ENCONTRADO":
        return _erro(erro.codigo, "O padrão não foi encontrado.", 404)
    if erro.codigo in {"PADRAO_DUPLICADO", "CADASTRO_CONFLITANTE"}:
        return _erro("PADRAO_DUPLICADO", "Já existe um padrão com esse nome.", 409)
    return _erro(
        "BANCO_INDISPONIVEL", "Não foi possível concluir a operação.", 503
    )


@padroes_api.get("/api/padroes")
def listar_padroes():
    """Lista cadastro, estatísticas e disponibilidade dos detectores."""

    servico: Callable[[], tuple[PadraoPersistido, ...]] = current_app.config[
        "LISTAR_PADROES"
    ]
    try:
        itens = servico()
    except (
        ErroConfiguracaoBanco,
        ErroConexaoBanco,
        ErroRepositorioPadrao,
        psycopg.Error,
    ):
        return _erro(
            "BANCO_INDISPONIVEL", "Não foi possível consultar os padrões.", 503
        )
    padroes = [serializar_padrao(item) for item in itens]
    return jsonify(padroes=padroes, total=len(padroes))


@padroes_api.post("/api/padroes")
def criar_padrao():
    """Cria um cadastro textual com código automático e estatísticas nulas."""

    try:
        nome, descricao = _textos_da_requisicao()
        servico = current_app.config["CRIAR_PADRAO"]
        criado = servico(nome, descricao)
    except ErroEntradaPadrao as erro:
        return _erro(erro.codigo, str(erro), 400)
    except ErroRepositorioPadrao as erro:
        return _tratar_erro_repositorio(erro)
    except (ErroConfiguracaoBanco, ErroConexaoBanco, psycopg.Error):
        return _erro(
            "BANCO_INDISPONIVEL", "Não foi possível cadastrar o padrão.", 503
        )
    return jsonify(padrao=serializar_padrao(criado)), 201


@padroes_api.put("/api/padroes/<codigo>")
def editar_padrao(codigo: str):
    """Edita somente nome e descrição do código informado."""

    try:
        codigo_valido = _validar_codigo(codigo)
        nome, descricao = _textos_da_requisicao()
        servico = current_app.config["EDITAR_PADRAO"]
        editado = servico(codigo_valido, nome, descricao)
    except ErroEntradaPadrao as erro:
        return _erro(erro.codigo, str(erro), 400)
    except ErroRepositorioPadrao as erro:
        return _tratar_erro_repositorio(erro)
    except (ErroConfiguracaoBanco, ErroConexaoBanco, psycopg.Error):
        return _erro(
            "BANCO_INDISPONIVEL", "Não foi possível atualizar o padrão.", 503
        )
    return jsonify(padrao=serializar_padrao(editado))


@padroes_api.delete("/api/padroes/<codigo>")
def excluir_padrao(codigo: str):
    """Exclui o padrão indicado; a confirmação visual pertence ao frontend."""

    try:
        codigo_valido = _validar_codigo(codigo)
        servico = current_app.config["EXCLUIR_PADRAO"]
        excluido = servico(codigo_valido)
    except ErroEntradaPadrao as erro:
        return _erro(erro.codigo, str(erro), 400)
    except ErroRepositorioPadrao as erro:
        return _tratar_erro_repositorio(erro)
    except (ErroConfiguracaoBanco, ErroConexaoBanco, psycopg.Error):
        return _erro(
            "BANCO_INDISPONIVEL", "Não foi possível excluir o padrão.", 503
        )
    return jsonify(padrao=serializar_padrao(excluido), mensagem="Padrão excluído.")
