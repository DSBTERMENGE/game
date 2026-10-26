"""Configuração da aplicação obtida exclusivamente do ambiente."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
import os


class ErroConfiguracaoBanco(ValueError):
    """Configuração do PostgreSQL ausente ou inválida."""

    def __init__(self, codigo: str, mensagem: str, *, variavel: str) -> None:
        super().__init__(mensagem)
        self.codigo = codigo
        self.variavel = variavel


@dataclass(frozen=True, slots=True)
class ConfiguracaoBanco:
    host: str
    porta: int
    nome: str
    usuario: str
    senha: str
    sslmode: str = "prefer"
    tempo_limite: int = 5

    def __repr__(self) -> str:
        return (
            "ConfiguracaoBanco("
            f"host={self.host!r}, porta={self.porta!r}, nome={self.nome!r}, "
            f"usuario={self.usuario!r}, senha='***', sslmode={self.sslmode!r}, "
            f"tempo_limite={self.tempo_limite!r})"
        )


def _obrigatoria(ambiente: Mapping[str, str], nome: str) -> str:
    valor = ambiente.get(nome, "").strip()
    if not valor:
        raise ErroConfiguracaoBanco(
            "VARIAVEL_OBRIGATORIA_AUSENTE",
            f"A variável de ambiente {nome} é obrigatória.",
            variavel=nome,
        )
    return valor


def _inteiro(
    ambiente: Mapping[str, str], nome: str, padrao: str, minimo: int, maximo: int
) -> int:
    texto = ambiente.get(nome, padrao).strip()
    try:
        valor = int(texto)
    except ValueError:
        valor = -1
    if not minimo <= valor <= maximo:
        raise ErroConfiguracaoBanco(
            "VARIAVEL_INTEIRA_INVALIDA",
            f"A variável de ambiente {nome} possui valor inválido.",
            variavel=nome,
        )
    return valor


def carregar_configuracao_banco(
    ambiente: Mapping[str, str] | None = None,
) -> ConfiguracaoBanco:
    """Valida `GAME_DB_*` sem carregar arquivos ou aplicar senhas implícitas."""

    fonte = os.environ if ambiente is None else ambiente
    sslmode = fonte.get("GAME_DB_SSLMODE", "prefer").strip().lower()
    modos_ssl = {"disable", "allow", "prefer", "require", "verify-ca", "verify-full"}
    if sslmode not in modos_ssl:
        raise ErroConfiguracaoBanco(
            "SSLMODE_INVALIDO",
            "A variável GAME_DB_SSLMODE possui valor inválido.",
            variavel="GAME_DB_SSLMODE",
        )

    return ConfiguracaoBanco(
        host=_obrigatoria(fonte, "GAME_DB_HOST"),
        porta=_inteiro(fonte, "GAME_DB_PORT", "5432", 1, 65535),
        nome=_obrigatoria(fonte, "GAME_DB_NAME"),
        usuario=_obrigatoria(fonte, "GAME_DB_USER"),
        senha=_obrigatoria(fonte, "GAME_DB_PASSWORD"),
        sslmode=sslmode,
        tempo_limite=_inteiro(fonte, "GAME_DB_CONNECT_TIMEOUT", "5", 1, 60),
    )
