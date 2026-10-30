"""Protege, aplica a 014 e sincroniza o registro da subetapa 20.5 no games."""

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
from msen.services import sincronizar_criterios_validacao
from msen.validacao import criar_registro_criterios_producao


PG_DUMP = Path(r"C:\Program Files\PostgreSQL\16\bin\pg_dump.exe")
PG_RESTORE = Path(r"C:\Program Files\PostgreSQL\16\bin\pg_restore.exe")
PASTA_BACKUPS = Path(__file__).resolve().parents[1] / "dados" / "backups"
MIGRACOES = Path(__file__).resolve().parents[2] / "database" / "migrations"


def _backup(configuracao):
    instante = datetime.now().strftime("%Y%m%d_%H%M%S")
    destino = PASTA_BACKUPS / f"games_pre_registro_criterios_20_5_{instante}.dump"
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
    if sys.argv[1:] != ["CONFIRMAR_GAMES_20_5"]:
        raise SystemExit("Uso: aplicar_registro_criterios_games.py CONFIRMAR_GAMES_20_5")
    configuracao = carregar_configuracao_banco()
    if configuracao.nome != "games":
        raise RuntimeError("A operação exige GAME_DB_NAME=games.")
    with abrir_conexao(configuracao) as conexao:
        with conexao.cursor() as cursor:
            cursor.execute("SELECT versao FROM schema_migrations ORDER BY versao")
            versoes = tuple(linha[0] for linha in cursor.fetchall())
            cursor.execute("SELECT count(*) FROM criterios_validacao")
            criterios_antes = cursor.fetchone()[0]
            cursor.execute("SELECT count(*) FROM amostras_validacao")
            amostras = cursor.fetchone()[0]
    if versoes != tuple(f"{numero:03d}" for numero in range(1, 14)):
        raise RuntimeError(f"Migrações iniciais inesperadas: {versoes!r}")
    if criterios_antes != 0 or amostras != 0:
        raise RuntimeError("A subetapa 20.5 exige catálogo e amostras ainda vazios.")

    backup, sha256, itens = _backup(configuracao)
    migracoes = executar_migracoes(configuracao, MIGRACOES)
    if migracoes.aplicadas != ("014",):
        raise RuntimeError(f"Migração aplicada inesperada: {migracoes!r}")
    registro = criar_registro_criterios_producao()
    with abrir_conexao(configuracao) as conexao:
        relatorio = sincronizar_criterios_validacao(conexao, registro)
        conexao.commit()
        repeticao = sincronizar_criterios_validacao(conexao, registro)
        conexao.commit()
        with conexao.cursor() as cursor:
            cursor.execute(
                "SELECT categoria, count(*) FROM criterios_validacao "
                "GROUP BY categoria ORDER BY categoria"
            )
            categorias = dict(cursor.fetchall())
            cursor.execute("SELECT count(*) FROM avaliacoes_validacao")
            avaliacoes = cursor.fetchone()[0]
            cursor.execute("SELECT atualizado, motivo FROM estado_algoritmo_selecao")
            estado = cursor.fetchone()
    if categorias != {"ESTATISTICA": 4, "GEOMETRIA": 6, "PADRAO": 9}:
        raise RuntimeError(f"Catálogo final inesperado: {categorias!r}")
    if avaliacoes != 0 or estado != (False, "CATALOGO_DE_CRITERIOS_ALTERADO"):
        raise RuntimeError("Avaliações ou estado global divergiram do contrato.")
    if repeticao.houve_alteracao or repeticao.avaliacoes_criadas:
        raise RuntimeError("A repetição da sincronização não foi idempotente.")
    print(json.dumps({
        "backup": str(backup), "backup_bytes": backup.stat().st_size,
        "backup_sha256": sha256, "backup_itens_catalogo": itens,
        "migracao_aplicada": list(migracoes.aplicadas),
        "criterios_incluidos": list(relatorio.incluidos),
        "categorias": categorias, "avaliacoes": avaliacoes,
        "estado_algoritmo": estado, "repeticao_idempotente": True,
    }, ensure_ascii=False, indent=2, default=list))


if __name__ == "__main__":
    main()
