"""Valida a migração 034 exclusivamente em database PostgreSQL temporário."""

from dataclasses import replace
import json
from pathlib import Path
import shutil
import sys
import tempfile

from dotenv import load_dotenv
import psycopg

from msen.config import carregar_configuracao_banco
from msen.database import executar_migracoes
from suporte_banco_integracao import conectar, criar_vazio, remover, validar_nome


RAIZ = Path(__file__).resolve().parents[2]
MIGRACOES = RAIZ / "database" / "migrations"


def _copiar_migracoes(destino: Path, versao_final: int) -> None:
    for caminho in sorted(MIGRACOES.glob("[0-9][0-9][0-9]_*.sql")):
        if int(caminho.name[:3]) <= versao_final:
            shutil.copy2(caminho, destino / caminho.name)


def _preparar_catalogo_anterior(configuracao, nome_database: str) -> None:
    grupos = (
        ("PG_004", "Dezenas em diagonal à esquerda", "Diagonal à esquerda."),
        ("PG_006", "Dezenas em diagonal à direita", "Diagonal à direita."),
        ("PG_007", "Dezenas em duas linhas", "Duas linhas."),
        ("PG_008", "1 linha e 1 coluna", "Uma linha e uma coluna."),
        ("PG_009", "Dezenas em duas Colunas", "Duas colunas."),
    )
    padroes = (
        ("PG_008", "PD_010", "6 dezenas distribuidas em L , T ou Cruz", "L, T ou cruz."),
        ("PG_007", "PD_011", "Padrão 2L", "Duas linhas."),
        ("PG_009", "PD_012", "Dezenas em 2H", "Duas colunas."),
    )
    with conectar(configuracao, nome_database) as conexao:
        with conexao.cursor() as cursor:
            cursor.executemany(
                "INSERT INTO padroes_grupo (grupo_cod, grupo_nome, grupo_descr) "
                "VALUES (%s, %s, %s)",
                grupos,
            )
            cursor.executemany(
                "INSERT INTO padroes_subgrupo "
                "(id_grupo, padrao_cod, padrao_nome, padrao_descr) "
                "SELECT id_grupo, %s, %s, %s FROM padroes_grupo WHERE grupo_cod = %s",
                tuple(
                    (codigo, nome, descricao, grupo)
                    for grupo, codigo, nome, descricao in padroes
                ),
            )
            cursor.execute("SELECT SETVAL('padroes_grupo_codigo_seq', 9, TRUE)")
            cursor.execute("SELECT SETVAL('padroes_subgrupo_codigo_seq', 12, TRUE)")
        conexao.commit()


def _fotografar_preservados(cursor) -> tuple[tuple[object, ...], ...]:
    cursor.execute(
        "SELECT g.grupo_cod, g.grupo_nome, p.padrao_cod, p.padrao_nome, "
        "p.funcao_detectora, p.num_oco, p.total_sorteios, p.percentual_ocorrencia "
        "FROM padroes_grupo g LEFT JOIN padroes_subgrupo p USING (id_grupo) "
        "WHERE g.grupo_cod NOT IN ('PG_004', 'PG_006') "
        "ORDER BY g.grupo_cod, p.padrao_cod"
    )
    return tuple(cursor.fetchall())


def _exigir_rejeicao(conexao, comando: str, parametros: tuple[object, ...]) -> None:
    try:
        with conexao.transaction():
            with conexao.cursor() as cursor:
                cursor.execute(comando, parametros)
    except psycopg.IntegrityError:
        return
    raise AssertionError("O PostgreSQL aceitou um contrato de grupo inválido.")


def _validar_estado(configuracao, nome_database: str, preservados):
    with conectar(configuracao, nome_database) as conexao:
        with conexao.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM padroes_grupo")
            grupos = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM padroes_subgrupo")
            padroes = cursor.fetchone()[0]
            cursor.execute(
                "SELECT g.grupo_nome, g.tipo_avaliacao, g.funcao_analisadora, "
                "p.padrao_cod, p.padrao_nome, p.funcao_detectora, "
                "POSITION('Ver tuplas' IN p.padrao_descr) > 0 "
                "FROM padroes_grupo g JOIN padroes_subgrupo p USING (id_grupo) "
                "WHERE g.grupo_cod = 'PG_004'"
            )
            diagonal = cursor.fetchone()
            cursor.execute("SELECT COUNT(*) FROM padroes_grupo WHERE grupo_cod = 'PG_006'")
            grupo_obsoleto = cursor.fetchone()[0]
            cursor.execute(
                "SELECT COUNT(*) FROM padroes_subgrupo "
                "WHERE padrao_cod BETWEEN 'PD_014' AND 'PD_026'"
            )
            padroes_obsoletos = cursor.fetchone()[0]
            preservados_depois = _fotografar_preservados(cursor)

        if grupos != 10 or padroes != 36:
            raise AssertionError(f"Totais inesperados: grupos={grupos}, padrões={padroes}.")
        if diagonal != (
            "Arranjos diagonais",
            "CATEGORICO_PERCENTUAL",
            "msen.padroes.diagonais.analisar_assinaturas_diagonais",
            "PD_013",
            "Configurações diagonais xDyE",
            None,
            True,
        ):
            raise AssertionError(f"Filtro diagonal divergente: {diagonal}.")
        if grupo_obsoleto or padroes_obsoletos:
            raise AssertionError("O catálogo diagonal obsoleto não foi removido.")
        if preservados_depois != preservados:
            raise AssertionError("A migração alterou registros fora do catálogo diagonal.")

        _exigir_rejeicao(
            conexao,
            "INSERT INTO padroes_grupo "
            "(grupo_cod, grupo_nome, grupo_descr, tipo_avaliacao, funcao_analisadora) "
            "VALUES (%s, %s, %s, 'BOOLEANO', %s)",
            ("PG_990", "Inválido booleano", "Teste.", "msen.padroes.funcao"),
        )
        _exigir_rejeicao(
            conexao,
            "INSERT INTO padroes_grupo "
            "(grupo_cod, grupo_nome, grupo_descr, tipo_avaliacao) "
            "VALUES (%s, %s, %s, 'CATEGORICO_PERCENTUAL')",
            ("PG_991", "Inválido categórico", "Teste."),
        )
    return {"grupos": grupos, "padroes": padroes, "filtro_diagonal": diagonal[:5]}


def validar(nome_database: str) -> dict[str, object]:
    nome = validar_nome(nome_database)
    configuracao_base = carregar_configuracao_banco()
    criar_vazio(configuracao_base, nome)
    configuracao = replace(configuracao_base, nome=nome)
    try:
        with tempfile.TemporaryDirectory() as pasta:
            anteriores = Path(pasta)
            _copiar_migracoes(anteriores, 32)
            executar_migracoes(configuracao, anteriores)

        _preparar_catalogo_anterior(configuracao, nome)
        with tempfile.TemporaryDirectory() as pasta:
            ate_33 = Path(pasta)
            _copiar_migracoes(ate_33, 33)
            executar_migracoes(configuracao, ate_33)

        with conectar(configuracao, nome) as conexao:
            with conexao.cursor() as cursor:
                preservados = _fotografar_preservados(cursor)

        primeira = executar_migracoes(configuracao, MIGRACOES)
        estado = _validar_estado(configuracao, nome, preservados)
        segunda = executar_migracoes(configuracao, MIGRACOES)
        if primeira.aplicadas != ("034",):
            raise AssertionError(f"Primeira execução inesperada: {primeira}.")
        if segunda.aplicadas:
            raise AssertionError(f"A migração foi reaplicada: {segunda}.")
        return {
            "migracao_aplicada": list(primeira.aplicadas),
            "segunda_execucao_sem_reaplicar": True,
            "estado": estado,
        }
    finally:
        remover(configuracao_base, nome)


def main() -> None:
    load_dotenv()
    if len(sys.argv) != 2:
        raise SystemExit("Uso: validar_migracao_arranjos_diagonais.py NOME_TEMPORARIO")
    print(json.dumps(validar(sys.argv[1]), ensure_ascii=False, indent=2, default=str))


if __name__ == "__main__":
    main()
