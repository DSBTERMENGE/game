"""Executa a subetapa 20.9 no banco local após backup e verificações."""

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
from msen.services import executar_criterios_numericos


PG_DUMP = Path(r"C:\Program Files\PostgreSQL\16\bin\pg_dump.exe")
PG_RESTORE = Path(r"C:\Program Files\PostgreSQL\16\bin\pg_restore.exe")
PASTA_BACKUPS = Path(__file__).resolve().parents[1] / "dados" / "backups"


def _backup(configuracao):
    instante = datetime.now().strftime("%Y%m%d_%H%M%S")
    destino = PASTA_BACKUPS / f"games_pre_execucao_geometrica_20_9_{instante}.dump"
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


def _referencias(conexao):
    with conexao.cursor() as cursor:
        cursor.execute(
            "SELECT a.id_resultado, a.id_criterio, a.referencia_conferida, "
            "a.estado_valor_esperado, a.valor_esperado::text, a.referencia_origem, "
            "a.referencia_revisor, a.referencia_observacao, "
            "a.referencia_conferida_em::text FROM avaliacoes_validacao a "
            "JOIN criterios_validacao c USING (id_criterio) "
            "WHERE c.categoria = 'GEOMETRIA' ORDER BY 1, 2"
        )
        linhas = cursor.fetchall()
    serializado = json.dumps(linhas, default=str, ensure_ascii=False)
    return len(linhas), hashlib.sha256(serializado.encode("utf-8")).hexdigest().upper()


def main() -> None:
    load_dotenv()
    if sys.argv[1:] != ["CONFIRMAR_EXECUCAO_GEOMETRICA_20_9"]:
        raise SystemExit(
            "Uso: aplicar_validacao_geometrica_games.py "
            "CONFIRMAR_EXECUCAO_GEOMETRICA_20_9"
        )
    configuracao = carregar_configuracao_banco()
    if configuracao.nome != "games":
        raise RuntimeError("A operação exige GAME_DB_NAME=games.")
    with abrir_conexao(configuracao) as conexao:
        quantidade_antes, referencias_antes = _referencias(conexao)
        with conexao.cursor() as cursor:
            cursor.execute(
                "SELECT count(*) FROM avaliacoes_validacao a JOIN criterios_validacao c "
                "USING (id_criterio) WHERE c.categoria = 'GEOMETRIA' "
                "AND a.referencia_conferida"
            )
            conferidas = cursor.fetchone()[0]
    if quantidade_antes != 1200 or conferidas != 1200:
        raise RuntimeError("As 1.200 referências geométricas não estão conferidas.")

    backup, sha256, itens = _backup(configuracao)
    with abrir_conexao(configuracao) as conexao:
        relatorio = executar_criterios_numericos(conexao, categoria="GEOMETRIA")
        quantidade_depois, referencias_depois = _referencias(conexao)
        with conexao.cursor() as cursor:
            cursor.execute(
                "SELECT count(*) FROM avaliacoes_validacao a JOIN criterios_validacao c "
                "USING (id_criterio) WHERE c.categoria = 'GEOMETRIA' "
                "AND a.executado AND a.assinatura_executada = c.assinatura_funcao"
            )
            assinaturas_atuais = cursor.fetchone()[0]
            cursor.execute(
                "SELECT codigo, estado FROM criterios_validacao "
                "WHERE categoria = 'GEOMETRIA' ORDER BY codigo"
            )
            estados = dict(cursor.fetchall())
            cursor.execute(
                "SELECT c.codigo, r.numero_ap, a.valor_esperado::text, "
                "a.valor_calculado::text, a.diferenca::text FROM avaliacoes_validacao a "
                "JOIN criterios_validacao c USING (id_criterio) "
                "JOIN resultados r USING (id_resultado) "
                "WHERE c.categoria = 'GEOMETRIA' AND a.aprovado = 'N' "
                "ORDER BY c.codigo, r.numero_ap LIMIT 50"
            )
            divergencias = cursor.fetchall()
            cursor.execute(
                "SELECT atualizado, motivo FROM estado_algoritmo_selecao WHERE id_estado = 1"
            )
            estado_algoritmo = cursor.fetchone()
    if (quantidade_antes, referencias_antes) != (quantidade_depois, referencias_depois):
        raise RuntimeError("As referências protegidas foram alteradas durante a execução.")
    if relatorio.total_avaliacoes != 1200 or assinaturas_atuais != 1200:
        raise RuntimeError("A execução geométrica não cobriu as 1.200 avaliações.")

    print(json.dumps({
        "backup": str(backup), "backup_bytes": backup.stat().st_size,
        "backup_sha256": sha256, "backup_itens_catalogo": itens,
        "hash_referencias_antes": referencias_antes,
        "hash_referencias_depois": referencias_depois,
        "relatorio": {
            "total_criterios": relatorio.total_criterios,
            "total_avaliacoes": relatorio.total_avaliacoes,
            "aprovadas": relatorio.aprovadas,
            "reprovadas": relatorio.reprovadas,
            "criterios": [{
                "codigo": item.codigo, "total": item.total,
                "aprovados": item.aprovados, "reprovados": item.reprovados,
                "estado": item.estado,
            } for item in relatorio.criterios],
        },
        "assinaturas_atuais": assinaturas_atuais,
        "estados_criterios": estados,
        "primeiras_divergencias": divergencias,
        "estado_algoritmo": estado_algoritmo,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
