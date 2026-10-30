"""Valida a migração 017 em PostgreSQL efêmero, sem tocar no database games."""

from dataclasses import replace
from pathlib import Path
import os

from dotenv import load_dotenv
import psycopg

from msen.calculos import calcular_frequencias, calcular_resultado
from msen.config import carregar_configuracao_banco
from msen.database import executar_migracoes
from msen.database.migrations import _remover_transacao_explicita
from msen.database.repositories import RepositorioResultados
from msen.modelos import ResultadoEntrada
from tests.suporte_banco_integracao import conectar, criar_vazio, remover


RAIZ = Path(__file__).resolve().parents[2]
MIGRACOES = RAIZ / "database" / "migrations"


def executar() -> None:
    load_dotenv(Path(__file__).resolve().parents[1] / ".env")
    configuracao = carregar_configuracao_banco()
    nome = f"games_test_7_1_{os.getpid()}"
    criar_vazio(configuracao, nome)
    try:
        config_teste = replace(configuracao, nome=nome)
        with conectar(configuracao, nome) as conexao:
            with conexao.cursor() as cursor:
                cursor.execute(_remover_transacao_explicita(
                    (MIGRACOES / "001_criar_estrutura_inicial.sql").read_text(
                        encoding="utf-8"
                    ), "001"
                ))

            repositorio = RepositorioResultados(conexao)
            entradas = (
                ResultadoEntrada.criar(data_resultado="01/01/2020", numero_ap=10,
                                       resultados=(2, 3, 4, 5, 6, 7)),
                ResultadoEntrada.criar(data_resultado="02/01/2020", numero_ap=20,
                                       resultados=(1, 2, 8, 9, 10, 11)),
                ResultadoEntrada.criar(data_resultado="03/01/2020", numero_ap=35,
                                       resultados=(2, 12, 13, 14, 15, 16)),
                ResultadoEntrada.criar(data_resultado="04/01/2020", numero_ap=50,
                                       resultados=(2, 17, 18, 19, 20, 21)),
            )
            for entrada in entradas:
                repositorio.inserir(calcular_resultado(entrada))

            frequencias = calcular_frequencias(entradas)
            with conexao.cursor() as cursor:
                for item in frequencias:
                    cursor.execute(
                        "UPDATE frequencia_de_resultado SET prim_oco=%s, ult_oco=%s, "
                        "num_oco=%s, media_oco=%s, mediana_oco=%s, "
                        "desv_padrao_oco=%s WHERE dezena=%s",
                        (item.prim_oco, item.ult_oco, item.num_oco, item.media_oco,
                         item.mediana_oco, item.desv_padrao_oco, item.dezena),
                    )
                cursor.execute(_remover_transacao_explicita(
                    (MIGRACOES / "017_ampliar_frequencia_resultado.sql").read_text(
                        encoding="utf-8"
                    ), "017"
                ))
                cursor.execute(
                    "SELECT qtd_intervalos, intervalo_minimo, intervalo_maximo "
                    "FROM frequencia_de_resultado WHERE dezena=2"
                )
                if cursor.fetchone() != (3, 10, 15):
                    raise AssertionError("Backfill da dezena 2 divergiu do esperado.")
                cursor.execute(
                    "SELECT count(*), sum(num_oco), sum(qtd_intervalos) "
                    "FROM frequencia_de_resultado"
                )
                if cursor.fetchone() != (60, 24, 3):
                    raise AssertionError("Reconciliação global das frequências divergiu.")
            conexao.commit()
        print("Migração 017 validada em PostgreSQL efêmero: 60 dezenas, 24 ocorrências, 3 intervalos.")
    finally:
        remover(configuracao, nome)

    nome_idempotencia = f"games_test_7_1_{os.getpid() + 1}"
    criar_vazio(configuracao, nome_idempotencia)
    try:
        config_idempotencia = replace(configuracao, nome=nome_idempotencia)
        primeira = executar_migracoes(config_idempotencia, MIGRACOES)
        segunda = executar_migracoes(config_idempotencia, MIGRACOES)
        if "017" not in primeira.aplicadas or segunda.aplicadas:
            raise AssertionError("Executor não preservou a idempotência da migração 017.")
        print("Executor idempotente: 017 aplicada uma vez e nenhuma reaplicada.")
    finally:
        remover(configuracao, nome_idempotencia)


if __name__ == "__main__":
    executar()
