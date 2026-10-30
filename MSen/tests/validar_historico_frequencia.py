"""Valida a estrutura histórica em PostgreSQL efêmero."""

from dataclasses import replace
import os
from pathlib import Path

from dotenv import load_dotenv
import psycopg
from psycopg.types.json import Jsonb

from msen.config import carregar_configuracao_banco
from msen.database import executar_migracoes
from msen.services import configuracao_frequencia_inicial
from tests.suporte_banco_integracao import conectar, criar_vazio, remover


RAIZ = Path(__file__).resolve().parents[2]
MIGRACOES = RAIZ / "database" / "migrations"


def executar() -> None:
    load_dotenv(Path(__file__).resolve().parents[1] / ".env")
    configuracao_banco = carregar_configuracao_banco()
    nome = f"games_test_7_1_{os.getpid()}"
    criar_vazio(configuracao_banco, nome)
    try:
        config_teste = replace(configuracao_banco, nome=nome)
        primeira = executar_migracoes(config_teste, MIGRACOES)
        segunda = executar_migracoes(config_teste, MIGRACOES)
        if "019" not in primeira.aplicadas or segunda.aplicadas:
            raise AssertionError("A migração 019 não foi idempotente.")

        config = configuracao_frequencia_inicial()
        with conectar(configuracao_banco, nome) as conexao:
            with conexao.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO geracoes_frequencia_dezenas "
                    "(assinatura_configuracao, configuracao_json, assinatura_resultados, "
                    "quantidade_resultados, versao_calculo, concurso_inicial) "
                    "VALUES (%s, %s, %s, %s, %s, %s) RETURNING id_geracao",
                    (config.assinatura_sha256, Jsonb(config.conteudo_assinavel()),
                     "1" * 64, 500, config.versao_calculo, 500),
                )
                id_geracao = cursor.fetchone()[0]
                cursor.execute(
                    "INSERT INTO historico_frequencia_dezenas "
                    "(id_geracao, numero_do_concurso, dezena, tipo_evento, "
                    "quantidade_ocorrencias, quantidade_intervalos) "
                    "VALUES (%s, 500, 1, '3VS', 0, 0)",
                    (id_geracao,),
                )
                cursor.execute(
                    "INSERT INTO historico_frequencia_dezenas "
                    "(id_geracao, numero_do_concurso, dezena, tipo_evento, "
                    "quantidade_ocorrencias, quantidade_intervalos, "
                    "intervalo_minimo, intervalo_maximo, media_intervalos, "
                    "mediana_intervalos, desvio_padrao_intervalos, previsao_central, "
                    "limite_inferior_exato, limite_superior_exato, "
                    "concurso_limite_inferior, concurso_limite_superior) "
                    "VALUES (%s, 500, 2, 'SIMPLES', 4, 3, 10, 15, 13.333333, "
                    "15.000000, 2.357023, 513.333333, 510.976310, 515.690356, 510, 516)",
                    (id_geracao,),
                )

                for comando in (
                    "INSERT INTO historico_frequencia_dezenas "
                    "(id_geracao, numero_do_concurso, dezena, tipo_evento, "
                    "quantidade_ocorrencias, quantidade_intervalos, intervalo_minimo) "
                    f"VALUES ({id_geracao}, 500, 3, '2VS', 2, 1, 5)",
                    "INSERT INTO historico_frequencia_dezenas "
                    "(id_geracao, numero_do_concurso, dezena, tipo_evento, "
                    "quantidade_ocorrencias, quantidade_intervalos) "
                    f"VALUES ({id_geracao}, 500, 1, '3VS', 0, 0)",
                ):
                    try:
                        with conexao.transaction():
                            cursor.execute(comando)
                    except (psycopg.errors.CheckViolation,
                            psycopg.errors.UniqueViolation):
                        pass
                    else:
                        raise AssertionError("O banco aceitou fotografia inválida.")

                cursor.execute(
                    "UPDATE geracoes_frequencia_dezenas SET estado='ATIVA', "
                    "concurso_final=500, quantidade_fotografias=1, "
                    "concluida_em=CURRENT_TIMESTAMP WHERE id_geracao=%s",
                    (id_geracao,),
                )
                try:
                    with conexao.transaction():
                        cursor.execute(
                            "INSERT INTO geracoes_frequencia_dezenas "
                            "(assinatura_configuracao, configuracao_json, "
                            "assinatura_resultados, quantidade_resultados, versao_calculo, "
                            "estado, concurso_inicial, concurso_final, concluida_em) "
                            "VALUES (%s, %s, %s, 500, 1, 'ATIVA', 500, 500, "
                            "CURRENT_TIMESTAMP)",
                            (config.assinatura_sha256,
                             Jsonb(config.conteudo_assinavel()), "1" * 64),
                        )
                except psycopg.errors.UniqueViolation:
                    pass
                else:
                    raise AssertionError("O banco aceitou duas gerações ativas.")

                cursor.execute("SET LOCAL enable_seqscan = off")
                cursor.execute(
                    "EXPLAIN SELECT numero_do_concurso, media_intervalos "
                    "FROM historico_frequencia_dezenas WHERE id_geracao=%s "
                    "AND dezena=2 AND tipo_evento='SIMPLES' "
                    "ORDER BY numero_do_concurso",
                    (id_geracao,),
                )
                plano = " ".join(linha[0] for linha in cursor.fetchall())
                if "ix_historico_frequencia_grafico" not in plano:
                    raise AssertionError("Consulta do gráfico não utilizou o índice previsto.")

                cursor.execute(
                    "DELETE FROM geracoes_frequencia_dezenas WHERE id_geracao=%s",
                    (id_geracao,),
                )
                cursor.execute(
                    "SELECT count(*) FROM historico_frequencia_dezenas "
                    "WHERE id_geracao=%s", (id_geracao,)
                )
                if cursor.fetchone()[0] != 0:
                    raise AssertionError("A cascata da geração não removeu as fotografias.")
            conexao.commit()

        print("Histórico 019 validado: estados, unicidade, precisão, índice e cascata.")
    finally:
        remover(configuracao_banco, nome)


if __name__ == "__main__":
    executar()
