"""Valida a migração 026 no Games e desfaz todos os dados de ensaio."""

from decimal import Decimal

from dotenv import load_dotenv
from psycopg.errors import RaiseException, UniqueViolation

from msen.config import carregar_configuracao_banco
from msen.database import abrir_conexao


load_dotenv()
with abrir_conexao(carregar_configuracao_banco()) as conexao, conexao.cursor() as cursor:
    cursor.execute("SELECT id_alvo_selecao FROM alvos_pesquisa_selecao ORDER BY id_alvo_selecao LIMIT 1")
    id_alvo = cursor.fetchone()[0]
    cursor.execute(
        "INSERT INTO formacoes_jogos_selecao ("
        "id_alvo_selecao,quantidade_dezenas,quantidade_combinacoes_brutas,"
        "quantidade_jogos_solicitada,valor_unitario,versao_formacao,"
        "fotografia_screener_json,assinatura_screener,versao_classificador,"
        "assinatura_classificador,chave_idempotencia) "
        "VALUES (%s,16,8008,100,5.00,1,'{}'::jsonb,%s,1,%s,%s) "
        "RETURNING id_formacao_jogos,valor_maximo_previsto,valor_efetivo",
        (id_alvo, "a" * 64, "b" * 64, "c" * 64),
    )
    id_formacao, valor_previsto, valor_efetivo = cursor.fetchone()
    assert valor_previsto == Decimal("500.00")
    assert valor_efetivo == Decimal("0.00")

    cursor.execute("SAVEPOINT tentativa_duplicada")
    try:
        cursor.execute(
            "INSERT INTO formacoes_jogos_selecao ("
            "id_alvo_selecao,quantidade_dezenas,quantidade_combinacoes_brutas,"
            "quantidade_jogos_solicitada,valor_unitario,versao_formacao,"
            "fotografia_screener_json,assinatura_screener,versao_classificador,"
            "assinatura_classificador,chave_idempotencia) "
            "VALUES (%s,16,8008,100,5.00,1,'{}'::jsonb,%s,1,%s,%s)",
            (id_alvo, "a" * 64, "b" * 64, "c" * 64),
        )
        raise AssertionError("A chave idempotente repetida deveria falhar.")
    except UniqueViolation:
        cursor.execute("ROLLBACK TO SAVEPOINT tentativa_duplicada")

    cursor.execute("SAVEPOINT tentativa_alteracao")
    try:
        cursor.execute(
            "UPDATE formacoes_jogos_selecao SET valor_unitario=6.00 "
            "WHERE id_formacao_jogos=%s",
            (id_formacao,),
        )
        raise AssertionError("A configuração deveria ser imutável.")
    except RaiseException:
        cursor.execute("ROLLBACK TO SAVEPOINT tentativa_alteracao")

    conexao.rollback()

with abrir_conexao(carregar_configuracao_banco()) as conexao, conexao.cursor() as cursor:
    cursor.execute("SELECT COUNT(*) FROM formacoes_jogos_selecao")
    assert cursor.fetchone() == (0,)
    cursor.execute("SELECT COUNT(*) FROM jogos_finais_selecao")
    assert cursor.fetchone() == (0,)
    cursor.execute("SELECT versao FROM schema_migrations WHERE versao='027'")
    assert cursor.fetchone() == ("027",)
    cursor.execute(
        "SELECT column_name,numeric_precision,numeric_scale "
        "FROM information_schema.columns "
        "WHERE table_name='formacoes_jogos_selecao' "
        "AND column_name IN ('valor_maximo_previsto','valor_efetivo') "
        "ORDER BY column_name"
    )
    assert cursor.fetchall() == [
        ("valor_efetivo", 24, 2),
        ("valor_maximo_previsto", 24, 2),
    ]

print({
    "migracoes": "026 e 027",
    "valor_maximo_previsto": "500.00",
    "idempotencia": "protegida",
    "configuracao": "imutavel",
    "registros_de_ensaio": 0,
})
