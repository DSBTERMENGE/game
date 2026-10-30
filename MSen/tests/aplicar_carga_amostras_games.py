"""Protege e carrega as 200 amostras iniciais no database games."""

from datetime import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

from dotenv import load_dotenv

from msen.config import carregar_configuracao_banco
from msen.database import abrir_conexao
from msen.services import carregar_amostras_iniciais_validacao


PG_DUMP = Path(r"C:\Program Files\PostgreSQL\16\bin\pg_dump.exe")
PG_RESTORE = Path(r"C:\Program Files\PostgreSQL\16\bin\pg_restore.exe")
PASTA_BACKUPS = Path(__file__).resolve().parents[1] / "dados" / "backups"


def _backup(configuracao):
    instante = datetime.now().strftime("%Y%m%d_%H%M%S")
    destino = PASTA_BACKUPS / f"games_pre_amostras_20_6_{instante}.dump"
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
    if sys.argv[1:] != ["CONFIRMAR_GAMES_20_6"]:
        raise SystemExit("Uso: aplicar_carga_amostras_games.py CONFIRMAR_GAMES_20_6")
    configuracao = carregar_configuracao_banco()
    if configuracao.nome != "games":
        raise RuntimeError("A operação exige GAME_DB_NAME=games.")
    with abrir_conexao(configuracao) as conexao:
        with conexao.cursor() as cursor:
            cursor.execute("SELECT count(*) FROM resultados")
            resultados = cursor.fetchone()[0]
            cursor.execute("SELECT count(*) FROM criterios_validacao")
            criterios = cursor.fetchone()[0]
            cursor.execute("SELECT count(*) FROM amostras_validacao")
            amostras_antes = cursor.fetchone()[0]
            cursor.execute("SELECT count(*) FROM avaliacoes_validacao")
            avaliacoes_antes = cursor.fetchone()[0]
    if resultados != 3069 or criterios != 19:
        raise RuntimeError("Resultados ou critérios divergiram do estado autorizado.")
    if amostras_antes or avaliacoes_antes:
        raise RuntimeError("A carga inicial exige amostras e avaliações vazias.")

    backup, sha256, itens = _backup(configuracao)
    with abrir_conexao(configuracao) as conexao:
        relatorio = carregar_amostras_iniciais_validacao(conexao)
        conexao.commit()
        repeticao = carregar_amostras_iniciais_validacao(conexao)
        conexao.commit()
        with conexao.cursor() as cursor:
            cursor.execute("SELECT count(*) FROM amostras_validacao")
            amostras = cursor.fetchone()[0]
            cursor.execute("SELECT count(*) FROM avaliacoes_validacao")
            avaliacoes = cursor.fetchone()[0]
            cursor.execute(
                "SELECT count(*) FROM avaliacoes_validacao WHERE "
                "referencia_conferida OR executado OR aprovado IS NOT NULL OR "
                "valor_esperado IS NOT NULL OR valor_calculado IS NOT NULL"
            )
            preenchidas = cursor.fetchone()[0]
            cursor.execute(
                "SELECT min(r.numero_ap), max(r.numero_ap), count(DISTINCT r.numero_ap) "
                "FROM amostras_validacao a JOIN resultados r USING (id_resultado)"
            )
            intervalo = cursor.fetchone()
            cursor.execute("SELECT atualizado, motivo FROM estado_algoritmo_selecao")
            estado = cursor.fetchone()
    if (amostras, avaliacoes, preenchidas) != (200, 3800, 0):
        raise RuntimeError("A matriz inicial divergiu do contrato.")
    if intervalo != (1, 200, 200):
        raise RuntimeError(f"Intervalo de concursos inesperado: {intervalo!r}")
    if repeticao.amostras_incluidas or repeticao.avaliacoes_criadas:
        raise RuntimeError("A repetição da carga não foi idempotente.")
    print(json.dumps({
        "backup": str(backup), "backup_bytes": backup.stat().st_size,
        "backup_sha256": sha256, "backup_itens_catalogo": itens,
        "relatorio": relatorio.__dict__ if hasattr(relatorio, "__dict__") else {
            campo: getattr(relatorio, campo) for campo in relatorio.__dataclass_fields__
        },
        "amostras": amostras, "avaliacoes": avaliacoes,
        "avaliacoes_preenchidas": preenchidas,
        "intervalo_numero_ap": intervalo, "estado_algoritmo": estado,
        "repeticao_idempotente": True,
    }, ensure_ascii=False, indent=2, default=list))


if __name__ == "__main__":
    main()
