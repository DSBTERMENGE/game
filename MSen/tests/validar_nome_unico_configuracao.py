"""Valida em Games que nome repetido não cria registro nem consome identidade."""

from dotenv import load_dotenv

from msen.config import carregar_configuracao_banco
from msen.database import (
    ErroRepositorioPesquisaSelecao,
    RepositorioPesquisaSelecao,
    abrir_conexao,
)


load_dotenv()
with abrir_conexao(carregar_configuracao_banco()) as conexao:
    repositorio = RepositorioPesquisaSelecao(conexao)
    configuracao = repositorio.listar_configuracoes()[0].configuracao
    with conexao.cursor() as cursor:
        cursor.execute(
            "SELECT last_value FROM "
            "configuracoes_pesquisa_selecao_id_configuracao_selecao_seq"
        )
        sequencia_antes = cursor.fetchone()[0]
    try:
        repositorio.criar_ou_buscar_configuracao(configuracao)
        raise AssertionError("O nome repetido deveria ser recusado.")
    except ErroRepositorioPesquisaSelecao as erro:
        assert erro.codigo == "NOME_CONFIGURACAO_EXISTENTE"
    with conexao.cursor() as cursor:
        cursor.execute(
            "SELECT last_value FROM "
            "configuracoes_pesquisa_selecao_id_configuracao_selecao_seq"
        )
        sequencia_depois = cursor.fetchone()[0]
        cursor.execute("SELECT versao FROM schema_migrations WHERE versao='025'")
        assert cursor.fetchone() == ("025",)
    assert sequencia_antes == sequencia_depois
    print({
        "migracao": "025",
        "nome_repetido": "recusado",
        "sequencia_antes": sequencia_antes,
        "sequencia_depois": sequencia_depois,
    })
