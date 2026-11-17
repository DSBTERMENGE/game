"""Protege e aplica a migração 037 e o critério PD_011 no banco games."""

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
from msen.padroes import resolver_funcao_detectora
from msen.services import sincronizar_criterios_validacao
from msen.validacao import criar_registro_criterios_producao


RAIZ = Path(__file__).resolve().parents[2]
MIGRACOES = RAIZ / "database" / "migrations"
PASTA_BACKUPS = RAIZ / "MSen" / "dados" / "backups"
PG_DUMP = Path(r"C:\Program Files\PostgreSQL\16\bin\pg_dump.exe")
PG_RESTORE = Path(r"C:\Program Files\PostgreSQL\16\bin\pg_restore.exe")
FUNCAO = "msen.padroes.duas_linhas.detectar_dezenas_em_duas_linhas"


def _fotografia(conexao) -> dict[str, object]:
    with conexao.cursor() as cursor:
        cursor.execute("SELECT versao FROM schema_migrations ORDER BY versao")
        versoes = tuple(linha[0] for linha in cursor.fetchall())
        cursor.execute(
            "SELECT funcao_detectora FROM padroes_subgrupo "
            "WHERE id_padrao=17 AND id_grupo=8"
        )
        padrao = cursor.fetchone()
        cursor.execute("SELECT * FROM criterios_validacao ORDER BY id_criterio")
        criterios = tuple(cursor.fetchall())
        cursor.execute(
            "SELECT * FROM avaliacoes_validacao ORDER BY id_resultado, id_criterio"
        )
        avaliacoes = tuple(cursor.fetchall())
        cursor.execute("SELECT count(*) FROM amostras_validacao WHERE ativo")
        amostras_ativas = cursor.fetchone()[0]
    return {
        "versoes": versoes,
        "funcao_pd_011": None if padrao is None else padrao[0],
        "criterios": criterios,
        "avaliacoes": avaliacoes,
        "amostras_ativas": amostras_ativas,
    }


def _criar_backup(configuracao) -> tuple[Path, str, int]:
    if not PG_DUMP.is_file() or not PG_RESTORE.is_file():
        raise FileNotFoundError("pg_dump ou pg_restore não encontrado.")
    PASTA_BACKUPS.mkdir(parents=True, exist_ok=True)
    instante = datetime.now().strftime("%Y%m%d_%H%M%S")
    destino = PASTA_BACKUPS / f"games_pre_funcao_duas_linhas_8_6_r_{instante}.dump"
    ambiente = os.environ.copy()
    ambiente["PGPASSWORD"] = configuracao.senha
    subprocess.run([
        str(PG_DUMP), "--format=custom", "--no-owner", "--no-privileges",
        "--host", configuracao.host, "--port", str(configuracao.porta),
        "--username", configuracao.usuario, "--file", str(destino),
        configuracao.nome,
    ], check=True, env=ambiente)
    listagem = subprocess.run(
        [str(PG_RESTORE), "--list", str(destino)],
        check=True, capture_output=True, text=True,
    ).stdout
    for item in (
        "TABLE public padroes_subgrupo",
        "TABLE public criterios_validacao",
        "TABLE public avaliacoes_validacao",
        "TABLE public schema_migrations",
    ):
        if item not in listagem:
            raise RuntimeError(f"O backup não contém {item}.")
    return (
        destino,
        hashlib.sha256(destino.read_bytes()).hexdigest().upper(),
        len(listagem.splitlines()),
    )


def main() -> None:
    load_dotenv()
    if sys.argv[1:] != ["CONFIRMAR_GAMES_8_6_R"]:
        raise SystemExit(
            "Uso: aplicar_funcao_duas_linhas_games.py CONFIRMAR_GAMES_8_6_R"
        )
    configuracao = carregar_configuracao_banco()
    if configuracao.nome != "games":
        raise RuntimeError("A operação exige GAME_DB_NAME=games.")

    with abrir_conexao(configuracao) as conexao:
        antes = _fotografia(conexao)
    if antes["versoes"][-1] != "036":
        raise RuntimeError(f"Migração inicial inesperada: {antes['versoes'][-1]!r}")
    if antes["funcao_pd_011"] is not None:
        raise RuntimeError("PD_011 já possui função no banco real.")
    if len(antes["criterios"]) != 20 or len(antes["avaliacoes"]) != 4000:
        raise RuntimeError("Quantidades iniciais de critérios ou avaliações divergentes.")
    if antes["amostras_ativas"] != 200:
        raise RuntimeError("A quantidade de amostras ativas não é 200.")

    backup, sha256, itens_backup = _criar_backup(configuracao)
    migracoes = executar_migracoes(configuracao, MIGRACOES)
    if migracoes.aplicadas != ("037",):
        raise RuntimeError(f"Migrações aplicadas inesperadas: {migracoes!r}")

    with abrir_conexao(configuracao) as conexao:
        relatorio = sincronizar_criterios_validacao(
            conexao, criar_registro_criterios_producao()
        )
        conexao.commit()
        repeticao = sincronizar_criterios_validacao(
            conexao, criar_registro_criterios_producao()
        )
        conexao.commit()
        depois = _fotografia(conexao)
        with conexao.cursor() as cursor:
            cursor.execute(
                "SELECT id_criterio, codigo, categoria, tipo_resultado, estado, "
                "id_grupo, id_padrao, funcao_python FROM criterios_validacao "
                "WHERE codigo='PAD_PD_011'"
            )
            novo = cursor.fetchone()
            cursor.execute(
                "SELECT count(*) FROM avaliacoes_validacao "
                "WHERE id_criterio=%s",
                (novo[0],),
            )
            avaliacoes_novas = cursor.fetchone()[0]

    if relatorio.incluidos != ("PAD_PD_011",) or relatorio.avaliacoes_criadas != 200:
        raise RuntimeError(f"Sincronização inesperada: {relatorio!r}")
    if repeticao.houve_alteracao or repeticao.avaliacoes_criadas:
        raise RuntimeError("A segunda sincronização não foi idempotente.")
    esperado = ("PAD_PD_011", "PADRAO", "PADRAO", "PENDENTE", 8, 17, FUNCAO)
    if novo[1:] != esperado or avaliacoes_novas != 200:
        raise RuntimeError(f"Novo critério divergente: {novo!r}, {avaliacoes_novas}")
    ids_anteriores = {linha[0] for linha in antes["criterios"]}
    criterios_anteriores_depois = tuple(
        linha for linha in depois["criterios"] if linha[0] in ids_anteriores
    )
    avaliacoes_anteriores_depois = tuple(
        linha for linha in depois["avaliacoes"] if linha[1] in ids_anteriores
    )
    if criterios_anteriores_depois != antes["criterios"]:
        raise RuntimeError("Um dos 20 critérios anteriores foi alterado.")
    if avaliacoes_anteriores_depois != antes["avaliacoes"]:
        raise RuntimeError("Uma das 4.000 avaliações anteriores foi alterada.")
    if depois["versoes"][-1] != "037" or depois["funcao_pd_011"] != FUNCAO:
        raise RuntimeError("O estado final da migração ou do vínculo divergiu.")

    detector = resolver_funcao_detectora(depois["funcao_pd_011"])
    if not detector((1, 2, 3, 11, 12, 13)) or detector((1, 11, 21, 31, 41, 51)):
        raise RuntimeError("A função vinculada não atende ao contrato booleano.")

    print(json.dumps({
        "backup": str(backup),
        "backup_bytes": backup.stat().st_size,
        "backup_sha256": sha256,
        "backup_itens_catalogo": itens_backup,
        "migracao_aplicada": migracoes.aplicadas,
        "criterio_incluido": relatorio.incluidos,
        "avaliacoes_criadas": relatorio.avaliacoes_criadas,
        "criterios_anteriores_preservados": 20,
        "avaliacoes_anteriores_preservadas": 4000,
        "criterios_finais": len(depois["criterios"]),
        "avaliacoes_finais": len(depois["avaliacoes"]),
        "vinculo": novo,
        "sincronizacao_idempotente": True,
        "detector_validado": True,
    }, ensure_ascii=False, indent=2, default=str))


if __name__ == "__main__":
    main()
