"""Protege e recalcula automaticamente a estatística do PD_011 no games."""

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
from msen.services import recalcular_padroes_iniciais


RAIZ = Path(__file__).resolve().parents[2]
PASTA_BACKUPS = RAIZ / "MSen" / "dados" / "backups"
PG_DUMP = Path(r"C:\Program Files\PostgreSQL\16\bin\pg_dump.exe")
PG_RESTORE = Path(r"C:\Program Files\PostgreSQL\16\bin\pg_restore.exe")


def _estatisticas(conexao) -> dict[int, tuple]:
    with conexao.cursor() as cursor:
        cursor.execute(
            "SELECT id_padrao, num_oco, intervalo_medio, desv_padrao, "
            "total_sorteios, percentual_ocorrencia "
            "FROM padroes_subgrupo ORDER BY id_padrao"
        )
        return {linha[0]: linha[1:] for linha in cursor.fetchall()}


def _backup(configuracao) -> tuple[Path, str, int]:
    PASTA_BACKUPS.mkdir(parents=True, exist_ok=True)
    instante = datetime.now().strftime("%Y%m%d_%H%M%S")
    destino = PASTA_BACKUPS / f"games_pre_recalculo_duas_linhas_8_8_1_r_{instante}.dump"
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
    for item in ("TABLE public resultados", "TABLE public padroes_subgrupo"):
        if item not in catalogo:
            raise RuntimeError(f"O backup não contém {item}.")
    return (
        destino,
        hashlib.sha256(destino.read_bytes()).hexdigest().upper(),
        len(catalogo.splitlines()),
    )


def main() -> None:
    load_dotenv()
    if sys.argv[1:] != ["CONFIRMAR_GAMES_8_8_1_R"]:
        raise SystemExit(
            "Uso: aplicar_recalculo_duas_linhas_games.py CONFIRMAR_GAMES_8_8_1_R"
        )
    configuracao = carregar_configuracao_banco()
    if configuracao.nome != "games":
        raise RuntimeError("A operação exige GAME_DB_NAME=games.")

    with abrir_conexao(configuracao) as conexao:
        antes = _estatisticas(conexao)
        with conexao.cursor() as cursor:
            cursor.execute("SELECT count(*) FROM resultados")
            total = cursor.fetchone()[0]
    if total != 3069 or antes.get(17) != (None, None, None, None, None):
        raise RuntimeError("O estado inicial do PD_011 ou dos resultados divergiu.")

    backup, sha256, itens_backup = _backup(configuracao)
    with abrir_conexao(configuracao) as conexao:
        relatorio = recalcular_padroes_iniciais(conexao)
        conexao.commit()
        depois = _estatisticas(conexao)

    antigos_antes = {chave: valor for chave, valor in antes.items() if chave != 17}
    antigos_depois = {chave: valor for chave, valor in depois.items() if chave != 17}
    if antigos_depois != antigos_antes:
        raise RuntimeError("Uma estatística diferente de PD_011 foi alterada.")
    esperado = (32, depois[17][1], depois[17][2], 3069, depois[17][4])
    if depois[17] != esperado or str(depois[17][4]) != "1.042685":
        raise RuntimeError(f"Estatística final de PD_011 divergente: {depois[17]!r}")
    if relatorio.resultados_analisados != 3069:
        raise RuntimeError("O recálculo não analisou os 3.069 resultados.")

    print(json.dumps({
        "backup": str(backup),
        "backup_bytes": backup.stat().st_size,
        "backup_sha256": sha256,
        "backup_itens_catalogo": itens_backup,
        "resultados_analisados": relatorio.resultados_analisados,
        "pd_011": {
            "ocorrencias": depois[17][0],
            "intervalo_medio": str(depois[17][1]),
            "desvio_padrao": str(depois[17][2]),
            "total_sorteios": depois[17][3],
            "percentual_ocorrencia": str(depois[17][4]),
        },
        "demais_estatisticas_preservadas": len(antigos_depois),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
