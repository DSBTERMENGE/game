"""Executor ordenado, transacional e concorrente de migrações PostgreSQL."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
from pathlib import Path
import re

import psycopg

from msen.config import ConfiguracaoBanco

from .connection import abrir_conexao


PADRAO_MIGRACAO = re.compile(r"^(?P<versao>\d{3,})_(?P<nome>[a-z0-9_]+)\.sql$")
CHAVE_TRAVA_MIGRACOES = 4_607_189_431

SQL_CONTROLE = """
CREATE TABLE IF NOT EXISTS schema_migrations (
    versao VARCHAR(20) PRIMARY KEY,
    nome VARCHAR(200) NOT NULL,
    checksum_sha256 CHAR(64) NOT NULL,
    aplicada_em TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT ck_schema_migrations_versao_preenchida CHECK (BTRIM(versao) <> ''),
    CONSTRAINT ck_schema_migrations_nome_preenchido CHECK (BTRIM(nome) <> ''),
    CONSTRAINT ck_schema_migrations_checksum_sha256
        CHECK (checksum_sha256 ~ '^[0-9a-f]{64}$')
)
"""


class ErroMigracao(RuntimeError):
    def __init__(self, codigo: str, mensagem: str, *, versao: str | None = None) -> None:
        super().__init__(mensagem)
        self.codigo = codigo
        self.versao = versao


@dataclass(frozen=True, slots=True)
class Migracao:
    versao: str
    nome: str
    caminho: Path
    conteudo: str
    checksum_sha256: str


@dataclass(frozen=True, slots=True)
class RelatorioMigracoes:
    aplicadas: tuple[str, ...]
    ja_aplicadas: tuple[str, ...]


def _remover_transacao_explicita(conteudo: str, versao: str) -> str:
    """Remove o invólucro BEGIN/COMMIT para a transação ficar sob controle Python."""

    linhas = conteudo.splitlines()
    relevantes = [i for i, linha in enumerate(linhas) if linha.strip() and not linha.lstrip().startswith("--")]
    if not relevantes:
        raise ErroMigracao("MIGRACAO_VAZIA", "A migração não contém SQL.", versao=versao)
    primeiro, ultimo = relevantes[0], relevantes[-1]
    tem_begin = linhas[primeiro].strip().upper() == "BEGIN;"
    tem_commit = linhas[ultimo].strip().upper() == "COMMIT;"
    if tem_begin != tem_commit:
        raise ErroMigracao(
            "TRANSACAO_EXPLICITA_INCOMPLETA",
            "A migração possui controle transacional explícito incompleto.",
            versao=versao,
        )
    if tem_begin:
        linhas[primeiro] = ""
        linhas[ultimo] = ""
    return "\n".join(linhas)


def descobrir_migracoes(pasta: str | Path) -> tuple[Migracao, ...]:
    diretorio = Path(pasta)
    if not diretorio.is_dir():
        raise ErroMigracao("PASTA_NAO_ENCONTRADA", "A pasta de migrações não foi encontrada.")

    migracoes: list[Migracao] = []
    versoes: set[str] = set()
    for caminho in diretorio.iterdir():
        correspondencia = PADRAO_MIGRACAO.fullmatch(caminho.name)
        if not caminho.is_file() or correspondencia is None:
            continue
        versao = correspondencia.group("versao")
        if versao in versoes:
            raise ErroMigracao(
                "VERSAO_DUPLICADA", f"Existe mais de uma migração com a versão {versao}.",
                versao=versao,
            )
        conteudo_bytes = caminho.read_bytes()
        try:
            conteudo = conteudo_bytes.decode("utf-8")
        except UnicodeDecodeError:
            raise ErroMigracao(
                "CODIFICACAO_INVALIDA", "A migração deve usar UTF-8.", versao=versao,
            ) from None
        migracoes.append(Migracao(
            versao=versao,
            nome=correspondencia.group("nome"),
            caminho=caminho,
            conteudo=conteudo,
            checksum_sha256=hashlib.sha256(conteudo_bytes).hexdigest(),
        ))
        versoes.add(versao)
    return tuple(sorted(migracoes, key=lambda item: int(item.versao)))


def _carregar_aplicadas(conexao: psycopg.Connection) -> dict[str, str]:
    with conexao.cursor() as cursor:
        cursor.execute("SELECT versao, checksum_sha256 FROM schema_migrations")
        return {versao: checksum.strip() for versao, checksum in cursor.fetchall()}


def aplicar_migracoes(
    conexao: psycopg.Connection, pasta: str | Path
) -> RelatorioMigracoes:
    """Aplica migrações sob trava de sessão; cada arquivo e registro são atômicos."""

    migracoes = descobrir_migracoes(pasta)
    aplicadas_agora: list[str] = []
    existentes: list[str] = []
    trava_adquirida = False
    try:
        with conexao.cursor() as cursor:
            cursor.execute("SELECT pg_advisory_lock(%s)", (CHAVE_TRAVA_MIGRACOES,))
            trava_adquirida = True
        conexao.commit()

        with conexao.transaction():
            with conexao.cursor() as cursor:
                cursor.execute(SQL_CONTROLE)

        with conexao.transaction():
            registradas = _carregar_aplicadas(conexao)

        for migracao in migracoes:
            checksum_registrado = registradas.get(migracao.versao)
            if checksum_registrado is not None:
                if checksum_registrado != migracao.checksum_sha256:
                    raise ErroMigracao(
                        "CHECKSUM_DIVERGENTE",
                        f"A migração {migracao.versao} foi alterada após sua aplicação.",
                        versao=migracao.versao,
                    )
                existentes.append(migracao.versao)
                continue

            sql = _remover_transacao_explicita(migracao.conteudo, migracao.versao)
            try:
                with conexao.transaction():
                    with conexao.cursor() as cursor:
                        cursor.execute(sql, prepare=False)
                        cursor.execute(
                            "INSERT INTO schema_migrations "
                            "(versao, nome, checksum_sha256) VALUES (%s, %s, %s)",
                            (migracao.versao, migracao.nome, migracao.checksum_sha256),
                        )
            except psycopg.Error:
                raise ErroMigracao(
                    "MIGRACAO_FALHOU",
                    f"A migração {migracao.versao} falhou e foi revertida.",
                    versao=migracao.versao,
                ) from None
            aplicadas_agora.append(migracao.versao)
            registradas[migracao.versao] = migracao.checksum_sha256

        return RelatorioMigracoes(tuple(aplicadas_agora), tuple(existentes))
    finally:
        if trava_adquirida:
            conexao.rollback()
            try:
                with conexao.cursor() as cursor:
                    cursor.execute("SELECT pg_advisory_unlock(%s)", (CHAVE_TRAVA_MIGRACOES,))
                conexao.commit()
            except psycopg.Error:
                conexao.rollback()


def executar_migracoes(
    configuracao: ConfiguracaoBanco, pasta: str | Path
) -> RelatorioMigracoes:
    """Abre e fecha a conexão ao executar o controle de migrações."""

    with abrir_conexao(configuracao) as conexao:
        return aplicar_migracoes(conexao, pasta)
