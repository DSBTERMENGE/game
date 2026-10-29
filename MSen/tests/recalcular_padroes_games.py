"""Cria backup e recalcula padrões no database local games com confirmação."""

from datetime import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

from dotenv import load_dotenv

from msen.config import carregar_configuracao_banco
from msen.database import (
    RepositorioPadroes,
    RepositorioResultados,
    abrir_conexao,
    executar_migracoes,
)
from msen.services import recalcular_padroes_iniciais


PG_DUMP = Path(r"C:\Program Files\PostgreSQL\16\bin\pg_dump.exe")
PASTA_BACKUPS = Path(__file__).resolve().parents[1] / "dados" / "backups"
MIGRACOES = Path(__file__).resolve().parents[2] / "database" / "migrations"
TEXTOS_COLUNAS = {
    "PD_004": (
        "Duas dezenas em linhas subjacentes na mesma coluna",
        "O maior grupo vertical possui exatamente duas dezenas na mesma coluna "
        "e em linhas imediatamente consecutivas.",
    ),
    "PD_005": (
        "Três dezenas em linhas subjacentes na mesma coluna",
        "O maior grupo vertical possui exatamente três dezenas na mesma coluna "
        "e em linhas imediatamente consecutivas.",
    ),
    "PD_006": (
        "Mais de três dezenas em linhas subjacentes na mesma coluna",
        "O maior grupo vertical possui quatro, cinco ou seis dezenas na mesma "
        "coluna e em linhas imediatamente consecutivas.",
    ),
}


def _resumo_padroes(padroes) -> dict[str, dict[str, object]]:
    return {
        item.padrao_cod: {
            "grupo_cod": item.grupo_cod,
            "padrao_nome": item.padrao_nome,
            "padrao_descr": item.padrao_descr,
            "num_oco": item.num_oco,
            "total_sorteios": item.total_sorteios,
            "percentual_ocorrencia": (
                None
                if item.percentual_ocorrencia is None
                else str(item.percentual_ocorrencia)
            ),
            "intervalo_medio": (
                None if item.intervalo_medio is None else str(item.intervalo_medio)
            ),
            "desv_padrao": None if item.desv_padrao is None else str(item.desv_padrao),
        }
        for item in padroes
    }


def _criar_backup(configuracao) -> tuple[Path, str]:
    if not PG_DUMP.is_file():
        raise FileNotFoundError(f"pg_dump não encontrado: {PG_DUMP}")
    PASTA_BACKUPS.mkdir(parents=True, exist_ok=True)
    instante = datetime.now().strftime("%Y%m%d_%H%M%S")
    destino = PASTA_BACKUPS / f"games_pre_recalculo_padroes_{instante}.dump"
    ambiente = os.environ.copy()
    ambiente["PGPASSWORD"] = configuracao.senha
    subprocess.run(
        [
            str(PG_DUMP),
            "--format=custom",
            "--no-owner",
            "--no-privileges",
            "--host",
            configuracao.host,
            "--port",
            str(configuracao.porta),
            "--username",
            configuracao.usuario,
            "--file",
            str(destino),
            configuracao.nome,
        ],
        check=True,
        env=ambiente,
    )
    if not destino.is_file() or destino.stat().st_size == 0:
        raise RuntimeError("O arquivo de backup não foi criado corretamente.")
    resumo = hashlib.sha256(destino.read_bytes()).hexdigest().upper()
    return destino, resumo


def executar() -> dict[str, object]:
    """Faz backup, alinha textos e recalcula os seis padrões aprovados.

    Retorno:
        Caminho e hash do backup, totais e estatísticas anteriores e posteriores.

    Regra:
        A operação recusa qualquer database cujo nome não seja exatamente
        `games`. O backup é concluído antes da transação de recálculo.
    """

    configuracao = carregar_configuracao_banco()
    if configuracao.nome != "games":
        raise RuntimeError("A operação exige GAME_DB_NAME=games.")

    destino, sha256 = _criar_backup(configuracao)
    migracoes = executar_migracoes(configuracao, MIGRACOES)
    with abrir_conexao(configuracao) as conexao:
        repositorio_padroes = RepositorioPadroes(conexao)
        repositorio_resultados = RepositorioResultados(conexao)
        total_antes = repositorio_resultados.contar()
        antes = _resumo_padroes(repositorio_padroes.listar())
        if tuple(antes) != tuple(f"PD_{numero:03d}" for numero in range(1, 10)):
            raise RuntimeError("O catálogo local não contém exatamente PD_001–PD_009.")

        for codigo, (nome, descricao) in TEXTOS_COLUNAS.items():
            repositorio_padroes.atualizar_textos(
                codigo, nome, descricao, antes[codigo]["grupo_cod"]
            )
        relatorio = recalcular_padroes_iniciais(conexao)
        total_depois = repositorio_resultados.contar()
        depois = _resumo_padroes(RepositorioPadroes(conexao).listar())

    if total_antes != total_depois or total_depois != relatorio.resultados_analisados:
        raise RuntimeError("O total de resultados mudou durante o recálculo.")
    for codigo in antes:
        if antes[codigo]["grupo_cod"] != depois[codigo]["grupo_cod"]:
            raise RuntimeError(f"O grupo de {codigo} foi alterado.")
    for codigo, (nome, descricao) in TEXTOS_COLUNAS.items():
        if depois[codigo]["padrao_nome"] != nome:
            raise RuntimeError(f"O nome aprovado de {codigo} não foi persistido.")
        if depois[codigo]["padrao_descr"] != descricao:
            raise RuntimeError(f"A descrição aprovada de {codigo} não foi persistida.")

    return {
        "backup": str(destino),
        "backup_bytes": destino.stat().st_size,
        "backup_sha256": sha256,
        "migracoes_aplicadas": list(migracoes.aplicadas),
        "migracoes_anteriores": list(migracoes.ja_aplicadas),
        "resultados": total_depois,
        "antes": antes,
        "depois": depois,
    }


def main() -> None:
    """Exige confirmação explícita e executa a operação local autorizada."""

    load_dotenv()
    if sys.argv[1:] != ["CONFIRMAR_GAMES"]:
        raise SystemExit("Uso: recalcular_padroes_games.py CONFIRMAR_GAMES")
    print(json.dumps(executar(), ensure_ascii=False))


if __name__ == "__main__":
    main()
