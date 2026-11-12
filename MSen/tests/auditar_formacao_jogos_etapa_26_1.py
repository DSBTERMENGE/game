"""Leitura das cardinalidades usadas na auditoria da etapa 26.1."""

from dotenv import load_dotenv
from itertools import combinations
from math import comb
from time import perf_counter
import tracemalloc

from msen.config import carregar_configuracao_banco
from msen.database import abrir_conexao


load_dotenv()
with abrir_conexao(carregar_configuracao_banco()) as conexao, conexao.cursor() as cursor:
    consultas = {
        "alvos": "SELECT COUNT(*) FROM alvos_pesquisa_selecao",
        "lotes": "SELECT COUNT(*) FROM lotes_jogos_selecao",
        "jogos": "SELECT COUNT(*) FROM jogos_selecao_dezenas",
        "grupos": "SELECT COUNT(*) FROM padroes_grupo",
        "padroes_total_com_perfil": (
            "SELECT COUNT(*), COUNT(*) FILTER (WHERE total_sorteios IS NOT NULL) "
            "FROM padroes_subgrupo"
        ),
        "criterios_ativos_aprovados": (
            "SELECT COUNT(*), COUNT(*) FILTER (WHERE estado='APROVADO') "
            "FROM criterios_validacao WHERE ativo"
        ),
        "algoritmo": (
            "SELECT atualizado, motivo, quantidade_resultados "
            "FROM estado_algoritmo_selecao WHERE id_estado=1"
        ),
    }
    for nome, sql in consultas.items():
        cursor.execute(sql)
        print(nome, cursor.fetchone())
    cursor.execute(
        "SELECT a.id_alvo_selecao, a.numero_concurso_alvo, "
        "COUNT(v.dezena) FILTER (WHERE v.retornada) "
        "FROM alvos_pesquisa_selecao a "
        "LEFT JOIN avaliacoes_dezenas_pesquisa v "
        "ON v.id_alvo_selecao=a.id_alvo_selecao "
        "GROUP BY a.id_alvo_selecao, a.numero_concurso_alvo "
        "ORDER BY a.id_alvo_selecao"
    )
    print("selecoes", cursor.fetchall())
    cursor.execute(
        "SELECT g.grupo_cod, p.padrao_cod, p.percentual_ocorrencia "
        "FROM padroes_subgrupo p JOIN padroes_grupo g ON g.id_grupo=p.id_grupo "
        "ORDER BY g.grupo_cod, p.padrao_cod"
    )
    print("padroes", cursor.fetchall())

for quantidade in (6, 16, 19, 26, 38, 60):
    print("combinacoes", quantidade, comb(quantidade, 6))

tracemalloc.start()
inicio = perf_counter()
amostra_atual = tuple(combinations(range(1, 17), 6))
duracao = perf_counter() - inicio
_, pico = tracemalloc.get_traced_memory()
tracemalloc.stop()
print(
    "materializacao_16",
    {"quantidade": len(amostra_atual), "duracao_segundos": duracao, "pico_bytes": pico},
)
