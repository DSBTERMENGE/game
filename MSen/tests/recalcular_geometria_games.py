"""Cria backup, aplica a migração 007 e recalcula a geometria no games."""

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
from msen.services import recalcular_analises_geometricas


PG_DUMP = Path(r"C:\Program Files\PostgreSQL\16\bin\pg_dump.exe")
PG_RESTORE = Path(r"C:\Program Files\PostgreSQL\16\bin\pg_restore.exe")
PASTA_BACKUPS = Path(__file__).resolve().parents[1] / "dados" / "backups"
MIGRACOES = Path(__file__).resolve().parents[2] / "database" / "migrations"


def _criar_backup(configuracao) -> tuple[Path, str, int]:
    if not PG_DUMP.is_file() or not PG_RESTORE.is_file():
        raise FileNotFoundError("pg_dump ou pg_restore do PostgreSQL 16 não foi encontrado.")
    PASTA_BACKUPS.mkdir(parents=True, exist_ok=True)
    instante = datetime.now().strftime("%Y%m%d_%H%M%S")
    destino = PASTA_BACKUPS / f"games_pre_geometria_{instante}.dump"
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
        raise RuntimeError("O backup geométrico não foi criado corretamente.")
    listagem = subprocess.run(
        [str(PG_RESTORE), "--list", str(destino)],
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    if "TABLE public resultados" not in listagem:
        raise RuntimeError("O catálogo do backup não contém a tabela resultados.")
    sha256 = hashlib.sha256(destino.read_bytes()).hexdigest().upper()
    return destino, sha256, len(listagem.splitlines())


def executar() -> dict[str, object]:
    """Protege, migra e recalcula o histórico local autorizado.

    Returns:
        Identificação do backup, migração, totais e resumo das medidas.

    Regra:
        Recusa qualquer database diferente de `games` e qualquer estado inicial
        que não corresponda exatamente às migrações `001` a `006`.
    """

    configuracao = carregar_configuracao_banco()
    if configuracao.nome != "games":
        raise RuntimeError("A operação exige GAME_DB_NAME=games.")

    with abrir_conexao(configuracao) as conexao:
        with conexao.cursor() as cursor:
            cursor.execute("SELECT versao FROM schema_migrations ORDER BY versao")
            versoes_antes = tuple(linha[0] for linha in cursor.fetchall())
            cursor.execute("SELECT COUNT(*) FROM resultados")
            resultados_antes = cursor.fetchone()[0]
            cursor.execute("SELECT TO_REGCLASS('public.analise_geometrica_resultado')")
            tabela_antes = cursor.fetchone()[0]
    if versoes_antes != tuple(f"{numero:03d}" for numero in range(1, 7)):
        raise RuntimeError(f"Migrações iniciais inesperadas: {versoes_antes!r}")
    if resultados_antes != 3069 or tabela_antes is not None:
        raise RuntimeError("O estado inicial do games não é o esperado para a migração 007.")

    backup, sha256, itens_catalogo = _criar_backup(configuracao)
    migracoes = executar_migracoes(configuracao, MIGRACOES)
    if migracoes.aplicadas != ("007",):
        raise RuntimeError(f"A migração aplicada divergiu: {migracoes.aplicadas!r}")

    with abrir_conexao(configuracao) as conexao:
        relatorio = recalcular_analises_geometricas(conexao)
        with conexao.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM resultados")
            resultados_depois = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM analise_geometrica_resultado")
            analises = cursor.fetchone()[0]
            cursor.execute(
                "SELECT MIN(area_total), MAX(area_total), AVG(area_total), "
                "MIN(quantidade_regioes), MAX(quantidade_regioes), "
                "COUNT(*) FILTER (WHERE centro_gravidade_x IS NULL) "
                "FROM analise_geometrica_resultado"
            )
            resumo = cursor.fetchone()
            cursor.execute("SELECT versao FROM schema_migrations ORDER BY versao")
            versoes_depois = tuple(linha[0] for linha in cursor.fetchall())

    if resultados_depois != resultados_antes:
        raise RuntimeError("O recálculo alterou a quantidade de resultados.")
    if analises != resultados_depois or relatorio.resultados_analisados != resultados_depois:
        raise RuntimeError("A relação entre resultados e análises não ficou completa.")
    if versoes_depois != tuple(f"{numero:03d}" for numero in range(1, 8)):
        raise RuntimeError(f"Migrações finais inesperadas: {versoes_depois!r}")

    return {
        "backup": str(backup),
        "backup_bytes": backup.stat().st_size,
        "backup_sha256": sha256,
        "backup_itens_catalogo": itens_catalogo,
        "migracoes_aplicadas": list(migracoes.aplicadas),
        "migracoes_anteriores": list(migracoes.ja_aplicadas),
        "resultados": resultados_depois,
        "analises": analises,
        "area_minima": str(resumo[0]),
        "area_maxima": str(resumo[1]),
        "area_media": str(resumo[2]),
        "regioes_minimas": resumo[3],
        "regioes_maximas": resumo[4],
        "centros_nulos": resumo[5],
    }


def main() -> None:
    """Exige confirmação explícita antes de alterar o database local."""

    load_dotenv()
    if sys.argv[1:] != ["CONFIRMAR_GAMES"]:
        raise SystemExit("Uso: recalcular_geometria_games.py CONFIRMAR_GAMES")
    print(json.dumps(executar(), ensure_ascii=False))


if __name__ == "__main__":
    main()
