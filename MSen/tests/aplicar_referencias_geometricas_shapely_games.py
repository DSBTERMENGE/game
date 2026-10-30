"""Aprova as referências geométricas calculadas pelo Shapely/GEOS."""

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
from msen.services import aprovar_referencia_numerica
from oraculo_referencias_independentes import referencias_geometricas


PG_DUMP = Path(r"C:\Program Files\PostgreSQL\16\bin\pg_dump.exe")
PG_RESTORE = Path(r"C:\Program Files\PostgreSQL\16\bin\pg_restore.exe")
PASTA_BACKUPS = Path(__file__).resolve().parents[1] / "dados" / "backups"


def _backup(configuracao):
    instante = datetime.now().strftime("%Y%m%d_%H%M%S")
    destino = PASTA_BACKUPS / f"games_pre_gabarito_geometrico_20_7_{instante}.dump"
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
    if "TABLE public avaliacoes_validacao" not in listagem:
        raise RuntimeError("O backup não contém as avaliações de validação.")
    return destino, hashlib.sha256(destino.read_bytes()).hexdigest().upper(), len(listagem.splitlines())


def main() -> None:
    load_dotenv()
    if sys.argv[1:] != ["CONFIRMAR_GABARITO_GEOMETRICO_20_7"]:
        raise SystemExit(
            "Uso: aplicar_referencias_geometricas_shapely_games.py "
            "CONFIRMAR_GABARITO_GEOMETRICO_20_7"
        )
    configuracao = carregar_configuracao_banco()
    if configuracao.nome != "games":
        raise RuntimeError("A operação exige GAME_DB_NAME=games.")
    with abrir_conexao(configuracao) as conexao:
        with conexao.cursor() as cursor:
            cursor.execute(
                "SELECT c.categoria, count(*) FROM avaliacoes_validacao a "
                "JOIN criterios_validacao c USING (id_criterio) "
                "WHERE a.referencia_conferida GROUP BY c.categoria"
            )
            conferidas_antes = dict(cursor.fetchall())
            cursor.execute(
                "SELECT a.id_resultado, r.res_01, r.res_02, r.res_03, r.res_04, "
                "r.res_05, r.res_06 FROM amostras_validacao a "
                "JOIN resultados r USING (id_resultado) ORDER BY a.ordem"
            )
            amostras = tuple(cursor.fetchall())
            cursor.execute(
                "SELECT codigo, id_criterio FROM criterios_validacao "
                "WHERE categoria = 'GEOMETRIA'"
            )
            criterios = dict(cursor.fetchall())
    if conferidas_antes != {"ESTATISTICA": 800, "PADRAO": 1800}:
        raise RuntimeError(f"Estado inicial inesperado: {conferidas_antes!r}")
    if len(amostras) != 200 or len(criterios) != 6:
        raise RuntimeError("Amostras ou critérios geométricos divergiram.")

    backup, sha256, itens = _backup(configuracao)
    with abrir_conexao(configuracao) as conexao:
        with conexao.transaction():
            for linha in amostras:
                id_resultado, *numeros = linha
                for codigo, valor in referencias_geometricas(tuple(numeros)).items():
                    aprovar_referencia_numerica(
                        conexao, id_resultado=id_resultado,
                        id_criterio=criterios[codigo], valor=valor,
                        origem="TESTE_AUTOMATIZADO",
                        revisor="Shapely/GEOS 2.2.0 — oráculo geométrico 20.7",
                    )
        with conexao.cursor() as cursor:
            cursor.execute(
                "SELECT c.categoria, count(*) FROM avaliacoes_validacao a "
                "JOIN criterios_validacao c USING (id_criterio) "
                "WHERE a.referencia_conferida GROUP BY c.categoria ORDER BY c.categoria"
            )
            conferidas = dict(cursor.fetchall())
            cursor.execute(
                "SELECT count(*) FROM avaliacoes_validacao WHERE NOT referencia_conferida"
            )
            pendentes = cursor.fetchone()[0]
            cursor.execute(
                "SELECT count(*) FROM avaliacoes_validacao WHERE "
                "estado_valor_esperado = 'SEM_VALOR'"
            )
            sem_valor = cursor.fetchone()[0]
            cursor.execute(
                "SELECT count(*) FROM avaliacoes_validacao WHERE referencia_conferida "
                "AND (referencia_origem IS NULL OR referencia_revisor IS NULL "
                "OR referencia_conferida_em IS NULL)"
            )
            metadados_invalidos = cursor.fetchone()[0]
    esperado = {"ESTATISTICA": 800, "GEOMETRIA": 1200, "PADRAO": 1800}
    if conferidas != esperado or pendentes or metadados_invalidos:
        raise RuntimeError(
            f"Gabarito final divergente: {conferidas!r}, pendentes={pendentes}."
        )
    print(json.dumps({
        "backup": str(backup), "backup_bytes": backup.stat().st_size,
        "backup_sha256": sha256, "backup_itens_catalogo": itens,
        "referencias_conferidas": conferidas,
        "referencias_pendentes": pendentes,
        "referencias_sem_valor": sem_valor,
        "metadados_invalidos": metadados_invalidos,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
