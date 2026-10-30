"""Valida consultas da API de frequências em PostgreSQL efêmero."""

from dataclasses import replace
from datetime import date, timedelta
import os
from pathlib import Path

from dotenv import load_dotenv

from msen.api.frequencias import (
    consultar_estado_frequencia,
    consultar_fotografia_atual_frequencia,
    consultar_serie_frequencia,
)
from msen.calculos import calcular_resultado
from msen.config import carregar_configuracao_banco
from msen.database import RepositorioResultados, executar_migracoes
from msen.modelos import ResultadoEntrada
from msen.services import atualizar_historico_frequencia, configuracao_frequencia_inicial
from tests.suporte_banco_integracao import conectar, criar_vazio, remover


RAIZ = Path(__file__).resolve().parents[2]
MIGRACOES = RAIZ / "database" / "migrations"


def executar() -> None:
    load_dotenv(Path(__file__).resolve().parents[1] / ".env")
    config_banco = carregar_configuracao_banco()
    nome = f"games_test_7_1_{os.getpid()}"
    criar_vazio(config_banco, nome)
    try:
        executar_migracoes(replace(config_banco, nome=nome), MIGRACOES)
        with conectar(config_banco, nome) as conexao:
            repositorio = RepositorioResultados(conexao)
            for numero in range(1, 6):
                entrada = ResultadoEntrada.criar(
                    data_resultado=date(2020, 1, 1) + timedelta(days=numero),
                    numero_ap=numero, resultados=(10, 21, 32, 43, 54, 60),
                )
                repositorio.inserir(calcular_resultado(entrada))
            config = replace(
                configuracao_frequencia_inicial(), nome="API teste", tamanho_inicial=3
            )
            atualizar_historico_frequencia(
                conexao, config, confirmacao_gravacao=True
            )
            estado = consultar_estado_frequencia(conexao)
            atuais = {
                tipo: consultar_fotografia_atual_frequencia(
                    conexao, tipo_evento=tipo
                )
                for tipo in ("SIMPLES", "2VS", "3VS")
            }
            serie = consultar_serie_frequencia(
                conexao, dezena=10, tipo_evento="SIMPLES",
                concurso_inicial=3, concurso_final=5,
            )
            serie_2vs = consultar_serie_frequencia(
                conexao, dezena=10, tipo_evento="2VS",
                concurso_inicial=3, concurso_final=5,
            )
            serie_3vs = consultar_serie_frequencia(
                conexao, dezena=10, tipo_evento="3VS",
                concurso_inicial=3, concurso_final=5,
            )
            if estado["geracao_ativa"]["concurso_final"] != 5:
                raise AssertionError("Estado não encontrou a geração ativa.")
            if any(len(atual["dezenas"]) != 60 for atual in atuais.values()):
                raise AssertionError("Fotografia atual não devolveu 60 dezenas por tipo.")
            if serie["total"] != 3 or [p["numero_do_concurso"] for p in serie["pontos"]] != [3, 4, 5]:
                raise AssertionError("Série histórica divergiu do período solicitado.")
            if any("dezenas" in ponto for ponto in serie["pontos"]):
                raise AssertionError("A série duplicou as dezenas dos resultados.")
            if serie["ocorrencias_reais"] != [3, 4, 5]:
                raise AssertionError("Ocorrências simples reais incorretas.")
            if serie_2vs["ocorrencias_reais"] != [3, 4, 5]:
                raise AssertionError("Ocorrências 2VS reais incorretas no corte solicitado.")
            if serie_3vs["ocorrencias_reais"] != [3, 4, 5]:
                raise AssertionError("Ocorrências 3VS reais incorretas no corte solicitado.")
            if serie["assertividade"]["total"] != 3:
                raise AssertionError("Assertividade não cobriu todos os cortes da série.")
            if serie["assertividade"]["censurados"] < 1:
                raise AssertionError("Último corte sem futuro deveria estar censurado.")
        print("API validada em PostgreSQL: estado, 60 dezenas por tipo e série filtrada.")
    finally:
        remover(config_banco, nome)


if __name__ == "__main__":
    executar()
