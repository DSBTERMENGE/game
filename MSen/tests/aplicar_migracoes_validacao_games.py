"""Protege e aplica exclusivamente as migrações 011–013 ao database games."""

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
VERSOES_ANTERIORES = tuple(f"{numero:03d}" for numero in range(1, 11))
VERSOES_FINAIS = tuple(f"{numero:03d}" for numero in range(1, 14))


def _estado(configuracao) -> dict[str, object]:
    with abrir_conexao(configuracao) as conexao:
        with conexao.cursor() as cursor:
            cursor.execute("SELECT versao FROM schema_migrations ORDER BY versao")
            versoes = tuple(linha[0] for linha in cursor.fetchall())
            cursor.execute("SELECT count(*) FROM resultados")
            resultados = cursor.fetchone()[0]
            cursor.execute("SELECT count(*) FROM padroes_grupo")
            grupos = cursor.fetchone()[0]
            cursor.execute("SELECT count(*) FROM padroes_subgrupo")
            subgrupos = cursor.fetchone()[0]
            cursor.execute("SELECT count(*) FROM resultado_classificacao_padrao")
            classificacoes = cursor.fetchone()[0]
    return {
        "versoes": versoes,
        "resultados": resultados,
        "grupos": grupos,
        "subgrupos": subgrupos,
        "classificacoes": classificacoes,
    }


def _criar_backup(configuracao) -> tuple[Path, str, int]:
    if not PG_DUMP.is_file() or not PG_RESTORE.is_file():
        raise FileNotFoundError("pg_dump ou pg_restore do PostgreSQL 16 não encontrado.")
    PASTA_BACKUPS.mkdir(parents=True, exist_ok=True)
    instante = datetime.now().strftime("%Y%m%d_%H%M%S")
    destino = PASTA_BACKUPS / f"games_pre_validacao_20_3_{instante}.dump"
    ambiente = os.environ.copy()
    ambiente["PGPASSWORD"] = configuracao.senha
    subprocess.run(
        [
            str(PG_DUMP), "--format=custom", "--no-owner", "--no-privileges",
            "--host", configuracao.host, "--port", str(configuracao.porta),
            "--username", configuracao.usuario, "--file", str(destino),
            configuracao.nome,
        ],
        check=True,
        env=ambiente,
    )
    if not destino.is_file() or destino.stat().st_size == 0:
        raise RuntimeError("O backup anterior à subetapa 20.3 não foi criado.")
    listagem = subprocess.run(
        [str(PG_RESTORE), "--list", str(destino)],
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    for item in (
        "TABLE public resultados",
        "TABLE public padroes_grupo",
        "TABLE public schema_migrations",
    ):
        if item not in listagem:
            raise RuntimeError(f"O catálogo do backup não contém {item}.")
    sha256 = hashlib.sha256(destino.read_bytes()).hexdigest().upper()
    return destino, sha256, len(listagem.splitlines())


def _auditar_novas_tabelas(configuracao) -> dict[str, object]:
    with abrir_conexao(configuracao) as conexao:
        with conexao.cursor() as cursor:
            cursor.execute("SELECT count(*) FROM amostras_validacao")
            amostras = cursor.fetchone()[0]
            cursor.execute("SELECT count(*) FROM criterios_validacao")
            criterios = cursor.fetchone()[0]
            cursor.execute("SELECT count(*) FROM avaliacoes_validacao")
            avaliacoes = cursor.fetchone()[0]
            cursor.execute(
                "SELECT id_estado, atualizado, motivo, quantidade_resultados "
                "FROM estado_algoritmo_selecao"
            )
            estado = cursor.fetchall()
    esperado = [(1, False, "AGUARDANDO_HOMOLOGACAO_INICIAL", 0)]
    if (amostras, criterios, avaliacoes) != (0, 0, 0) or estado != esperado:
        raise RuntimeError(
            "O estado inicial das tabelas de validação divergiu do contrato."
        )
    return {
        "amostras": amostras,
        "criterios": criterios,
        "avaliacoes": avaliacoes,
        "estado_algoritmo": estado[0],
    }


def main() -> None:
    load_dotenv()
    if sys.argv[1:] != ["CONFIRMAR_GAMES_20_3"]:
        raise SystemExit(
            "Uso: aplicar_migracoes_validacao_games.py CONFIRMAR_GAMES_20_3"
        )
    configuracao = carregar_configuracao_banco()
    if configuracao.nome != "games":
        raise RuntimeError("A operação exige GAME_DB_NAME=games.")

    antes = _estado(configuracao)
    if antes["versoes"] != VERSOES_ANTERIORES:
        raise RuntimeError(f"Migrações iniciais inesperadas: {antes['versoes']!r}")

    backup, sha256, itens_catalogo = _criar_backup(configuracao)
    primeira = executar_migracoes(configuracao, MIGRACOES)
    if primeira.aplicadas != ("011", "012", "013"):
        raise RuntimeError(f"Migrações aplicadas divergiram: {primeira!r}")
    segunda = executar_migracoes(configuracao, MIGRACOES)
    if segunda.aplicadas or segunda.ja_aplicadas != VERSOES_FINAIS:
        raise RuntimeError(f"Repetição não idempotente: {segunda!r}")

    depois = _estado(configuracao)
    if depois["versoes"] != VERSOES_FINAIS:
        raise RuntimeError(f"Migrações finais inesperadas: {depois['versoes']!r}")
    for campo in ("resultados", "grupos", "subgrupos", "classificacoes"):
        if depois[campo] != antes[campo]:
            raise RuntimeError(f"A migração alterou o total preexistente: {campo}.")

    print(json.dumps({
        "backup": str(backup),
        "backup_bytes": backup.stat().st_size,
        "backup_sha256": sha256,
        "backup_itens_catalogo": itens_catalogo,
        "estado_antes": antes,
        "migracoes_aplicadas": list(primeira.aplicadas),
        "migracoes_na_repeticao": list(segunda.aplicadas),
        "estado_depois": depois,
        "novas_tabelas": _auditar_novas_tabelas(configuracao),
    }, ensure_ascii=False, indent=2, default=list))


if __name__ == "__main__":
    main()
