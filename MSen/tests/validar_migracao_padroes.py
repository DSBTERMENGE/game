"""Valida a migração de padrões exclusivamente em database temporário de teste."""

from dataclasses import replace
import json
import sys

from dotenv import load_dotenv
import psycopg

from msen.config import carregar_configuracao_banco
from suporte_banco_integracao import conectar, validar_nome


COLUNAS_ESPERADAS = (
    ("id_padrao", "bigint", "NO"),
    ("padrao_cod", "character varying", "NO"),
    ("padrao_nome", "character varying", "NO"),
    ("padrao_descr", "text", "NO"),
    ("num_oco", "integer", "YES"),
    ("intervalo_medio", "numeric", "YES"),
    ("desv_padrao", "numeric", "YES"),
)


def validar_estrutura(nome_database: str) -> dict[str, object]:
    """Confere estrutura e restrições da tabela `padroes` no database indicado."""

    nome = validar_nome(nome_database)
    configuracao = replace(carregar_configuracao_banco(), nome=nome)
    with conectar(configuracao, nome) as conexao:
        with conexao.cursor() as cursor:
            cursor.execute(
                "SELECT column_name, data_type, is_nullable "
                "FROM information_schema.columns "
                "WHERE table_schema = 'public' AND table_name = 'padroes' "
                "ORDER BY ordinal_position"
            )
            colunas = tuple(cursor.fetchall())
            if colunas != COLUNAS_ESPERADAS:
                raise AssertionError(f"Colunas inesperadas: {colunas!r}")

            cursor.execute(
                "SELECT versao FROM schema_migrations ORDER BY versao"
            )
            versoes = tuple(linha[0] for linha in cursor.fetchall())
            if versoes != ("001", "002", "003"):
                raise AssertionError(f"Migrações inesperadas: {versoes!r}")

            cursor.execute(
                "INSERT INTO padroes (padrao_cod, padrao_nome, padrao_descr) "
                "VALUES ('PD_010', 'Pendente', 'Detector ainda pendente'), "
                "('PD_011', 'Nunca ocorreu', 'Analisado sem ocorrências')"
            )
            cursor.execute(
                "UPDATE padroes SET num_oco = 0 WHERE padrao_cod = 'PD_011'"
            )
            cursor.execute(
                "INSERT INTO padroes "
                "(padrao_cod, padrao_nome, padrao_descr, num_oco, "
                "intervalo_medio, desv_padrao) "
                "VALUES ('PD_012', 'Com intervalos', "
                "'Analisado com intervalos', 2, 15, 0)"
            )
        conexao.commit()

        invalidos = (
            (
                "INSERT INTO padroes (padrao_cod, padrao_nome, padrao_descr) "
                "VALUES ('P1', 'Código inválido', 'Teste')",
                "formato_codigo",
            ),
            (
                "INSERT INTO padroes (padrao_cod, padrao_nome, padrao_descr) "
                "VALUES ('PD_004', ' ', 'Teste')",
                "nome_vazio",
            ),
            (
                "INSERT INTO padroes "
                "(padrao_cod, padrao_nome, padrao_descr, num_oco) "
                "VALUES ('PD_005', 'Contagem inválida', 'Teste', -1)",
                "contagem_negativa",
            ),
            (
                "INSERT INTO padroes "
                "(padrao_cod, padrao_nome, padrao_descr, num_oco) "
                "VALUES ('PD_006', 'Estado incompleto', 'Teste', 2)",
                "estado_incompleto",
            ),
            (
                "INSERT INTO padroes (padrao_cod, padrao_nome, padrao_descr) "
                "VALUES ('PD_010', 'Código repetido', 'Teste')",
                "codigo_duplicado",
            ),
        )
        rejeitados: list[str] = []
        for comando, identificador in invalidos:
            try:
                with conexao.transaction():
                    with conexao.cursor() as cursor:
                        cursor.execute(comando)
            except psycopg.IntegrityError:
                rejeitados.append(identificador)
            else:
                raise AssertionError(f"O banco aceitou o caso inválido: {identificador}")

        with conexao.cursor() as cursor:
            cursor.execute(
                "SELECT count(*) FROM padroes WHERE padrao_cod LIKE 'PD_%'"
            )
            registros_validos = cursor.fetchone()[0]

    return {
        "colunas": len(colunas),
        "migracoes": list(versoes),
        "registros_validos": registros_validos,
        "restricoes_rejeitadas": rejeitados,
    }


def main() -> None:
    """Executa a validação solicitada pela linha de comando."""

    load_dotenv()
    if len(sys.argv) != 2:
        raise SystemExit("Uso: validar_migracao_padroes.py NOME_DATABASE_TEMPORARIO")
    print(json.dumps(validar_estrutura(sys.argv[1]), ensure_ascii=False))


if __name__ == "__main__":
    main()
