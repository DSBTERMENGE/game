"""Protege e aplica somente a migração 038 no banco games."""

from datetime import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

from dotenv import load_dotenv

from msen.config import carregar_configuracao_banco
from msen.database import abrir_conexao, executar_migracoes


RAIZ = Path(__file__).resolve().parents[2]
MIGRACOES = RAIZ / "database" / "migrations"
PASTA_BACKUPS = RAIZ / "MSen" / "dados" / "backups"
PG_DUMP = Path(r"C:\Program Files\PostgreSQL\16\bin\pg_dump.exe")
PG_RESTORE = Path(r"C:\Program Files\PostgreSQL\16\bin\pg_restore.exe")


def _estado(configuracao) -> dict[str, object]:
    with abrir_conexao(configuracao) as conexao, conexao.cursor() as cursor:
        cursor.execute("SELECT max(versao) FROM schema_migrations")
        versao = cursor.fetchone()[0]
        cursor.execute("SELECT to_regclass('public.resultados_teste')")
        tabela = cursor.fetchone()[0]
        quantidade = None
        colunas: tuple[str, ...] = ()
        if tabela is not None:
            cursor.execute("SELECT count(*) FROM resultados_teste")
            quantidade = cursor.fetchone()[0]
            cursor.execute(
                "SELECT column_name FROM information_schema.columns "
                "WHERE table_schema='public' AND table_name='resultados_teste' "
                "ORDER BY ordinal_position"
            )
            colunas = tuple(item[0] for item in cursor.fetchall())
    return {
        "versao": versao,
        "tabela": tabela,
        "quantidade": quantidade,
        "colunas": colunas,
    }


def _backup(configuracao) -> tuple[Path, str, int]:
    if not PG_DUMP.is_file() or not PG_RESTORE.is_file():
        raise FileNotFoundError("pg_dump ou pg_restore não encontrado.")
    PASTA_BACKUPS.mkdir(parents=True, exist_ok=True)
    instante = datetime.now().strftime("%Y%m%d_%H%M%S")
    destino = PASTA_BACKUPS / f"games_pre_resultados_teste_13_1_7_{instante}.dump"
    ambiente = os.environ.copy()
    ambiente["PGPASSWORD"] = configuracao.senha
    subprocess.run([
        str(PG_DUMP), "--format=custom", "--no-owner", "--no-privileges",
        "--host", configuracao.host, "--port", str(configuracao.porta),
        "--username", configuracao.usuario, "--file", str(destino),
        configuracao.nome,
    ], check=True, env=ambiente)
    catalogo = subprocess.run(
        [str(PG_RESTORE), "--list", str(destino)],
        check=True, capture_output=True, text=True,
    ).stdout
    for tabela in ("resultados", "padroes_grupo", "padroes_subgrupo"):
        if f"TABLE public {tabela}" not in catalogo:
            raise RuntimeError(f"O backup não contém a tabela {tabela}.")
    return (
        destino,
        hashlib.sha256(destino.read_bytes()).hexdigest().upper(),
        len(catalogo.splitlines()),
    )


def main() -> None:
    load_dotenv()
    if sys.argv[1:] != ["CONFIRMAR_RESULTADOS_TESTE_13_1_7"]:
        raise SystemExit(
            "Uso: aplicar_migracao_resultados_teste_games.py "
            "CONFIRMAR_RESULTADOS_TESTE_13_1_7"
        )
    configuracao = carregar_configuracao_banco()
    if configuracao.nome != "games":
        raise RuntimeError("A operação exige GAME_DB_NAME=games.")

    antes = _estado(configuracao)
    if antes != {
        "versao": "037", "tabela": None, "quantidade": None, "colunas": ()
    }:
        raise RuntimeError(f"Estado inicial inesperado: {antes!r}")

    backup, sha256, itens = _backup(configuracao)
    relatorio = executar_migracoes(configuracao, MIGRACOES)
    if relatorio.aplicadas != ("038",):
        raise RuntimeError(f"Migrações aplicadas inesperadas: {relatorio.aplicadas!r}")
    repeticao = executar_migracoes(configuracao, MIGRACOES)
    if repeticao.aplicadas:
        raise RuntimeError("A segunda execução não foi idempotente.")

    depois = _estado(configuracao)
    esperado = {
        "versao": "038",
        "tabela": "resultados_teste",
        "quantidade": 0,
        "colunas": (
            "id_resultado_teste", "res_01", "res_02", "res_03",
            "res_04", "res_05", "res_06",
        ),
    }
    if depois != esperado:
        raise RuntimeError(f"Estado final inesperado: {depois!r}")

    print(json.dumps({
        "backup": str(backup),
        "backup_bytes": backup.stat().st_size,
        "backup_sha256": sha256,
        "backup_itens_catalogo": itens,
        "migracao_aplicada": relatorio.aplicadas,
        "segunda_execucao_idempotente": True,
        "estado_final": depois,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
