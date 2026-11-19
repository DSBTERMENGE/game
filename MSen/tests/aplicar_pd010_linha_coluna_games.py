"""Aplica, em uma transação, a consolidação do padrão PD_010 no banco games."""

from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

from dotenv import load_dotenv

from msen.config import carregar_configuracao_banco
from msen.database import abrir_conexao
from msen.modelos import ResultadoEntrada
from msen.padroes import calcular_estatistica_padrao
from msen.services import (
    aprovar_referencia_padrao,
    atualizar_validacao_e_auditoria,
    sincronizar_criterios_validacao,
)
from msen.validacao import criar_registro_criterios_producao


RAIZ = Path(__file__).resolve().parents[2]
PASTA_BACKUPS = RAIZ / "MSen" / "dados" / "backups"
PG_DUMP = Path(r"C:\Program Files\PostgreSQL\16\bin\pg_dump.exe")
PG_RESTORE = Path(r"C:\Program Files\PostgreSQL\16\bin\pg_restore.exe")
FUNCAO = "msen.padroes.linha_coluna.detectar_dezenas_em_uma_linha_e_uma_coluna"
ALVO = "PD_010"
REDUNDANTES = ("PD_037", "PD_038", "PD_039")


def _backup(configuracao) -> tuple[Path, str]:
    if not PG_DUMP.is_file() or not PG_RESTORE.is_file():
        raise FileNotFoundError("pg_dump ou pg_restore não encontrado.")
    PASTA_BACKUPS.mkdir(parents=True, exist_ok=True)
    instante = datetime.now().strftime("%Y%m%d_%H%M%S")
    destino = PASTA_BACKUPS / f"games_pre_pd010_12_3_{instante}.dump"
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
    for tabela in ("padroes_subgrupo", "criterios_validacao", "avaliacoes_validacao"):
        if f"TABLE public {tabela}" not in catalogo:
            raise RuntimeError(f"O backup não contém a tabela {tabela}.")
    return destino, hashlib.sha256(destino.read_bytes()).hexdigest().upper()


def _referencia_independente(dezenas: tuple[int, ...]) -> bool:
    """Oráculo local: não chama o detector que está sendo homologado."""

    pontos = tuple((divmod(dezena - 1, 10)[0] + 1, divmod(dezena - 1, 10)[1] + 1)
                   for dezena in dezenas)
    for linha in {item[0] for item in pontos}:
        for coluna in {item[1] for item in pontos}:
            if (
                all(l == linha or c == coluna for l, c in pontos)
                and any(l == linha and c != coluna for l, c in pontos)
                and any(c == coluna and l != linha for l, c in pontos)
            ):
                return True
    return False


def main() -> None:
    load_dotenv()
    if sys.argv[1:] != ["CONFIRMAR_PD010_12_3"]:
        raise SystemExit("Uso: aplicar_pd010_linha_coluna_games.py CONFIRMAR_PD010_12_3")
    configuracao = carregar_configuracao_banco()
    if configuracao.nome != "games":
        raise RuntimeError("A operação exige GAME_DB_NAME=games.")

    with abrir_conexao(configuracao) as conexao:
        with conexao.cursor() as cursor:
            cursor.execute(
                "SELECT id_padrao, id_grupo, padrao_cod, padrao_nome, funcao_detectora "
                "FROM padroes_subgrupo WHERE padrao_cod = ANY(%s) ORDER BY padrao_cod",
                ([ALVO, *REDUNDANTES],),
            )
            fotografia = tuple(cursor.fetchall())
    codigos = tuple(item[2] for item in fotografia)
    if codigos != (ALVO, *REDUNDANTES):
        raise RuntimeError(f"Fotografia dos quatro padrões divergente: {fotografia!r}")
    if fotografia[0][0:3] != (16, 9, ALVO) or any(item[1] != 9 for item in fotografia):
        raise RuntimeError(f"IDs ou grupo inesperados: {fotografia!r}")
    if any(item[4] is not None for item in fotografia):
        raise RuntimeError("Um dos padrões já possui função e exige revisão manual.")

    backup, sha256 = _backup(configuracao)
    with abrir_conexao(configuracao) as conexao:
        with conexao.transaction():
            with conexao.cursor() as cursor:
                cursor.execute(
                    "SELECT data_resultado, numero_ap, res_01, res_02, res_03, res_04, "
                    "res_05, res_06 FROM resultados ORDER BY numero_ap"
                )
                resultados = tuple(cursor.fetchall())
            serie = tuple(
                ResultadoEntrada(
                    data_resultado=item[0], numero_ap=item[1],
                    res_01=item[2], res_02=item[3], res_03=item[4],
                    res_04=item[5], res_05=item[6], res_06=item[7],
                )
                for item in resultados
            )
            estatistica = calcular_estatistica_padrao(
                ALVO, _referencia_independente, serie
            )
            percentual = (
                Decimal(estatistica.num_oco) * Decimal(100) / Decimal(len(serie))
            ).quantize(Decimal("0.000001"), rounding=ROUND_HALF_UP)

            with conexao.cursor() as cursor:
                cursor.execute(
                    "UPDATE padroes_subgrupo SET funcao_detectora=%s, num_oco=%s, "
                    "total_sorteios=%s, percentual_ocorrencia=%s, intervalo_medio=%s, "
                    "desv_padrao=%s WHERE id_padrao=16 AND id_grupo=9 AND padrao_cod=%s",
                    (FUNCAO, estatistica.num_oco, len(serie), percentual,
                     estatistica.intervalo_medio, estatistica.desv_padrao, ALVO),
                )
                if cursor.rowcount != 1:
                    raise RuntimeError("PD_010 não foi atualizado de forma exclusiva.")
                cursor.execute(
                    "DELETE FROM padroes_subgrupo WHERE id_grupo=9 AND padrao_cod=ANY(%s) "
                    "RETURNING padrao_cod",
                    (list(REDUNDANTES),),
                )
                removidos = tuple(sorted(item[0] for item in cursor.fetchall()))
                if removidos != REDUNDANTES:
                    raise RuntimeError(f"Remoção divergente: {removidos!r}")

            sincronizacao = sincronizar_criterios_validacao(
                conexao, criar_registro_criterios_producao()
            )
            with conexao.cursor() as cursor:
                cursor.execute(
                    "SELECT id_criterio, id_padrao FROM criterios_validacao "
                    "WHERE codigo='PAD_PD_010'"
                )
                criterio = cursor.fetchone()
                cursor.execute(
                    "SELECT a.id_resultado, r.res_01, r.res_02, r.res_03, r.res_04, "
                    "r.res_05, r.res_06 FROM avaliacoes_validacao a "
                    "JOIN amostras_validacao am USING (id_resultado) "
                    "JOIN resultados r USING (id_resultado) "
                    "WHERE a.id_criterio=%s AND am.ativo ORDER BY am.ordem",
                    (criterio[0],),
                )
                amostras = tuple(cursor.fetchall())
            if criterio[1] != 16 or len(amostras) != 200:
                raise RuntimeError("Critério PD_010 ou suas 200 amostras divergiram.")
            positivos = 0
            for amostra in amostras:
                detectado = _referencia_independente(tuple(amostra[1:]))
                positivos += detectado
                aprovar_referencia_padrao(
                    conexao, id_resultado=amostra[0], id_criterio=criterio[0],
                    id_padrao=16 if detectado else None,
                    origem="TESTE_AUTOMATIZADO", revisor="oráculo independente 12.3",
                    observacao="União de uma linha horizontal e uma coluna no volante 6x10.",
                )
            homologacao = atualizar_validacao_e_auditoria(conexao)
            if not homologacao.homologacao_concluida:
                raise RuntimeError(f"Homologação não concluída: {homologacao!r}")
            with conexao.cursor() as cursor:
                cursor.execute(
                    "SELECT padrao_cod, funcao_detectora, num_oco, total_sorteios, "
                    "percentual_ocorrencia FROM padroes_subgrupo "
                    "WHERE padrao_cod = ANY(%s) ORDER BY padrao_cod",
                    ([ALVO, *REDUNDANTES],),
                )
                estado_final = tuple(cursor.fetchall())
                cursor.execute(
                    "SELECT estado FROM criterios_validacao WHERE codigo='PAD_PD_010'"
                )
                estado_criterio = cursor.fetchone()[0]
            esperado_final = ((ALVO, FUNCAO, estatistica.num_oco, len(serie), percentual),)
            if estado_final != esperado_final or estado_criterio != "APROVADO":
                raise RuntimeError(f"Estado final divergente: {estado_final!r}, {estado_criterio}")

    print(json.dumps({
        "backup": str(backup), "backup_sha256": sha256,
        "pd010": {"id_padrao": 16, "id_grupo": 9, "funcao": FUNCAO,
                  "ocorrencias": estatistica.num_oco, "resultados": len(serie),
                  "percentual": str(percentual)},
        "removidos": removidos,
        "criterio_incluido": sincronizacao.incluidos,
        "amostras_homologacao": len(amostras), "positivos_amostras": positivos,
        "estado_criterio": estado_criterio,
        "transacao_confirmada": True,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
