"""Protege, aplica a 015 e cria os perfis atuais no database games."""

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
    atualizar_perfis_operacionais_atuais,
    marcar_perfis_operacionais_desatualizados,
)


PG_DUMP = Path(r"C:\Program Files\PostgreSQL\16\bin\pg_dump.exe")
PG_RESTORE = Path(r"C:\Program Files\PostgreSQL\16\bin\pg_restore.exe")
PASTA_BACKUPS = Path(__file__).resolve().parents[1] / "dados" / "backups"
MIGRACOES = Path(__file__).resolve().parents[2] / "database" / "migrations"


def _backup(configuracao):
    instante = datetime.now().strftime("%Y%m%d_%H%M%S")
    destino = PASTA_BACKUPS / f"games_pre_perfis_20_5a_{instante}.dump"
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
    for item in ("TABLE public resultados", "TABLE public criterios_validacao"):
        if item not in listagem:
            raise RuntimeError(f"O backup não contém {item}.")
    return destino, hashlib.sha256(destino.read_bytes()).hexdigest().upper(), len(listagem.splitlines())


def main() -> None:
    load_dotenv()
    if sys.argv[1:] != ["CONFIRMAR_GAMES_20_5A"]:
        raise SystemExit("Uso: aplicar_perfis_operacionais_games.py CONFIRMAR_GAMES_20_5A")
    configuracao = carregar_configuracao_banco()
    if configuracao.nome != "games":
        raise RuntimeError("A operação exige GAME_DB_NAME=games.")
    with abrir_conexao(configuracao) as conexao:
        with conexao.cursor() as cursor:
            cursor.execute("SELECT versao FROM schema_migrations ORDER BY versao")
            versoes = tuple(linha[0] for linha in cursor.fetchall())
            cursor.execute("SELECT count(*) FROM resultados")
            total_antes = cursor.fetchone()[0]
            cursor.execute("SELECT count(*) FROM avaliacoes_validacao")
            avaliacoes_antes = cursor.fetchone()[0]
    if versoes != tuple(f"{numero:03d}" for numero in range(1, 15)):
        raise RuntimeError(f"Migrações iniciais inesperadas: {versoes!r}")

    backup, sha256, itens = _backup(configuracao)
    migracoes = executar_migracoes(configuracao, MIGRACOES)
    if migracoes.aplicadas != ("015",):
        raise RuntimeError(f"Migração aplicada inesperada: {migracoes!r}")
    with abrir_conexao(configuracao) as conexao:
        marcar_perfis_operacionais_desatualizados(conexao)
        conexao.commit()
        relatorio = atualizar_perfis_operacionais_atuais(conexao)
        conexao.commit()
        with conexao.cursor() as cursor:
            cursor.execute(
                "SELECT categoria, count(*) FROM perfis_operacionais_atuais "
                "GROUP BY categoria ORDER BY categoria"
            )
            categorias = dict(cursor.fetchall())
            cursor.execute(
                "SELECT count(*) FROM perfis_operacionais_atuais "
                "WHERE quantidade_resultados = %s", (total_antes,)
            )
            perfis_completos = cursor.fetchone()[0]
            cursor.execute(
                "SELECT count(*) FROM padroes_subgrupo WHERE total_sorteios = %s",
                (total_antes,),
            )
            padroes_completos = cursor.fetchone()[0]
            cursor.execute(
                "SELECT quantidade_resultados, assinatura_conjunto_resultados, "
                "atualizado, motivo FROM estado_algoritmo_selecao"
            )
            estado = cursor.fetchone()
            cursor.execute("SELECT count(*) FROM avaliacoes_validacao")
            avaliacoes_depois = cursor.fetchone()[0]
    if categorias != {"ESTATISTICA": 4, "GEOMETRIA": 6}:
        raise RuntimeError(f"Categorias finais inesperadas: {categorias!r}")
    if perfis_completos != 10 or padroes_completos != 9:
        raise RuntimeError("Perfis ou incidências não cobrem o conjunto atual.")
    if avaliacoes_depois != avaliacoes_antes:
        raise RuntimeError("A atualização alterou avaliações de homologação.")
    if estado[0] != total_antes or estado[1] != relatorio.assinatura_conjunto_resultados:
        raise RuntimeError("O estado global não identifica o conjunto recalculado.")
    print(json.dumps({
        "backup": str(backup), "backup_bytes": backup.stat().st_size,
        "backup_sha256": sha256, "backup_itens_catalogo": itens,
        "migracao_aplicada": list(migracoes.aplicadas),
        "resultados": total_antes, "categorias": categorias,
        "perfis_completos": perfis_completos,
        "padroes_com_denominador_atual": padroes_completos,
        "avaliacoes_preservadas": avaliacoes_depois,
        "estado_algoritmo": estado,
    }, ensure_ascii=False, indent=2, default=list))


if __name__ == "__main__":
    main()
