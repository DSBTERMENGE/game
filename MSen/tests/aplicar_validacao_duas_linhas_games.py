"""Valida somente o PAD_PD_011 nas 200 amostras do banco games."""

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
from msen.padroes import resolver_funcao_detectora
from msen.services import aprovar_referencia_padrao, comparar_resultado_padrao
from msen.validacao import criar_registro_criterios_producao
from oraculo_referencias_independentes import referencias_padroes


RAIZ = Path(__file__).resolve().parents[2]
PASTA_BACKUPS = RAIZ / "MSen" / "dados" / "backups"
PG_DUMP = Path(r"C:\Program Files\PostgreSQL\16\bin\pg_dump.exe")
PG_RESTORE = Path(r"C:\Program Files\PostgreSQL\16\bin\pg_restore.exe")
CODIGO = "PAD_PD_011"


def _backup(configuracao) -> tuple[Path, str, int]:
    PASTA_BACKUPS.mkdir(parents=True, exist_ok=True)
    instante = datetime.now().strftime("%Y%m%d_%H%M%S")
    destino = PASTA_BACKUPS / f"games_pre_validacao_duas_linhas_8_7_r_{instante}.dump"
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
    if "TABLE public avaliacoes_validacao" not in catalogo:
        raise RuntimeError("O backup não contém as avaliações de validação.")
    return (
        destino,
        hashlib.sha256(destino.read_bytes()).hexdigest().upper(),
        len(catalogo.splitlines()),
    )


def _linhas_outros_criterios(conexao, id_criterio: int) -> tuple[tuple, ...]:
    with conexao.cursor() as cursor:
        cursor.execute(
            "SELECT * FROM avaliacoes_validacao WHERE id_criterio <> %s "
            "ORDER BY id_resultado, id_criterio",
            (id_criterio,),
        )
        return tuple(cursor.fetchall())


def main() -> None:
    load_dotenv()
    if sys.argv[1:] != ["CONFIRMAR_GAMES_8_7_R"]:
        raise SystemExit(
            "Uso: aplicar_validacao_duas_linhas_games.py CONFIRMAR_GAMES_8_7_R"
        )
    configuracao = carregar_configuracao_banco()
    if configuracao.nome != "games":
        raise RuntimeError("A operação exige GAME_DB_NAME=games.")

    registro = criar_registro_criterios_producao()
    definicao = next(item for item in registro.listar() if item.codigo == CODIGO)
    with abrir_conexao(configuracao) as conexao:
        with conexao.cursor() as cursor:
            cursor.execute(
                "SELECT c.id_criterio, c.id_padrao, c.estado, c.assinatura_funcao, "
                "p.funcao_detectora FROM criterios_validacao c "
                "JOIN padroes_subgrupo p USING (id_padrao) WHERE c.codigo=%s",
                (CODIGO,),
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
            cursor.execute(
                "SELECT count(*) FROM avaliacoes_validacao "
                "WHERE id_criterio=%s AND (referencia_conferida OR executado)",
                (criterio[0],),
            )
            preenchidas = cursor.fetchone()[0]
        outros_antes = _linhas_outros_criterios(conexao, criterio[0])

    if criterio[2] != "PENDENTE" or criterio[3].strip() != definicao.assinatura_funcao:
        raise RuntimeError(f"Estado inicial do critério inesperado: {criterio!r}")
    if len(amostras) != 200 or preenchidas != 0:
        raise RuntimeError("As 200 avaliações novas não estão inicialmente vazias.")

    backup, sha256, itens_backup = _backup(configuracao)
    positivos_esperados = 0
    with abrir_conexao(configuracao) as conexao:
        for linha in amostras:
            esperado = referencias_padroes(tuple(linha[1:]))[CODIGO]
            positivos_esperados += esperado
            aprovar_referencia_padrao(
                conexao,
                id_resultado=linha[0],
                id_criterio=criterio[0],
                id_padrao=criterio[1] if esperado else None,
                origem="TESTE_AUTOMATIZADO",
                revisor="oráculo independente 8.7-R",
                observacao="Exatamente duas linhas distintas no volante 6x10.",
            )
        conexao.commit()

        detector = resolver_funcao_detectora(criterio[4])
        aprovadas = 0
        with conexao.transaction(), conexao.cursor() as cursor:
            cursor.execute(
                "SELECT a.id_resultado, a.estado_padrao_esperado, "
                "a.id_padrao_esperado, r.res_01, r.res_02, r.res_03, r.res_04, "
                "r.res_05, r.res_06 FROM avaliacoes_validacao a "
                "JOIN amostras_validacao am USING (id_resultado) "
                "JOIN resultados r USING (id_resultado) "
                "WHERE a.id_criterio=%s AND am.ativo ORDER BY am.ordem FOR UPDATE OF a",
                (criterio[0],),
            )
            for linha in cursor.fetchall():
                estado, id_calculado, aprovado = comparar_resultado_padrao(
                    estado_esperado=linha[1],
                    id_padrao_esperado=linha[2],
                    detectado=detector(tuple(linha[3:])),
                    id_padrao_criterio=criterio[1],
                )
                cursor.execute(
                    "UPDATE avaliacoes_validacao SET estado_padrao_calculado=%s, "
                    "id_padrao_calculado=%s, executado=TRUE, assinatura_executada=%s, "
                    "aprovado=%s, calculado_em=CURRENT_TIMESTAMP "
                    "WHERE id_resultado=%s AND id_criterio=%s",
                    (estado, id_calculado, definicao.assinatura_funcao, aprovado,
                     linha[0], criterio[0]),
                )
                aprovadas += aprovado == "S"
            cursor.execute(
                "UPDATE criterios_validacao SET estado=%s, atualizado_em=CURRENT_TIMESTAMP "
                "WHERE id_criterio=%s",
                ("APROVADO" if aprovadas == 200 else "REPROVADO", criterio[0]),
            )

        outros_depois = _linhas_outros_criterios(conexao, criterio[0])
        with conexao.cursor() as cursor:
            cursor.execute(
                "SELECT count(*) FILTER (WHERE referencia_conferida), "
                "count(*) FILTER (WHERE executado), "
                "count(*) FILTER (WHERE aprovado='S'), "
                "count(*) FILTER (WHERE aprovado='N'), "
                "count(*) FILTER (WHERE id_padrao_calculado IS NOT NULL) "
                "FROM avaliacoes_validacao WHERE id_criterio=%s",
                (criterio[0],),
            )
            resumo = cursor.fetchone()
            cursor.execute(
                "SELECT estado FROM criterios_validacao WHERE id_criterio=%s",
                (criterio[0],),
            )
            estado_final = cursor.fetchone()[0]

    if outros_depois != outros_antes:
        raise RuntimeError("Avaliações de outros critérios foram alteradas.")
    if resumo != (200, 200, 200, 0, positivos_esperados) or estado_final != "APROVADO":
        raise RuntimeError(f"Resultado final divergente: {resumo!r}, {estado_final!r}")

    print(json.dumps({
        "backup": str(backup),
        "backup_bytes": backup.stat().st_size,
        "backup_sha256": sha256,
        "backup_itens_catalogo": itens_backup,
        "criterio": CODIGO,
        "referencias_conferidas": resumo[0],
        "avaliacoes_executadas": resumo[1],
        "aprovadas": resumo[2],
        "divergencias": resumo[3],
        "amostras_com_duas_linhas": positivos_esperados,
        "estado_final": estado_final,
        "avaliacoes_dos_outros_criterios_preservadas": len(outros_depois),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
