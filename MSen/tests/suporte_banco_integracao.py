"""Cria e remove exclusivamente databases efêmeros dos testes integrados."""

from dataclasses import replace
import json
import os
from pathlib import Path
import re
import subprocess
import sys

from dotenv import load_dotenv
import psycopg
from psycopg import sql

from msen.config import ConfiguracaoBanco, carregar_configuracao_banco
from msen.database import executar_migracoes


PADRAO_NOME = re.compile(r"games_test_7_1_[0-9]+")
MIGRACOES = Path(__file__).resolve().parents[2] / "database" / "migrations"
BACKUP = (
    Path(__file__).resolve().parents[1]
    / "dados"
    / "backups"
    / "games_pos_importacao_20261026.dump"
)
PG_RESTORE = Path(r"C:\Program Files\PostgreSQL\16\bin\pg_restore.exe")


def validar_nome(nome: str) -> str:
    if PADRAO_NOME.fullmatch(nome) is None:
        raise ValueError("Nome de database temporário fora do padrão permitido.")
    return nome


def conectar(configuracao: ConfiguracaoBanco, nome: str, *, autocommit=False):
    return psycopg.connect(
        host=configuracao.host,
        port=configuracao.porta,
        dbname=nome,
        user=configuracao.usuario,
        password=configuracao.senha,
        sslmode=configuracao.sslmode,
        connect_timeout=configuracao.tempo_limite,
        autocommit=autocommit,
    )


def remover(configuracao: ConfiguracaoBanco, nome: str) -> None:
    with conectar(configuracao, "postgres", autocommit=True) as conexao:
        with conexao.cursor() as cursor:
            cursor.execute(
                "SELECT pg_terminate_backend(pid) FROM pg_stat_activity "
                "WHERE datname = %s AND pid <> pg_backend_pid()",
                (nome,),
            )
            cursor.execute(sql.SQL("DROP DATABASE IF EXISTS {}").format(sql.Identifier(nome)))


def criar_vazio(configuracao: ConfiguracaoBanco, nome: str) -> None:
    with conectar(configuracao, "postgres", autocommit=True) as conexao:
        with conexao.cursor() as cursor:
            cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (nome,))
            if cursor.fetchone() is not None:
                raise RuntimeError("O database temporário já existe.")
            cursor.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(nome)))


def criar(configuracao: ConfiguracaoBanco, nome: str) -> None:
    criar_vazio(configuracao, nome)
    try:
        executar_migracoes(replace(configuracao, nome=nome), MIGRACOES)
    except Exception:
        remover(configuracao, nome)
        raise


def resumo(configuracao: ConfiguracaoBanco, nome: str) -> dict[str, int]:
    with conectar(configuracao, nome) as conexao:
        with conexao.cursor() as cursor:
            cursor.execute("SELECT count(*) FROM resultados")
            resultados = cursor.fetchone()[0]
            cursor.execute("SELECT count(*), sum(num_oco) FROM frequencia_de_resultado")
            frequencias, ocorrencias = cursor.fetchone()
    return {
        "resultados": resultados,
        "frequencias": frequencias,
        "ocorrencias": ocorrencias,
    }


def listar_temporarios(configuracao: ConfiguracaoBanco) -> tuple[str, ...]:
    with conectar(configuracao, "postgres") as conexao:
        with conexao.cursor() as cursor:
            cursor.execute(
                "SELECT datname FROM pg_database "
                "WHERE datname LIKE 'games_test_7_1_%' ORDER BY datname"
            )
            return tuple(linha[0] for linha in cursor.fetchall())


def ensaiar_restauracao(configuracao: ConfiguracaoBanco, nome: str) -> dict[str, int]:
    if not BACKUP.is_file():
        raise FileNotFoundError(f"Backup não encontrado: {BACKUP}")
    if not PG_RESTORE.is_file():
        raise FileNotFoundError(f"pg_restore não encontrado: {PG_RESTORE}")

    criar_vazio(configuracao, nome)
    try:
        ambiente = os.environ.copy()
        ambiente["PGPASSWORD"] = configuracao.senha
        subprocess.run(
            [
                str(PG_RESTORE),
                "--exit-on-error",
                "--no-owner",
                "--no-privileges",
                "--host",
                configuracao.host,
                "--port",
                str(configuracao.porta),
                "--username",
                configuracao.usuario,
                "--dbname",
                nome,
                str(BACKUP),
            ],
            check=True,
            env=ambiente,
        )
        return resumo(configuracao, nome)
    finally:
        remover(configuracao, nome)


def main() -> None:
    load_dotenv()
    configuracao = carregar_configuracao_banco()
    if len(sys.argv) == 2 and sys.argv[1] == "listar":
        print(json.dumps(listar_temporarios(configuracao)))
        return
    if len(sys.argv) != 3 or sys.argv[1] not in {
        "criar",
        "remover",
        "resumo",
        "restaurar",
    }:
        raise SystemExit(
            "Uso: suporte_banco_integracao.py listar | "
            "criar|remover|resumo|restaurar NOME"
        )
    operacao, nome = sys.argv[1], validar_nome(sys.argv[2])
    if operacao == "criar":
        criar(configuracao, nome)
    elif operacao == "remover":
        remover(configuracao, nome)
    elif operacao == "restaurar":
        print(json.dumps(ensaiar_restauracao(configuracao, nome)))
    else:
        print(json.dumps(resumo(configuracao, nome)))


if __name__ == "__main__":
    main()
