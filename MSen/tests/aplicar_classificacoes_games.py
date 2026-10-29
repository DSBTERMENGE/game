"""Protege, migra e classifica PG_001 no database local games."""

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
from msen.services import (
    calcular_perfil_grupo_sequenciais,
    recalcular_classificacoes_grupo_sequenciais,
)


PG_DUMP = Path(r"C:\Program Files\PostgreSQL\16\bin\pg_dump.exe")
PG_RESTORE = Path(r"C:\Program Files\PostgreSQL\16\bin\pg_restore.exe")
PASTA_BACKUPS = Path(__file__).resolve().parents[1] / "dados" / "backups"
MIGRACOES = Path(__file__).resolve().parents[2] / "database" / "migrations"


def _criar_backup(configuracao) -> tuple[Path, str, int]:
    """Cria dump customizado, valida seu catálogo e calcula SHA-256."""
    if not PG_DUMP.is_file() or not PG_RESTORE.is_file():
        raise FileNotFoundError("pg_dump ou pg_restore do PostgreSQL 16 não foi encontrado.")
    PASTA_BACKUPS.mkdir(parents=True, exist_ok=True)
    instante = datetime.now().strftime("%Y%m%d_%H%M%S")
    destino = PASTA_BACKUPS / f"games_pre_classificacao_{instante}.dump"
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
        raise RuntimeError("O backup da classificação não foi criado corretamente.")
    listagem = subprocess.run(
        [str(PG_RESTORE), "--list", str(destino)],
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    for item in ("TABLE public resultados", "TABLE public padroes_subgrupo"):
        if item not in listagem:
            raise RuntimeError(f"O catálogo do backup não contém {item}.")
    sha256 = hashlib.sha256(destino.read_bytes()).hexdigest().upper()
    return destino, sha256, len(listagem.splitlines())


def _estado_inicial(configuracao) -> dict[str, object]:
    """Lê e valida o estado exato autorizado antes do backup e da migração."""
    with abrir_conexao(configuracao) as conexao:
        with conexao.cursor() as cursor:
            cursor.execute("SELECT versao FROM schema_migrations ORDER BY versao")
            versoes = tuple(linha[0] for linha in cursor.fetchall())
            cursor.execute("SELECT count(*) FROM resultados")
            resultados = cursor.fetchone()[0]
            cursor.execute("SELECT count(*) FROM frequencia_de_resultado")
            frequencias = cursor.fetchone()[0]
            cursor.execute("SELECT count(*) FROM analise_geometrica_resultado")
            analises = cursor.fetchone()[0]
            cursor.execute("SELECT to_regclass('public.resultado_classificacao_padrao')")
            classificacoes = cursor.fetchone()[0]
    esperado = tuple(f"{numero:03d}" for numero in range(1, 8))
    if versoes != esperado:
        raise RuntimeError(f"Migrações iniciais inesperadas: {versoes!r}")
    if (resultados, frequencias, analises, classificacoes) != (3069, 60, 3069, None):
        raise RuntimeError(
            "Estado inicial inesperado: "
            f"resultados={resultados}, frequências={frequencias}, "
            f"análises={analises}, classificações={classificacoes!r}."
        )
    return {
        "migracoes": list(versoes),
        "resultados": resultados,
        "frequencias": frequencias,
        "analises": analises,
    }


def executar() -> dict[str, object]:
    """Cria backup, aplica somente 008, recalcula e audita o estado final."""
    configuracao = carregar_configuracao_banco()
    if configuracao.nome != "games":
        raise RuntimeError("A operação exige GAME_DB_NAME=games.")
    antes = _estado_inicial(configuracao)
    backup, sha256, itens_catalogo = _criar_backup(configuracao)
    migracoes = executar_migracoes(configuracao, MIGRACOES)
    if migracoes.aplicadas != ("008",):
        raise RuntimeError(f"A migração aplicada divergiu: {migracoes.aplicadas!r}")

    with abrir_conexao(configuracao) as conexao:
        primeiro = recalcular_classificacoes_grupo_sequenciais(conexao)
        with conexao.cursor() as cursor:
            cursor.execute(
                "SELECT id_resultado, id_classificacao "
                "FROM resultado_classificacao_padrao ORDER BY id_resultado"
            )
            identidades_primeiro = tuple(cursor.fetchall())
        segundo = recalcular_classificacoes_grupo_sequenciais(conexao)
        with conexao.cursor() as cursor:
            cursor.execute(
                "SELECT id_resultado, id_classificacao "
                "FROM resultado_classificacao_padrao ORDER BY id_resultado"
            )
            identidades_segundo = tuple(cursor.fetchall())
        if identidades_primeiro != identidades_segundo:
            raise RuntimeError("O segundo recálculo alterou identidades.")

        perfil = calcular_perfil_grupo_sequenciais(
            conexao, limite_raridade_percentual=10
        )
        contagens = {item.padrao_cod: item.quantidade for item in perfil.classes}
        with conexao.cursor() as cursor:
            cursor.execute("SELECT versao FROM schema_migrations ORDER BY versao")
            versoes_depois = tuple(linha[0] for linha in cursor.fetchall())
            cursor.execute("SELECT count(*) FROM resultados")
            resultados_depois = cursor.fetchone()[0]
            cursor.execute("SELECT count(*) FROM frequencia_de_resultado")
            frequencias_depois = cursor.fetchone()[0]
            cursor.execute("SELECT count(*) FROM analise_geometrica_resultado")
            analises_depois = cursor.fetchone()[0]
            cursor.execute("SELECT count(*) FROM resultado_classificacao_padrao")
            classificacoes = cursor.fetchone()[0]
            cursor.execute(
                "SELECT padrao_cod, num_oco FROM padroes_subgrupo "
                "WHERE padrao_cod IN ('PD_001', 'PD_002', 'PD_003') "
                "ORDER BY padrao_cod"
            )
            catalogo = tuple(cursor.fetchall())

    esperado_versoes = tuple(f"{numero:03d}" for numero in range(1, 11))
    esperado_contagens = {
        "PD_001": 1192,
        "PD_002": 92,
        "PD_003": 5,
    }
    if versoes_depois != esperado_versoes:
        raise RuntimeError(f"Migrações finais inesperadas: {versoes_depois!r}")
    if (resultados_depois, frequencias_depois, analises_depois, classificacoes) != (
        3069, 60, 3069, 1289
    ):
        raise RuntimeError("Os totais finais não reconciliaram.")
    if contagens != esperado_contagens:
        raise RuntimeError(f"Contagens finais inesperadas: {contagens!r}")
    if catalogo != (("PD_001", 1192), ("PD_002", 92), ("PD_003", 5)):
        raise RuntimeError(f"Catálogo final inesperado: {catalogo!r}")
    if perfil.padroes_raros != ("PD_002", "PD_003"):
        raise RuntimeError(f"Indicação de raridade inesperada: {perfil.padroes_raros!r}")

    return {
        "backup": str(backup),
        "backup_bytes": backup.stat().st_size,
        "backup_sha256": sha256,
        "backup_itens_catalogo": itens_catalogo,
        "estado_antes": antes,
        "migracoes_aplicadas": list(migracoes.aplicadas),
        "resultados": resultados_depois,
        "frequencias": frequencias_depois,
        "analises_geometricas": analises_depois,
        "classificacoes": classificacoes,
        "contagens": contagens,
        "padroes_indicados": list(perfil.padroes_raros),
        "recalculo_idempotente": primeiro.contagens == segundo.contagens,
    }


def main() -> None:
    """Exige confirmação explícita antes de alterar o database local."""
    load_dotenv()
    if sys.argv[1:] != ["CONFIRMAR_GAMES"]:
        raise SystemExit("Uso: aplicar_classificacoes_games.py CONFIRMAR_GAMES")
    print(json.dumps(executar(), ensure_ascii=False))


if __name__ == "__main__":
    main()
