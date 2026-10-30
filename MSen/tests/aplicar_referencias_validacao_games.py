"""Protege e aplica a estrutura de referências independentes ao games."""

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


PG_DUMP = Path(r"C:\Program Files\PostgreSQL\16\bin\pg_dump.exe")
PG_RESTORE = Path(r"C:\Program Files\PostgreSQL\16\bin\pg_restore.exe")
PASTA_BACKUPS = Path(__file__).resolve().parents[1] / "dados" / "backups"
MIGRACOES = Path(__file__).resolve().parents[2] / "database" / "migrations"


def _backup(configuracao):
    instante = datetime.now().strftime("%Y%m%d_%H%M%S")
    destino = PASTA_BACKUPS / f"games_pre_referencias_20_7_{instante}.dump"
    ambiente = os.environ.copy()
    ambiente["PGPASSWORD"] = configuracao.senha
    subprocess.run([
        str(PG_DUMP), "--format=custom", "--no-owner", "--no-privileges",
        "--host", configuracao.host, "--port", str(configuracao.porta),
        "--username", configuracao.usuario, "--file", str(destino),
        configuracao.nome,
    ], check=True, env=ambiente)
    listagem = subprocess.run(
        [str(PG_RESTORE), "--list", str(destino)], check=True,
        capture_output=True, text=True,
    ).stdout
    for item in ("TABLE public avaliacoes_validacao", "TABLE public resultados"):
        if item not in listagem:
            raise RuntimeError(f"O backup não contém {item}.")
    return destino, hashlib.sha256(destino.read_bytes()).hexdigest().upper(), len(listagem.splitlines())


def _resumo(conexao):
    with conexao.cursor() as cursor:
        cursor.execute("SELECT count(*) FROM avaliacoes_validacao")
        total = cursor.fetchone()[0]
        cursor.execute(
            "SELECT count(*) FROM avaliacoes_validacao WHERE referencia_conferida"
        )
        conferidas = cursor.fetchone()[0]
        cursor.execute(
            "SELECT count(*) FROM avaliacoes_validacao WHERE valor_esperado IS NOT NULL "
            "OR id_padrao_esperado IS NOT NULL OR estado_padrao_esperado IS NOT NULL"
        )
        preenchidas = cursor.fetchone()[0]
    return total, conferidas, preenchidas


def main() -> None:
    load_dotenv()
    if sys.argv[1:] != ["CONFIRMAR_GAMES_20_7"]:
        raise SystemExit("Uso: aplicar_referencias_validacao_games.py CONFIRMAR_GAMES_20_7")
    configuracao = carregar_configuracao_banco()
    if configuracao.nome != "games":
        raise RuntimeError("A operação exige GAME_DB_NAME=games.")
    with abrir_conexao(configuracao) as conexao:
        with conexao.cursor() as cursor:
            cursor.execute("SELECT versao FROM schema_migrations ORDER BY versao")
            versoes = tuple(linha[0] for linha in cursor.fetchall())
        antes = _resumo(conexao)
    if versoes != tuple(f"{numero:03d}" for numero in range(1, 16)):
        raise RuntimeError(f"Migrações iniciais inesperadas: {versoes!r}")
    if antes != (3800, 0, 0):
        raise RuntimeError(f"Avaliações iniciais inesperadas: {antes!r}")

    backup, sha256, itens = _backup(configuracao)
    migracoes = executar_migracoes(configuracao, MIGRACOES)
    repeticao = executar_migracoes(configuracao, MIGRACOES)
    if migracoes.aplicadas != ("016",) or repeticao.aplicadas:
        raise RuntimeError("A aplicação da migração 016 não foi idempotente.")
    with abrir_conexao(configuracao) as conexao:
        depois = _resumo(conexao)
        with conexao.cursor() as cursor:
            cursor.execute(
                "SELECT count(*) FROM information_schema.columns WHERE "
                "table_schema = 'public' AND table_name = 'avaliacoes_validacao' "
                "AND column_name IN ('estado_valor_esperado', 'estado_valor_calculado', "
                "'referencia_origem', 'referencia_revisor', "
                "'referencia_observacao', 'referencia_conferida_em')"
            )
            colunas = cursor.fetchone()[0]
    if depois != antes or colunas != 6:
        raise RuntimeError("A migração alterou avaliações ou não criou todas as colunas.")
    print(json.dumps({
        "backup": str(backup), "backup_bytes": backup.stat().st_size,
        "backup_sha256": sha256, "backup_itens_catalogo": itens,
        "migracao_aplicada": list(migracoes.aplicadas),
        "avaliacoes_antes": antes, "avaliacoes_depois": depois,
        "colunas_novas": colunas, "repeticao_idempotente": True,
    }, ensure_ascii=False, indent=2, default=list))


if __name__ == "__main__":
    main()
