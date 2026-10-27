"""Valida a migração de grupos exclusivamente em database temporário."""

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


MIGRACOES = Path(__file__).resolve().parents[2] / "database" / "migrations"
SCHEMA = Path(__file__).resolve().parents[2] / "database" / "schema_postgresql.sql"


def preparar_estrutura_anterior(nome_database: str) -> None:
    """Cria a estrutura 001–003 e inclui estatísticas antes da migração 004."""

    nome = validar_nome(nome_database)
    configuracao_base = carregar_configuracao_banco()
    criar_vazio(configuracao_base, nome)
    configuracao = replace(configuracao_base, nome=nome)
    with tempfile.TemporaryDirectory() as pasta:
        pasta_migracoes = Path(pasta)
        for caminho in sorted(MIGRACOES.glob("00[1-3]_*.sql")):
            shutil.copy2(caminho, pasta_migracoes / caminho.name)
        executar_migracoes(configuracao, pasta_migracoes)

    with conectar(configuracao, nome) as conexao:
        with conexao.cursor() as cursor:
            cursor.execute(
                "UPDATE padroes SET num_oco = 2, intervalo_medio = 15, "
                "desv_padrao = 0 WHERE padrao_cod = 'PD_001'"
            )
            cursor.execute(
                "INSERT INTO padroes (padrao_cod, padrao_nome, padrao_descr) "
                "VALUES "
                "('PD_004', 'Duas dezenas na mesma coluna', 'Teste'), "
                "('PD_005', 'Três dezenas na mesma coluna', 'Teste'), "
                "('PD_006', 'Mais de três dezenas na mesma coluna', 'Teste')"
            )
            cursor.execute("SELECT SETVAL('padroes_codigo_seq', 6, TRUE)")
        conexao.commit()


def aplicar_migracao_atual(nome_database: str) -> None:
    """Aplica ao database preparado apenas as migrações ainda pendentes."""

    nome = validar_nome(nome_database)
    configuracao = replace(carregar_configuracao_banco(), nome=nome)
    executar_migracoes(configuracao, MIGRACOES)


def inserir_padrao_desconhecido(nome_database: str) -> None:
    """Inclui um padrão legado sem classificação para testar a reversão."""

    nome = validar_nome(nome_database)
    configuracao = replace(carregar_configuracao_banco(), nome=nome)
    with conectar(configuracao, nome) as conexao:
        with conexao.cursor() as cursor:
            cursor.execute(
                "INSERT INTO padroes (padrao_cod, padrao_nome, padrao_descr) "
                "VALUES ('PD_007', 'Padrão desconhecido', 'Sem grupo aprovado')"
            )
        conexao.commit()


def validar_reversao(nome_database: str) -> dict[str, object]:
    """Confirma que uma migração rejeitada preservou integralmente a versão 003."""

    nome = validar_nome(nome_database)
    configuracao = replace(carregar_configuracao_banco(), nome=nome)
    with conectar(configuracao, nome) as conexao:
        with conexao.cursor() as cursor:
            cursor.execute(
                "SELECT table_name FROM information_schema.tables "
                "WHERE table_schema = 'public' "
                "AND table_name IN ('padroes', 'padroes_grupo', 'padroes_subgrupo')"
            )
            tabelas = tuple(sorted(linha[0] for linha in cursor.fetchall()))
            cursor.execute("SELECT versao FROM schema_migrations ORDER BY versao")
            versoes = tuple(linha[0] for linha in cursor.fetchall())
            cursor.execute("SELECT count(*) FROM padroes")
            quantidade = cursor.fetchone()[0]
    if tabelas != ("padroes",) or versoes != ("001", "002", "003") or quantidade != 7:
        raise AssertionError(
            f"Reversão incompleta: tabelas={tabelas}, versões={versoes}, "
            f"padrões={quantidade}"
        )
    return {"tabelas": list(tabelas), "migracoes": list(versoes), "padroes": quantidade}


def testar_schema_canonico(nome_database: str) -> dict[str, int]:
    """Executa o esquema completo em database efêmero e remove-o ao final."""

    nome = validar_nome(nome_database)
    configuracao_base = carregar_configuracao_banco()
    criar_vazio(configuracao_base, nome)
    try:
        configuracao = replace(configuracao_base, nome=nome)
        with conectar(configuracao, nome) as conexao:
            with conexao.cursor() as cursor:
                cursor.execute(SCHEMA.read_text(encoding="utf-8"))
                cursor.execute("SELECT count(*) FROM padroes_grupo")
                grupos = cursor.fetchone()[0]
                cursor.execute("SELECT count(*) FROM padroes_subgrupo")
                padroes = cursor.fetchone()[0]
            conexao.commit()
        return {"grupos": grupos, "padroes": padroes}
    finally:
        remover(configuracao_base, nome)


def validar_estrutura(nome_database: str) -> dict[str, object]:
    """Confere estrutura, dados preservados e proteções da migração 004."""

    nome = validar_nome(nome_database)
    configuracao = replace(carregar_configuracao_banco(), nome=nome)
    with conectar(configuracao, nome) as conexao:
        with conexao.cursor() as cursor:
            cursor.execute(
                "SELECT table_name FROM information_schema.tables "
                "WHERE table_schema = 'public' "
                "AND table_name IN ('padroes', 'padroes_grupo', "
                "'padroes_subgrupo') ORDER BY table_name"
            )
            tabelas = tuple(linha[0] for linha in cursor.fetchall())
            if tabelas != ("padroes_grupo", "padroes_subgrupo"):
                raise AssertionError(f"Tabelas inesperadas: {tabelas!r}")

            cursor.execute(
                "SELECT versao FROM schema_migrations ORDER BY versao"
            )
            versoes = tuple(linha[0] for linha in cursor.fetchall())
            if versoes != ("001", "002", "003", "004", "005"):
                raise AssertionError(f"Migrações inesperadas: {versoes!r}")

            cursor.execute(
                "SELECT g.grupo_cod, p.padrao_cod, p.padrao_nome, "
                "p.num_oco, p.intervalo_medio, p.desv_padrao "
                "FROM padroes_subgrupo p "
                "JOIN padroes_grupo g USING (id_grupo) "
                "ORDER BY p.padrao_cod"
            )
            padroes = tuple(cursor.fetchall())
            if tuple(linha[:3] for linha in padroes) != (
                ("PG_001", "PD_001", "Duas dezenas sequenciais"),
                ("PG_001", "PD_002", "Três dezenas sequenciais"),
                ("PG_001", "PD_003", "Mais de três dezenas sequenciais"),
                ("PG_002", "PD_004", "Duas dezenas na mesma coluna"),
                ("PG_002", "PD_005", "Três dezenas na mesma coluna"),
                ("PG_002", "PD_006", "Mais de três dezenas na mesma coluna"),
            ):
                raise AssertionError(f"Padrões não preservados: {padroes!r}")
            if padroes[0][3:] != (2, 15, 0):
                raise AssertionError(
                    f"Estatísticas do PD_001 não preservadas: {padroes[0][3:]!r}"
                )

        rejeitados: list[str] = []
        comandos_invalidos = (
            (
                "INSERT INTO padroes_grupo "
                "(grupo_cod, grupo_nome, grupo_descr) VALUES "
                "('PG_003', ' dezenas SEQUENCIAIS ', 'Duplicado')",
                "grupo_nome_normalizado",
            ),
            (
                "DELETE FROM padroes_grupo WHERE grupo_cod = 'PG_001'",
                "grupo_com_padroes",
            ),
            (
                "INSERT INTO padroes_subgrupo "
                "(id_grupo, padrao_cod, padrao_nome, padrao_descr) VALUES "
                "(999999, 'PD_010', 'Teste', 'Grupo inexistente')",
                "grupo_inexistente",
            ),
            (
                "INSERT INTO padroes_subgrupo "
                "(id_grupo, padrao_cod, padrao_nome, padrao_descr) "
                "SELECT id_grupo, 'PD_011', ' duas dezenas SEQUENCIAIS ', "
                "'Duplicado' FROM padroes_grupo WHERE grupo_cod = 'PG_001'",
                "padrao_nome_no_grupo",
            ),
        )
        for comando, caso in comandos_invalidos:
            try:
                with conexao.transaction():
                    with conexao.cursor() as cursor:
                        cursor.execute(comando)
            except psycopg.IntegrityError:
                rejeitados.append(caso)
            else:
                raise AssertionError(f"O banco aceitou o caso inválido: {caso}")

        with conexao.cursor() as cursor:
            cursor.execute(
                "SELECT last_value, is_called FROM padroes_grupo_codigo_seq"
            )
            sequencia_grupo = cursor.fetchone()
            cursor.execute(
                "SELECT last_value, is_called FROM padroes_subgrupo_codigo_seq"
            )
            sequencia_padrao = cursor.fetchone()

    return {
        "tabelas": list(tabelas),
        "migracoes": list(versoes),
        "padroes_preservados": len(padroes),
        "restricoes_rejeitadas": rejeitados,
        "sequencia_grupo": list(sequencia_grupo),
        "sequencia_padrao": list(sequencia_padrao),
    }


def main() -> None:
    """Executa a validação para o database temporário informado."""

    load_dotenv()
    if len(sys.argv) != 3 or sys.argv[1] not in {
        "preparar",
        "aplicar",
        "validar",
        "schema",
        "inserir_desconhecido",
        "validar_reversao",
    }:
        raise SystemExit(
            "Uso: validar_migracao_grupos_padroes.py "
            "preparar|aplicar|validar NOME_DATABASE_TEMPORARIO"
        )
    operacao, nome = sys.argv[1], sys.argv[2]
    if operacao == "preparar":
        preparar_estrutura_anterior(nome)
    elif operacao == "aplicar":
        aplicar_migracao_atual(nome)
    elif operacao == "schema":
        print(json.dumps(testar_schema_canonico(nome), ensure_ascii=False))
    elif operacao == "inserir_desconhecido":
        inserir_padrao_desconhecido(nome)
    elif operacao == "validar_reversao":
        print(json.dumps(validar_reversao(nome), ensure_ascii=False))
    else:
        print(json.dumps(validar_estrutura(nome), ensure_ascii=False))


if __name__ == "__main__":
    main()
