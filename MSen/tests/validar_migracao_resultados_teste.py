"""Valida a migração 038 em clone temporário, sem alterar o banco games."""

from dataclasses import replace
import os
from pathlib import Path
import subprocess
import tempfile

from dotenv import load_dotenv
import psycopg

from msen.config import carregar_configuracao_banco
from msen.database import executar_migracoes
from suporte_banco_integracao import conectar, criar_vazio, remover


RAIZ = Path(__file__).resolve().parents[2]
MIGRACOES = RAIZ / "database" / "migrations"
PG_DUMP = Path(r"C:\Program Files\PostgreSQL\16\bin\pg_dump.exe")
PG_RESTORE = Path(r"C:\Program Files\PostgreSQL\16\bin\pg_restore.exe")


def _existe_tabela(configuracao, nome: str) -> bool:
    with conectar(configuracao, nome) as conexao, conexao.cursor() as cursor:
        cursor.execute("SELECT to_regclass('public.resultados_teste')")
        return cursor.fetchone()[0] is not None


def main() -> None:
    load_dotenv()
    configuracao = carregar_configuracao_banco()
    if configuracao.nome != "games":
        raise RuntimeError("A validação exige GAME_DB_NAME=games.")
    if _existe_tabela(configuracao, configuracao.nome):
        raise RuntimeError("O banco real já possui resultados_teste.")

    nome_temporario = f"games_test_migracao_038_{os.getpid()}"
    ambiente = os.environ.copy()
    ambiente["PGPASSWORD"] = configuracao.senha
    criar_vazio(configuracao, nome_temporario)
    try:
        with tempfile.TemporaryDirectory() as pasta:
            backup = Path(pasta) / "clone.dump"
            subprocess.run([
                str(PG_DUMP), "--format=custom", "--no-owner", "--no-privileges",
                "--host", configuracao.host, "--port", str(configuracao.porta),
                "--username", configuracao.usuario, "--file", str(backup),
                configuracao.nome,
            ], check=True, env=ambiente)
            subprocess.run([
                str(PG_RESTORE), "--exit-on-error", "--no-owner", "--no-privileges",
                "--host", configuracao.host, "--port", str(configuracao.porta),
                "--username", configuracao.usuario, "--dbname", nome_temporario,
                str(backup),
            ], check=True, env=ambiente)

        temporaria = replace(configuracao, nome=nome_temporario)
        relatorio = executar_migracoes(temporaria, MIGRACOES)
        if relatorio.aplicadas != ("038",):
            raise RuntimeError(f"Migrações inesperadas: {relatorio.aplicadas!r}")

        with conectar(configuracao, nome_temporario) as conexao:
            with conexao.transaction(), conexao.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO resultados_teste "
                    "(res_01,res_02,res_03,res_04,res_05,res_06) "
                    "VALUES (50,1,20,15,5,40) RETURNING "
                    "res_01,res_02,res_03,res_04,res_05,res_06"
                )
                if cursor.fetchone() != (50, 1, 20, 15, 5, 40):
                    raise RuntimeError("A ordem inserida não foi preservada.")

            for valores in ((0, 2, 3, 4, 5, 6), (1, 1, 3, 4, 5, 6)):
                try:
                    with conexao.transaction(), conexao.cursor() as cursor:
                        cursor.execute(
                            "INSERT INTO resultados_teste "
                            "(res_01,res_02,res_03,res_04,res_05,res_06) "
                            "VALUES (%s,%s,%s,%s,%s,%s)", valores,
                        )
                except psycopg.errors.CheckViolation:
                    continue
                raise RuntimeError(f"Linha inválida aceita: {valores!r}")

        if _existe_tabela(configuracao, configuracao.nome):
            raise RuntimeError("O banco real foi alterado durante a validação.")
        print("Migração 038 validada em clone temporário; banco games preservado.")
    finally:
        remover(configuracao, nome_temporario)


if __name__ == "__main__":
    main()
