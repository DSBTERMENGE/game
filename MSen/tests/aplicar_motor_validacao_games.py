"""Executa o motor integrado da subetapa 20.11 no banco local."""

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
from msen.services import atualizar_validacao_e_auditoria


PG_DUMP = Path(r"C:\Program Files\PostgreSQL\16\bin\pg_dump.exe")
PG_RESTORE = Path(r"C:\Program Files\PostgreSQL\16\bin\pg_restore.exe")
PASTA_BACKUPS = Path(__file__).resolve().parents[1] / "dados" / "backups"


def _backup(configuracao):
    instante = datetime.now().strftime("%Y%m%d_%H%M%S")
    destino = PASTA_BACKUPS / f"games_pre_motor_validacao_20_11_{instante}.dump"
    ambiente = os.environ.copy()
    ambiente["PGPASSWORD"] = configuracao.senha
    subprocess.run([
        str(PG_DUMP), "--format=custom", "--no-owner", "--no-privileges",
        "--host", configuracao.host, "--port", str(configuracao.porta),
        "--username", configuracao.usuario, "--file", str(destino),
        configuracao.nome,
    ], check=True, env=ambiente)
    catalogo = subprocess.run(
        [str(PG_RESTORE), "--list", str(destino)], check=True,
        capture_output=True, text=True,
    ).stdout
    if "TABLE public avaliacoes_validacao" not in catalogo:
        raise RuntimeError("O backup não contém as avaliações de validação.")
    return destino, hashlib.sha256(destino.read_bytes()).hexdigest().upper(), len(catalogo.splitlines())


def _hash_referencias(conexao):
    with conexao.cursor() as cursor:
        cursor.execute(
            "SELECT id_resultado, id_criterio, id_grupo, referencia_conferida, "
            "estado_valor_esperado, valor_esperado::text, estado_padrao_esperado, "
            "id_padrao_esperado, referencia_origem, referencia_revisor, "
            "referencia_observacao, referencia_conferida_em::text "
            "FROM avaliacoes_validacao ORDER BY 1, 2"
        )
        linhas = cursor.fetchall()
    serializado = json.dumps(linhas, default=str, ensure_ascii=False)
    return len(linhas), hashlib.sha256(serializado.encode("utf-8")).hexdigest().upper()


def main() -> None:
    load_dotenv()
    if sys.argv[1:] != ["CONFIRMAR_MOTOR_VALIDACAO_20_11"]:
        raise SystemExit(
            "Uso: aplicar_motor_validacao_games.py CONFIRMAR_MOTOR_VALIDACAO_20_11"
        )
    configuracao = carregar_configuracao_banco()
    if configuracao.nome != "games":
        raise RuntimeError("A operação exige GAME_DB_NAME=games.")
    with abrir_conexao(configuracao) as conexao:
        quantidade_antes, hash_antes = _hash_referencias(conexao)
    if quantidade_antes != 3800:
        raise RuntimeError("A matriz inicial deve conter 3.800 avaliações.")
    backup, sha256, itens = _backup(configuracao)
    with abrir_conexao(configuracao) as conexao:
        relatorio = atualizar_validacao_e_auditoria(conexao)
        quantidade_depois, hash_depois = _hash_referencias(conexao)
        with conexao.cursor() as cursor:
            cursor.execute(
                "SELECT categoria, estado, count(*) FROM criterios_validacao "
                "WHERE ativo GROUP BY categoria, estado ORDER BY categoria, estado"
            )
            estados = cursor.fetchall()
            cursor.execute(
                "SELECT atualizado, motivo FROM estado_algoritmo_selecao WHERE id_estado = 1"
            )
            estado_global = cursor.fetchone()
    if (quantidade_antes, hash_antes) != (quantidade_depois, hash_depois):
        raise RuntimeError("O motor alterou as referências protegidas.")
    if relatorio.total_avaliacoes != 3800 or relatorio.total_criterios != 19:
        raise RuntimeError("O motor não cobriu toda a matriz ativa.")
    print(json.dumps({
        "backup": str(backup), "backup_bytes": backup.stat().st_size,
        "backup_sha256": sha256, "backup_itens_catalogo": itens,
        "hash_referencias_antes": hash_antes,
        "hash_referencias_depois": hash_depois,
        "sincronizacao": {
            "incluidos": relatorio.sincronizacao.incluidos,
            "implementacoes_alteradas": relatorio.sincronizacao.implementacoes_alteradas,
            "regras_alteradas": relatorio.sincronizacao.regras_alteradas,
            "excluidos": relatorio.sincronizacao.excluidos,
            "avaliacoes_criadas": relatorio.sincronizacao.avaliacoes_criadas,
        },
        "total_criterios": relatorio.total_criterios,
        "total_avaliacoes": relatorio.total_avaliacoes,
        "aprovadas": relatorio.aprovadas,
        "reprovadas": relatorio.reprovadas,
        "pendentes": relatorio.pendentes,
        "criterios_aprovados": relatorio.criterios_aprovados,
        "criterios_reprovados": relatorio.criterios_reprovados,
        "criterios_pendentes": relatorio.criterios_pendentes,
        "homologacao_concluida": relatorio.homologacao_concluida,
        "estados_por_categoria": estados,
        "estado_global": estado_global,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
