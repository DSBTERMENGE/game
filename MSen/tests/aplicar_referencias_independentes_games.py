"""Calcula e aprova referências não geométricas por oráculo independente."""

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
from msen.services import aprovar_referencia_numerica, aprovar_referencia_padrao
from oraculo_referencias_independentes import (
    referencias_estatisticas,
    referencias_padroes,
)


PG_DUMP = Path(r"C:\Program Files\PostgreSQL\16\bin\pg_dump.exe")
PG_RESTORE = Path(r"C:\Program Files\PostgreSQL\16\bin\pg_restore.exe")
PASTA_BACKUPS = Path(__file__).resolve().parents[1] / "dados" / "backups"


def _backup(configuracao):
    instante = datetime.now().strftime("%Y%m%d_%H%M%S")
    destino = PASTA_BACKUPS / f"games_pre_gabarito_parcial_20_7_{instante}.dump"
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
    if sys.argv[1:] != ["CONFIRMAR_GABARITO_PARCIAL_20_7"]:
        raise SystemExit(
            "Uso: aplicar_referencias_independentes_games.py "
            "CONFIRMAR_GABARITO_PARCIAL_20_7"
        )
    configuracao = carregar_configuracao_banco()
    if configuracao.nome != "games":
        raise RuntimeError("A operação exige GAME_DB_NAME=games.")
    with abrir_conexao(configuracao) as conexao:
        with conexao.cursor() as cursor:
            cursor.execute(
                "SELECT count(*) FROM avaliacoes_validacao WHERE referencia_conferida"
            )
            if cursor.fetchone()[0] != 0:
                raise RuntimeError("A carga parcial exige referências ainda vazias.")
            cursor.execute(
                "SELECT a.id_resultado, r.res_01, r.res_02, r.res_03, r.res_04, "
                "r.res_05, r.res_06 FROM amostras_validacao a "
                "JOIN resultados r USING (id_resultado) ORDER BY a.ordem"
            )
            amostras = tuple(cursor.fetchall())
            cursor.execute(
                "SELECT codigo, id_criterio FROM criterios_validacao"
            )
            criterios = dict(cursor.fetchall())
            cursor.execute("SELECT padrao_cod, id_padrao FROM padroes_subgrupo")
            padroes = dict(cursor.fetchall())
    if len(amostras) != 200:
        raise RuntimeError("A carga exige exatamente 200 amostras iniciais.")

    backup, sha256, itens = _backup(configuracao)
    with abrir_conexao(configuracao) as conexao:
        with conexao.transaction():
            for linha in amostras:
                id_resultado, *numeros = linha
                dezenas = tuple(numeros)
                for codigo, valor in referencias_estatisticas(dezenas).items():
                    aprovar_referencia_numerica(
                        conexao, id_resultado=id_resultado,
                        id_criterio=criterios[codigo], valor=valor,
                        origem="TESTE_AUTOMATIZADO",
                        revisor="oráculo independente estatístico 20.7",
                    )
                for codigo, detectado in referencias_padroes(dezenas).items():
                    padrao_codigo = codigo.removeprefix("PAD_")
                    aprovar_referencia_padrao(
                        conexao, id_resultado=id_resultado,
                        id_criterio=criterios[codigo],
                        id_padrao=padroes[padrao_codigo] if detectado else None,
                        origem="TESTE_AUTOMATIZADO",
                        revisor="oráculo independente de padrões 20.7",
                    )
        with conexao.cursor() as cursor:
            cursor.execute(
                "SELECT c.categoria, count(*) FROM avaliacoes_validacao a "
                "JOIN criterios_validacao c USING (id_criterio) "
                "WHERE a.referencia_conferida GROUP BY c.categoria ORDER BY c.categoria"
            )
            conferidas = dict(cursor.fetchall())
            cursor.execute(
                "SELECT c.categoria, count(*) FROM avaliacoes_validacao a "
                "JOIN criterios_validacao c USING (id_criterio) "
                "WHERE NOT a.referencia_conferida GROUP BY c.categoria ORDER BY c.categoria"
            )
            pendentes = dict(cursor.fetchall())
            cursor.execute(
                "SELECT count(*) FROM avaliacoes_validacao WHERE referencia_conferida "
                "AND (referencia_origem <> 'TESTE_AUTOMATIZADO' "
                "OR referencia_revisor IS NULL OR referencia_conferida_em IS NULL)"
            )
            metadados_invalidos = cursor.fetchone()[0]
    if conferidas != {"ESTATISTICA": 800, "PADRAO": 1800}:
        raise RuntimeError(f"Referências conferidas divergentes: {conferidas!r}")
    if pendentes != {"GEOMETRIA": 1200} or metadados_invalidos:
        raise RuntimeError(f"Pendências ou metadados divergentes: {pendentes!r}")
    print(json.dumps({
        "backup": str(backup), "backup_bytes": backup.stat().st_size,
        "backup_sha256": sha256, "backup_itens_catalogo": itens,
        "referencias_conferidas": conferidas,
        "referencias_pendentes": pendentes,
        "metadados_invalidos": metadados_invalidos,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
