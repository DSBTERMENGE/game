"""Audita, sem alterar dados, as leituras necessárias ao backtest temporário."""

from __future__ import annotations

import json

from dotenv import load_dotenv

from msen.config import carregar_configuracao_banco
from msen.database import abrir_conexao


TABELAS_AUDITADAS = (
    "resultados",
    "configuracoes_pesquisa_selecao",
    "historico_frequencia_dezenas",
    "geracoes_frequencia_dezenas",
)


def _resumo_plano(plano: list[dict[str, object]]) -> dict[str, object]:
    raiz = plano[0]
    operacao = raiz["Plan"]
    return {
        "operacao_raiz": operacao["Node Type"],
        "linhas": operacao["Actual Rows"],
        "tempo_ms": raiz["Execution Time"],
    }


def main() -> None:
    """Imprime somente metadados técnicos, sem host, usuário ou credenciais."""

    load_dotenv()
    configuracao = carregar_configuracao_banco()
    saida: dict[str, object] = {}

    with abrir_conexao(configuracao) as conexao:
        with conexao.cursor() as cursor:
            cursor.execute(
                "SELECT COUNT(*), MIN(numero_ap), MAX(numero_ap) FROM resultados"
            )
            quantidade, minimo, maximo = cursor.fetchone()
            saida["resultados"] = {
                "quantidade": quantidade,
                "minimo": minimo,
                "maximo": maximo,
            }

            cursor.execute(
                "SELECT estado, COUNT(*) FROM configuracoes_pesquisa_selecao "
                "GROUP BY estado ORDER BY estado"
            )
            saida["configuracoes"] = dict(cursor.fetchall())

            cursor.execute(
                "SELECT "
                "(SELECT COUNT(*) FROM execucoes_pesquisa_selecao),"
                "(SELECT COUNT(*) FROM alvos_pesquisa_selecao),"
                "(SELECT COUNT(*) FROM avaliacoes_dezenas_pesquisa)"
            )
            saida["estrutura_legada"] = dict(
                zip(("execucoes", "alvos", "avaliacoes"), cursor.fetchone())
            )

            cursor.execute(
                "SELECT COUNT(*), COUNT(DISTINCT h.numero_do_concurso), "
                "MIN(h.numero_do_concurso), MAX(h.numero_do_concurso) "
                "FROM historico_frequencia_dezenas h "
                "JOIN geracoes_frequencia_dezenas g "
                "ON g.id_geracao=h.id_geracao AND g.estado='ATIVA' "
                "WHERE h.tipo_evento='SIMPLES'"
            )
            saida["historico_frequencia_ativo"] = dict(
                zip(
                    ("linhas", "concursos", "minimo", "maximo"),
                    cursor.fetchone(),
                )
            )

            cursor.execute(
                "SELECT COUNT(*) FROM ("
                "SELECT h.numero_do_concurso "
                "FROM historico_frequencia_dezenas h "
                "JOIN geracoes_frequencia_dezenas g "
                "ON g.id_geracao=h.id_geracao AND g.estado='ATIVA' "
                "WHERE h.tipo_evento='SIMPLES' "
                "GROUP BY h.numero_do_concurso HAVING COUNT(*) <> 60"
                ") incompletos"
            )
            saida["concursos_com_fotografia_incompleta"] = cursor.fetchone()[0]

            cursor.execute(
                "SELECT tablename,indexname,indexdef FROM pg_indexes "
                "WHERE schemaname='public' AND tablename = ANY(%s) "
                "ORDER BY tablename,indexname",
                (list(TABELAS_AUDITADAS),),
            )
            saida["indices"] = [
                dict(zip(("tabela", "nome", "definicao"), linha))
                for linha in cursor.fetchall()
            ]

            cursor.execute(
                "SELECT relname,pg_total_relation_size(oid) FROM pg_class "
                "WHERE relname = ANY(%s) ORDER BY relname",
                (list(TABELAS_AUDITADAS),),
            )
            saida["tamanhos_bytes"] = dict(cursor.fetchall())

            cursor.execute(
                "EXPLAIN (ANALYZE,BUFFERS,FORMAT JSON) "
                "SELECT data_resultado,numero_ap,res_01,res_02,res_03,res_04,"
                "res_05,res_06 FROM resultados WHERE numero_ap <= %s "
                "ORDER BY numero_ap",
                (maximo,),
            )
            saida["leitura_resultados"] = _resumo_plano(cursor.fetchone()[0])

            cursor.execute(
                "EXPLAIN (ANALYZE,BUFFERS,FORMAT JSON) "
                "SELECT d.dezena,r.numero_ap FROM resultados r "
                "CROSS JOIN LATERAL UNNEST(ARRAY[r.res_01,r.res_02,r.res_03,"
                "r.res_04,r.res_05,r.res_06]) d(dezena) "
                "WHERE r.numero_ap <= %s ORDER BY d.dezena,r.numero_ap",
                (maximo,),
            )
            saida["reconstrucao_ocorrencias"] = _resumo_plano(
                cursor.fetchone()[0]
            )

            cursor.execute(
                "EXPLAIN (ANALYZE,BUFFERS,FORMAT JSON) "
                "SELECT h.numero_do_concurso,h.dezena,h.quantidade_intervalos,"
                "h.media_intervalos,h.desvio_padrao_intervalos,h.previsao_central "
                "FROM historico_frequencia_dezenas h "
                "JOIN geracoes_frequencia_dezenas g "
                "ON g.id_geracao=h.id_geracao AND g.estado='ATIVA' "
                "WHERE h.tipo_evento='SIMPLES' "
                "AND h.numero_do_concurso BETWEEN 500 AND %s "
                "ORDER BY h.numero_do_concurso,h.dezena",
                (maximo - 1,),
            )
            saida["leitura_fotografias_em_lote"] = _resumo_plano(
                cursor.fetchone()[0]
            )

            cursor.execute(
                "EXPLAIN (ANALYZE,BUFFERS,FORMAT JSON) "
                "SELECT numero_ap,res_01,res_02,res_03,res_04,res_05,res_06 "
                "FROM resultados WHERE numero_ap BETWEEN 500 AND %s "
                "ORDER BY numero_ap",
                (maximo,),
            )
            saida["leitura_resultados_alvo"] = _resumo_plano(
                cursor.fetchone()[0]
            )

    print(json.dumps(saida, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
