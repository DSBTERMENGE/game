"""Criação e verificação de conexões PostgreSQL sem expor credenciais."""

from dataclasses import dataclass
from typing import Any, Callable

import psycopg

from msen.config import ConfiguracaoBanco


class ErroConexaoBanco(ConnectionError):
    """Falha segura ao conectar ou consultar o PostgreSQL."""

    def __init__(self, codigo: str, mensagem: str) -> None:
        super().__init__(mensagem)
        self.codigo = codigo


@dataclass(frozen=True, slots=True)
class InformacaoConexao:
    banco: str
    usuario: str
    versao_servidor: int


def abrir_conexao(
    configuracao: ConfiguracaoBanco,
    *,
    conector: Callable[..., Any] = psycopg.connect,
) -> Any:
    """Abre uma conexão usando argumentos separados, nunca uma URL com senha."""

    if not isinstance(configuracao, ConfiguracaoBanco):
        raise TypeError("A conexão exige uma ConfiguracaoBanco validada.")
    try:
        return conector(
            host=configuracao.host,
            port=configuracao.porta,
            dbname=configuracao.nome,
            user=configuracao.usuario,
            password=configuracao.senha,
            sslmode=configuracao.sslmode,
            connect_timeout=configuracao.tempo_limite,
        )
    except psycopg.Error:
        raise ErroConexaoBanco(
            "FALHA_CONEXAO",
            "Não foi possível conectar ao PostgreSQL. Confira servidor, porta, banco e usuário.",
        ) from None


def verificar_conexao(configuracao: ConfiguracaoBanco) -> InformacaoConexao:
    """Abre, consulta metadados não secretos e sempre fecha a conexão."""

    try:
        with abrir_conexao(configuracao) as conexao:
            with conexao.cursor() as cursor:
                cursor.execute(
                    "SELECT current_database(), current_user, "
                    "current_setting('server_version_num')::integer"
                )
                banco, usuario, versao = cursor.fetchone()
                return InformacaoConexao(banco, usuario, versao)
    except ErroConexaoBanco:
        raise
    except psycopg.Error:
        raise ErroConexaoBanco(
            "FALHA_VERIFICACAO",
            "A conexão foi aberta, mas não pôde ser verificada.",
        ) from None
