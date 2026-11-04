"""Valida a API de Seleção de dezenas em database efêmero."""

import os
import time

from dotenv import load_dotenv

from msen.api import criar_app
from msen.config import carregar_configuracao_banco
from tests.suporte_banco_integracao import conectar, criar, remover


COLUNAS = (
    "data_resultado,numero_ap,res_01,res_02,res_03,res_04,res_05,res_06,"
    "soma_res,media_aritmetica_res,mediana_res,desvio_padrao_media,"
    "media_coordenada_x,media_coordenada_y,versao_calculo"
)


def configuracao_json():
    return {
        "nome": "API integrada sete dezenas",
        "fator_k": "1.000000",
        "fator_j": "0.000000",
        "modo_quantidade": "FIXA",
        "quantidade_dezenas": 7,
        "horizonte_concursos": 1,
        "versao_calculo": 1,
    }


def aguardar(cliente, identificador, limite=10):
    fim = time.monotonic() + limite
    while time.monotonic() < fim:
        resposta = cliente.get(f"/api/selecao-dezenas/execucoes/{identificador}")
        assert resposta.status_code == 200
        if resposta.json["estado"] in {"CONCLUIDA", "CANCELADA", "FALHOU"}:
            return resposta.json
        time.sleep(0.02)
    raise AssertionError("O backtest da API não terminou no prazo.")


def executar() -> None:
    load_dotenv()
    banco = carregar_configuracao_banco()
    temporario = f"games_test_7_1_{os.getpid()}"
    with conectar(banco, banco.nome) as origem:
        with origem.cursor() as cursor:
            cursor.execute(
                f"SELECT {COLUNAS} FROM resultados "
                "WHERE numero_ap <= 505 ORDER BY numero_ap"
            )
            resultados = cursor.fetchall()
    assert len(resultados) == 505

    criar(banco, temporario)
    nome_anterior = os.environ["GAME_DB_NAME"]
    try:
        with conectar(banco, temporario) as conexao:
            with conexao.transaction():
                with conexao.cursor() as cursor:
                    cursor.executemany(
                        f"INSERT INTO resultados ({COLUNAS}) "
                        "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                        resultados,
                    )
        os.environ["GAME_DB_NAME"] = temporario
        app = criar_app({"TESTING": True})
        cliente = app.test_client()

        criada = cliente.post("/api/selecao-dezenas/configuracoes", json={
            "configuracao": configuracao_json()
        })
        assert criada.status_code == 201
        lista = cliente.get("/api/selecao-dezenas/configuracoes")
        assert lista.status_code == 200
        assert len(lista.json["configuracoes"]) == 1

        previa = cliente.post("/api/selecao-dezenas/previa", json={
            "configuracao": configuracao_json(),
            "concurso_inicial": 500,
            "concurso_final": 505,
        })
        assert previa.status_code == 200
        assert previa.json["backtest"]["quantidade_alvos"] == 6
        assert previa.json["previsao_futura"]["concurso_inicial"] == 506

        inicio = cliente.post("/api/selecao-dezenas/backtests", json={
            "configuracao": configuracao_json(),
            "concurso_inicial": 500,
            "concurso_final": 505,
        })
        assert inicio.status_code == 202
        tarefa = aguardar(cliente, inicio.json["id"])
        assert tarefa["estado"] == "CONCLUIDA", tarefa
        id_backtest = tarefa["resultado"]["id_execucao_selecao"]
        resumo = cliente.get(
            f"/api/selecao-dezenas/backtests/{id_backtest}/resumo"
        )
        detalhes = cliente.get(
            f"/api/selecao-dezenas/backtests/{id_backtest}/detalhes"
        )
        assert resumo.status_code == detalhes.status_code == 200
        assert resumo.json["avaliados"] == 6
        assert len(detalhes.json["detalhes"]) == 6

        previsao = cliente.post("/api/selecao-dezenas/previsoes", json={
            "configuracao": configuracao_json()
        })
        assert previsao.status_code == 200
        id_previsao = previsao.json["nova_previsao"]["id_execucao_selecao"]
        alvo = cliente.get(
            f"/api/selecao-dezenas/previsoes/{id_previsao}/detalhes"
        ).json["detalhes"][0]
        assert alvo["numero_concurso_alvo"] == 506
        id_alvo = alvo["id_alvo_selecao"]
        jogos = cliente.get(
            f"/api/selecao-dezenas/alvos/{id_alvo}/jogos/previa"
        )
        assert jogos.status_code == 200
        assert jogos.json["quantidade_combinacoes"] == 7
        recusada = cliente.post(
            f"/api/selecao-dezenas/alvos/{id_alvo}/jogos",
            json={"autorizar_persistencia": False},
        )
        assert recusada.status_code == 400
        gravada = cliente.post(
            f"/api/selecao-dezenas/alvos/{id_alvo}/jogos",
            json={
                "autorizar_persistencia": True,
                "confirmar_volume_elevado": False,
            },
        )
        assert gravada.status_code == 201
        assert gravada.json["quantidade_combinacoes"] == 7
        print("API, backtest, previsão e jogos autorizados validados.")
    finally:
        os.environ["GAME_DB_NAME"] = nome_anterior
        remover(banco, temporario)


if __name__ == "__main__":
    executar()
