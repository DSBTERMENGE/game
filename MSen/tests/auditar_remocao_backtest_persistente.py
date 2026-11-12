"""Auditoria somente leitura para retirada segura do backtest persistente."""

from __future__ import annotations

import json

from dotenv import load_dotenv

from msen.config import carregar_configuracao_banco
from msen.database import abrir_conexao


def main() -> None:
    load_dotenv()
    with abrir_conexao(carregar_configuracao_banco()) as conexao:
        with conexao.transaction():
            with conexao.cursor() as cursor:
                cursor.execute("SET TRANSACTION READ ONLY")
                cursor.execute(
                    "SELECT tipo_execucao,COUNT(*) FROM execucoes_pesquisa_selecao "
                    "GROUP BY tipo_execucao ORDER BY tipo_execucao"
                )
                execucoes = dict(cursor.fetchall())
                cursor.execute(
                    "SELECT e.tipo_execucao,COUNT(*) "
                    "FROM alvos_pesquisa_selecao a "
                    "JOIN execucoes_pesquisa_selecao e USING (id_execucao_selecao) "
                    "GROUP BY e.tipo_execucao ORDER BY e.tipo_execucao"
                )
                alvos = dict(cursor.fetchall())
                cursor.execute(
                    "SELECT e.tipo_execucao,COUNT(*) "
                    "FROM avaliacoes_dezenas_pesquisa d "
                    "JOIN alvos_pesquisa_selecao a USING (id_alvo_selecao) "
                    "JOIN execucoes_pesquisa_selecao e USING (id_execucao_selecao) "
                    "GROUP BY e.tipo_execucao ORDER BY e.tipo_execucao"
                )
                avaliacoes = dict(cursor.fetchall())
                cursor.execute(
                    "SELECT tc.table_name,kcu.column_name,ccu.table_name,"
                    "ccu.column_name,rc.delete_rule "
                    "FROM information_schema.table_constraints tc "
                    "JOIN information_schema.key_column_usage kcu "
                    "ON tc.constraint_name=kcu.constraint_name "
                    "AND tc.constraint_schema=kcu.constraint_schema "
                    "JOIN information_schema.referential_constraints rc "
                    "ON tc.constraint_name=rc.constraint_name "
                    "AND tc.constraint_schema=rc.constraint_schema "
                    "JOIN information_schema.constraint_column_usage ccu "
                    "ON rc.unique_constraint_name=ccu.constraint_name "
                    "AND rc.unique_constraint_schema=ccu.constraint_schema "
                    "WHERE tc.constraint_type='FOREIGN KEY' "
                    "AND (tc.table_name IN ('execucoes_pesquisa_selecao',"
                    "'alvos_pesquisa_selecao','avaliacoes_dezenas_pesquisa') "
                    "OR ccu.table_name IN ('execucoes_pesquisa_selecao',"
                    "'alvos_pesquisa_selecao','avaliacoes_dezenas_pesquisa')) "
                    "ORDER BY tc.table_name,kcu.column_name"
                )
                chaves = [dict(zip(
                    ("tabela", "coluna", "referencia", "coluna_referencia", "exclusao"),
                    linha,
                )) for linha in cursor.fetchall()]
                cursor.execute(
                    "SELECT tablename,indexname,indexdef FROM pg_indexes "
                    "WHERE schemaname='public' AND tablename IN "
                    "('execucoes_pesquisa_selecao','alvos_pesquisa_selecao',"
                    "'avaliacoes_dezenas_pesquisa') ORDER BY tablename,indexname"
                )
                indices = [dict(zip(
                    ("tabela", "indice", "definicao"), linha
                )) for linha in cursor.fetchall()]
                cursor.execute(
                    "SELECT con.conname,pg_get_constraintdef(con.oid) "
                    "FROM pg_constraint con "
                    "JOIN pg_class rel ON rel.oid=con.conrelid "
                    "WHERE rel.relname='execucoes_pesquisa_selecao' "
                    "ORDER BY con.conname"
                )
                restricoes_execucao = [dict(zip(
                    ("restricao", "definicao"), linha
                )) for linha in cursor.fetchall()]
                cursor.execute(
                    "SELECT COUNT(*) FROM lotes_jogos_selecao l "
                    "JOIN alvos_pesquisa_selecao a USING (id_alvo_selecao) "
                    "JOIN execucoes_pesquisa_selecao e USING (id_execucao_selecao) "
                    "WHERE e.tipo_execucao='BACKTEST'"
                )
                lotes_backtest = cursor.fetchone()[0]
    print(json.dumps({
        "execucoes_por_tipo": execucoes,
        "alvos_por_tipo": alvos,
        "avaliacoes_por_tipo": avaliacoes,
        "lotes_jogos_vinculados_a_backtest": lotes_backtest,
        "chaves_estrangeiras": chaves,
        "indices": indices,
        "restricoes_execucao": restricoes_execucao,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
