"""Valida a migração 033 exclusivamente em database PostgreSQL temporário."""

from dataclasses import replace
import json
from pathlib import Path
import shutil
import sys
import tempfile

from dotenv import load_dotenv

from msen.config import carregar_configuracao_banco
from msen.database import executar_migracoes
from suporte_banco_integracao import conectar, criar_vazio, remover, validar_nome


RAIZ = Path(__file__).resolve().parents[2]
MIGRACOES = RAIZ / "database" / "migrations"


def _copiar_migracoes(destino: Path, versao_final: int) -> None:
    for caminho in sorted(MIGRACOES.glob("[0-9][0-9][0-9]_*.sql")):
        if int(caminho.name[:3]) <= versao_final:
            shutil.copy2(caminho, destino / caminho.name)


def _preparar_catalogo_atual(configuracao, nome_database: str) -> None:
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
                tuple((codigo, nome, descricao, grupo) for grupo, codigo, nome, descricao in padroes),
            )
            cursor.execute("SELECT SETVAL('padroes_grupo_codigo_seq', 9, TRUE)")
            cursor.execute("SELECT SETVAL('padroes_subgrupo_codigo_seq', 12, TRUE)")
        conexao.commit()


def _fotografar(cursor, limite_codigo: int | None = None):
    condicao = "" if limite_codigo is None else "WHERE SUBSTRING(p.padrao_cod FROM 4)::INT <= %s"
    parametros = () if limite_codigo is None else (limite_codigo,)
    cursor.execute(
        "SELECT g.grupo_cod, p.padrao_cod, p.padrao_nome, p.padrao_descr, "
        "p.funcao_detectora FROM padroes_subgrupo p "
        "JOIN padroes_grupo g USING (id_grupo) " + condicao + " ORDER BY p.padrao_cod",
        parametros,
    )
    return tuple(cursor.fetchall())


def _validar_resultado(configuracao, nome_database: str, fotografia_inicial):
    esperados = {
        "PG_004": 7,
        "PG_006": 7,
        "PG_007": 6,
        "PG_008": 4,
        "PG_009": 6,
        "Alinhamentos e linhas poligonais": 4,
        "Circularidade": 4,
        "Arcos e elipses": 2,
    }
    with conectar(configuracao, nome_database) as conexao:
        with conexao.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM padroes_grupo")
            grupos = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM padroes_subgrupo")
            padroes = cursor.fetchone()[0]
            cursor.execute(
                "SELECT COUNT(*) FROM padroes_subgrupo "
                "WHERE SUBSTRING(padrao_cod FROM 4)::INT >= 13 "
                "AND funcao_detectora IS NULL"
            )
            novos_sem_funcao = cursor.fetchone()[0]
            if _fotografar(cursor, 12) != fotografia_inicial:
                raise AssertionError("A migração alterou padrões que já existiam.")

            contagens = {}
            for chave in esperados:
                cursor.execute(
                    "SELECT COUNT(*) FROM padroes_subgrupo p "
                    "JOIN padroes_grupo g USING (id_grupo) "
                    "WHERE g.grupo_cod = %s OR g.grupo_nome = %s",
                    (chave, chave),
                )
                contagens[chave] = cursor.fetchone()[0]

    if grupos != 11 or padroes != 49 or novos_sem_funcao != 37:
        raise AssertionError(
            f"Totais inesperados: grupos={grupos}, padrões={padroes}, "
            f"novos_sem_funcao={novos_sem_funcao}."
        )
    if contagens != esperados:
        raise AssertionError(f"Associações inesperadas: {contagens}.")
    return {
        "grupos_totais": grupos,
        "padroes_totais": padroes,
        "padroes_novos": 37,
        "novos_sem_funcao": novos_sem_funcao,
        "associacoes": contagens,
    }


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

        _preparar_catalogo_atual(configuracao, nome)
        with conectar(configuracao, nome) as conexao:
            with conexao.cursor() as cursor:
                fotografia_inicial = _fotografar(cursor, 12)

        primeira = executar_migracoes(configuracao, MIGRACOES)
        resultado = _validar_resultado(configuracao, nome, fotografia_inicial)

        with conectar(configuracao, nome, autocommit=True) as conexao:
            conexao.execute((MIGRACOES / "033_expandir_catalogo_padroes_geometricos.sql").read_text(encoding="utf-8"))
        repeticao = _validar_resultado(configuracao, nome, fotografia_inicial)

        return {
            "migracao_aplicada": list(primeira.aplicadas),
            "primeira_execucao": resultado,
            "repeticao_sem_duplicar": repeticao == resultado,
        }
    finally:
        remover(configuracao_base, nome)


def main() -> None:
    load_dotenv()
    if len(sys.argv) != 2:
        raise SystemExit("Uso: validar_migracao_expansao_padroes.py NOME_TEMPORARIO")
    print(json.dumps(validar(sys.argv[1]), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
