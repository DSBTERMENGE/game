"""Valida a migração 008 exclusivamente em database PostgreSQL temporário."""

from dataclasses import replace
import json
from pathlib import Path
import shutil
import sys
import tempfile

from dotenv import load_dotenv
import psycopg

from msen.config import carregar_configuracao_banco
from msen.database import ErroMigracao, executar_migracoes
from suporte_banco_integracao import conectar, criar_vazio, remover, validar_nome


RAIZ = Path(__file__).resolve().parents[2]
MIGRACOES = RAIZ / "database" / "migrations"
MIGRACAO_FALHA = (
    Path(__file__).resolve().parent / "fixtures" / "migrations" / "009_falha_controlada.sql"
)


def _copiar_migracoes(destino: Path, versao_final: int) -> None:
    """Copia para o ensaio somente as migrações até a versão solicitada."""
    for caminho in sorted(MIGRACOES.glob("[0-9][0-9][0-9]_*.sql")):
        if int(caminho.name[:3]) <= versao_final:
            shutil.copy2(caminho, destino / caminho.name)


def _inserir_resultado(cursor: psycopg.Cursor, numero_ap: int) -> int:
    """Inclui um resultado mínimo válido e devolve seu identificador."""
    cursor.execute(
        "INSERT INTO resultados ("
        "data_resultado, numero_ap, res_01, res_02, res_03, res_04, res_05, res_06, "
        "soma_res, media_aritmetica_res, mediana_res, desvio_padrao_media, "
        "media_coordenada_x, media_coordenada_y"
        ") VALUES (DATE '2026-10-28', %s, 1, 2, 3, 4, 5, 6, "
        "21, 3.5, 3.5, 1.707825, 2.5, 0) RETURNING id_resultado",
        (numero_ap,),
    )
    return cursor.fetchone()[0]


def _esperar_rejeicao(
    conexao: psycopg.Connection, comando: str, parametros: tuple[object, ...], caso: str
) -> str:
    """Executa um caso inválido e exige rejeição por integridade do PostgreSQL."""
    try:
        with conexao.transaction():
            with conexao.cursor() as cursor:
                cursor.execute(comando, parametros)
    except psycopg.IntegrityError:
        return caso
    raise AssertionError(f"O PostgreSQL aceitou o caso inválido: {caso}")


def _validar_restricoes(configuracao, nome: str) -> list[str]:
    """Confirma estados válidos e rejeita combinações estruturais incoerentes."""
    rejeitados: list[str] = []
    with conectar(configuracao, nome) as conexao:
        with conexao.cursor() as cursor:
            resultado_1 = _inserir_resultado(cursor, 900001)
            resultado_2 = _inserir_resultado(cursor, 900002)
            cursor.execute(
                "SELECT g.id_grupo, p.id_padrao FROM padroes_grupo g "
                "JOIN padroes_subgrupo p USING (id_grupo) "
                "WHERE g.grupo_cod = 'PG_001' AND p.padrao_cod = 'PD_001'"
            )
            grupo_1, padrao_1 = cursor.fetchone()
            cursor.execute(
                "SELECT g.id_grupo, p.id_padrao FROM padroes_grupo g "
                "JOIN padroes_subgrupo p USING (id_grupo) "
                "WHERE g.grupo_cod = 'PG_002' AND p.padrao_cod = 'PD_004'"
            )
            grupo_2, padrao_2 = cursor.fetchone()
            cursor.execute(
                "INSERT INTO resultado_classificacao_padrao "
                "(id_resultado, id_grupo, id_padrao, estado_classificacao) "
                "VALUES (%s, %s, %s, 'PADRAO_IDENTIFICADO')",
                (resultado_1, grupo_1, padrao_1),
            )
            cursor.execute(
                "INSERT INTO resultado_classificacao_padrao "
                "(id_resultado, id_grupo, id_padrao, estado_classificacao) "
                "VALUES (%s, %s, NULL, 'SEM_CORRESPONDENCIA')",
                (resultado_1, grupo_2),
            )
        conexao.commit()

        inserir = (
            "INSERT INTO resultado_classificacao_padrao "
            "(id_resultado, id_grupo, id_padrao, estado_classificacao, versao_calculo) "
            "VALUES (%s, %s, %s, %s, %s)"
        )
        casos = (
            ((resultado_1, grupo_1, padrao_1, "PADRAO_IDENTIFICADO", 1), "resultado_grupo_duplicado"),
            ((resultado_2, grupo_1, None, "PADRAO_IDENTIFICADO", 1), "padrao_obrigatorio"),
            ((resultado_2, grupo_1, padrao_1, "SEM_CORRESPONDENCIA", 1), "sem_correspondencia_sem_padrao"),
            ((resultado_2, grupo_1, padrao_2, "PADRAO_IDENTIFICADO", 1), "padrao_de_outro_grupo"),
            ((resultado_2, grupo_1, padrao_1, "PADRAO_IDENTIFICADO", 0), "versao_positiva"),
        )
        for parametros, caso in casos:
            rejeitados.append(_esperar_rejeicao(conexao, inserir, parametros, caso))

        with conexao.cursor() as cursor:
            cursor.execute("DELETE FROM resultados WHERE id_resultado = %s", (resultado_1,))
            cursor.execute(
                "SELECT count(*) FROM resultado_classificacao_padrao WHERE id_resultado = %s",
                (resultado_1,),
            )
            if cursor.fetchone()[0] != 0:
                raise AssertionError("A exclusão do resultado não removeu suas classificações.")
        conexao.commit()
    return rejeitados


def _validar_rollback(configuracao, nome: str) -> str:
    """Prova que uma migração com falha não deixa tabela nem versão registrada."""
    with tempfile.TemporaryDirectory() as pasta:
        destino = Path(pasta)
        _copiar_migracoes(destino, 8)
        shutil.copy2(MIGRACAO_FALHA, destino / MIGRACAO_FALHA.name)
        try:
            executar_migracoes(configuracao, destino)
        except ErroMigracao as erro:
            if erro.codigo != "MIGRACAO_FALHOU" or erro.versao != "009":
                raise AssertionError(f"Falha inesperada: {erro.codigo}/{erro.versao}") from erro
        else:
            raise AssertionError("A migração de falha controlada foi aceita.")

    with conectar(configuracao, nome) as conexao:
        with conexao.cursor() as cursor:
            cursor.execute("SELECT to_regclass('public.teste_rollback_migracao_16_3')")
            if cursor.fetchone()[0] is not None:
                raise AssertionError("A tabela da migração defeituosa não sofreu rollback.")
            cursor.execute("SELECT count(*) FROM schema_migrations WHERE versao = '009'")
            if cursor.fetchone()[0] != 0:
                raise AssertionError("A versão defeituosa foi registrada.")
    return "tabela_e_versao_009_ausentes"


def validar(nome_database: str) -> dict[str, object]:
    """Executa todo o ensaio da migração 008 e sempre remove o database."""
    nome = validar_nome(nome_database)
    configuracao_base = carregar_configuracao_banco()
    criar_vazio(configuracao_base, nome)
    configuracao = replace(configuracao_base, nome=nome)
    try:
        with tempfile.TemporaryDirectory() as pasta:
            anteriores = Path(pasta)
            _copiar_migracoes(anteriores, 7)
            relatorio_anterior = executar_migracoes(configuracao, anteriores)

        relatorio_primeira = executar_migracoes(configuracao, MIGRACOES)
        relatorio_segunda = executar_migracoes(configuracao, MIGRACOES)
        if relatorio_primeira.aplicadas != ("008",):
            raise AssertionError(f"Primeira execução inesperada: {relatorio_primeira}")
        todas = tuple(f"{numero:03d}" for numero in range(1, 9))
        if relatorio_segunda.aplicadas or relatorio_segunda.ja_aplicadas != todas:
            raise AssertionError(f"Segunda execução inesperada: {relatorio_segunda}")

        return {
            "migracoes_estrutura_anterior": list(relatorio_anterior.aplicadas),
            "aplicadas_primeira_execucao": list(relatorio_primeira.aplicadas),
            "ja_aplicadas_segunda_execucao": list(relatorio_segunda.ja_aplicadas),
            "restricoes_rejeitadas": _validar_restricoes(configuracao, nome),
            "cascade_resultado": "confirmado",
            "rollback": _validar_rollback(configuracao, nome),
        }
    finally:
        remover(configuracao_base, nome)


def main() -> None:
    load_dotenv()
    if len(sys.argv) != 2:
        raise SystemExit("Uso: validar_migracao_classificacao_padrao.py NOME_TEMPORARIO")
    print(json.dumps(validar(sys.argv[1]), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
