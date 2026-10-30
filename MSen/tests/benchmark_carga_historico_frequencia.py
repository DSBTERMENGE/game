"""Mede a carga histórica com os resultados locais em database efêmero."""

from dataclasses import replace
from datetime import timedelta
import os
from pathlib import Path
from time import perf_counter

from dotenv import load_dotenv

from msen.config import carregar_configuracao_banco
from msen.database import executar_migracoes
from msen.services import atualizar_historico_frequencia, configuracao_frequencia_inicial
from msen.api.frequencias import (
    consultar_fotografia_atual_frequencia,
    consultar_serie_frequencia,
)
from tests.suporte_banco_integracao import conectar, criar_vazio, remover


RAIZ = Path(__file__).resolve().parents[2]
MIGRACOES = RAIZ / "database" / "migrations"
COLUNAS = (
    "data_resultado, numero_ap, res_01, res_02, res_03, res_04, res_05, res_06, "
    "soma_res, media_aritmetica_res, mediana_res, desvio_padrao_media, "
    "media_coordenada_x, media_coordenada_y, versao_calculo"
)


def executar() -> None:
    load_dotenv(Path(__file__).resolve().parents[1] / ".env")
    config_banco = carregar_configuracao_banco()
    with conectar(config_banco, config_banco.nome) as origem:
        with origem.cursor() as cursor:
            cursor.execute(f"SELECT {COLUNAS} FROM resultados ORDER BY numero_ap")
            resultados = cursor.fetchall()

    nome = f"games_test_7_1_{os.getpid()}"
    criar_vazio(config_banco, nome)
    try:
        config_teste = replace(config_banco, nome=nome)
        executar_migracoes(config_teste, MIGRACOES)
        with conectar(config_banco, nome) as conexao:
            with conexao.cursor() as cursor:
                cursor.executemany(
                    f"INSERT INTO resultados ({COLUNAS}) VALUES "
                    "(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                    resultados,
                )
            conexao.commit()
            inicio = perf_counter()
            relatorio = atualizar_historico_frequencia(
                conexao, configuracao_frequencia_inicial(),
                confirmacao_gravacao=True,
            )
            duracao_total = perf_counter() - inicio
            with conexao.cursor() as cursor:
                cursor.execute("SELECT count(*) FROM historico_frequencia_dezenas")
                linhas = cursor.fetchone()[0]
                cursor.execute(
                    "SELECT pg_total_relation_size('historico_frequencia_dezenas'), "
                    "pg_indexes_size('historico_frequencia_dezenas')"
                )
                tamanho_total, tamanho_indices = cursor.fetchone()
                ultimo = resultados[-1]
                novo = list(ultimo)
                novo[0] = ultimo[0] + timedelta(days=3)
                novo[1] = ultimo[1] + 1
                cursor.execute(
                    f"INSERT INTO resultados ({COLUNAS}) VALUES "
                    "(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                    novo,
                )
            conexao.commit()
            inicio_incremental = perf_counter()
            relatorio_incremental = atualizar_historico_frequencia(
                conexao, configuracao_frequencia_inicial(),
                confirmacao_gravacao=True,
            )
            duracao_incremental = perf_counter() - inicio_incremental
            inicio_fotografia = perf_counter()
            for tipo in ("SIMPLES", "2VS", "3VS"):
                fotografia = consultar_fotografia_atual_frequencia(
                    conexao, tipo_evento=tipo
                )
                if len(fotografia["dezenas"]) != 60:
                    raise AssertionError("Fotografia incompleta no benchmark.")
            duracao_fotografias = perf_counter() - inicio_fotografia
            inicio_serie = perf_counter()
            serie = consultar_serie_frequencia(
                conexao, dezena=10, tipo_evento="SIMPLES",
                concurso_inicial=500, concurso_final=novo[1],
            )
            duracao_serie = perf_counter() - inicio_serie
            print(
                "Benchmark: resultados=%d, cortes=%d, linhas=%d, motor+gravação=%.3fs, "
                "total=%.3fs, tabela+índices=%d bytes, índices=%d bytes, "
                "incremental_1=%.3fs, linhas_incrementais=%d, "
                "fotografias_3=%.3fs, serie_%d_pontos=%.3fs"
                % (len(resultados), relatorio.fotografias_adicionadas, linhas,
                   relatorio.duracao_segundos, duracao_total, tamanho_total,
                   tamanho_indices, duracao_incremental,
                   relatorio_incremental.linhas_adicionadas,
                   duracao_fotografias, serie["total"], duracao_serie)
            )
    finally:
        remover(config_banco, nome)


if __name__ == "__main__":
    executar()
