"""Valida a API do Backtest completa sem persistir resultados derivados."""

from __future__ import annotations

import json
import time

from dotenv import load_dotenv

from msen.api import criar_app
from msen.config import carregar_configuracao_banco
from msen.database import abrir_conexao


TERMINAIS = {"CONCLUIDA", "CANCELADA", "FALHOU"}


def _cardinalidades() -> tuple[int, int, int, int, int]:
    with abrir_conexao(carregar_configuracao_banco()) as conexao:
        with conexao.transaction():
            with conexao.cursor() as cursor:
                cursor.execute(
                    "SELECT "
                    "(SELECT COUNT(*) FROM configuracoes_pesquisa_selecao),"
                    "(SELECT COUNT(*) FROM resultados),"
                    "(SELECT COUNT(*) FROM execucoes_pesquisa_selecao),"
                    "(SELECT COUNT(*) FROM alvos_pesquisa_selecao),"
                    "(SELECT COUNT(*) FROM avaliacoes_dezenas_pesquisa)"
                )
                return cursor.fetchone()


def _configuracao_disponivel() -> int:
    with abrir_conexao(carregar_configuracao_banco()) as conexao:
        with conexao.transaction():
            with conexao.cursor() as cursor:
                cursor.execute(
                    "SELECT id_configuracao_selecao "
                    "FROM configuracoes_pesquisa_selecao "
                    "WHERE estado='DISPONIVEL' "
                    "ORDER BY id_configuracao_selecao LIMIT 1"
                )
                linha = cursor.fetchone()
    if linha is None:
        raise RuntimeError("É necessária uma configuração salva e disponível.")
    return linha[0]


def _aguardar(cliente, identificador: str, limite: float = 20) -> dict:
    fim = time.monotonic() + limite
    while time.monotonic() < fim:
        resposta = cliente.get(
            f"/api/selecao-dezenas/backtests/{identificador}"
        )
        assert resposta.status_code == 200, resposta.get_data(as_text=True)
        if resposta.json["estado"] in TERMINAIS:
            return resposta.json
        time.sleep(0.05)
    raise AssertionError("A execução do Backtest não terminou no prazo esperado.")


def main() -> None:
    load_dotenv()
    cliente = criar_app({"TESTING": True}).test_client()
    corpo = {
        "id_configuracao_selecao": _configuracao_disponivel(),
        "concurso_inicial": 500,
    }
    antes = _cardinalidades()

    for concurso_invalido in (499, 3070):
        invalida = cliente.post(
            "/api/selecao-dezenas/backtests/previa",
            json={
                "id_configuracao_selecao": corpo["id_configuracao_selecao"],
                "concurso_inicial": concurso_invalido,
            },
        )
        assert invalida.status_code == 400, invalida.get_data(as_text=True)

    previa = cliente.post(
        "/api/selecao-dezenas/backtests/previa", json=corpo
    )
    assert previa.status_code == 200, previa.get_data(as_text=True)
    assert previa.json["periodo"]["quantidade_concursos"] == 2570
    assert previa.json["persistira_resultados"] is False

    inicio = cliente.post(
        "/api/selecao-dezenas/backtests", json=corpo
    )
    assert inicio.status_code == 202, inicio.get_data(as_text=True)
    final = _aguardar(cliente, inicio.json["id"])
    assert final["estado"] == "CONCLUIDA", final
    assert final["resultado"]["persistido"] is False
    assert len(final["resultado"]["pontos"]) == 2570
    assert final["resultado"]["resumo"]["testes_efetuados"] == 2570
    assert sum(
        item["quantidade"] for item in final["resultado"]["resumo"]["classes"]
    ) == 2570
    depois_conclusao = _cardinalidades()
    assert antes == depois_conclusao

    segunda = cliente.post(
        "/api/selecao-dezenas/backtests", json=corpo
    )
    assert segunda.status_code == 202
    cancelamento = cliente.post(
        f"/api/selecao-dezenas/backtests/{segunda.json['id']}"
        "/cancelamento"
    )
    assert cancelamento.status_code == 202, cancelamento.get_data(as_text=True)
    cancelada = _aguardar(cliente, segunda.json["id"])
    assert cancelada["estado"] == "CANCELADA", cancelada
    assert cancelada["resultado"] is None
    depois_cancelamento = _cardinalidades()
    assert antes == depois_cancelamento

    descarte = cliente.delete(
        f"/api/selecao-dezenas/backtests/{segunda.json['id']}"
    )
    assert descarte.status_code == 204
    ausente = cliente.get(
        f"/api/selecao-dezenas/backtests/{segunda.json['id']}"
    )
    assert ausente.status_code == 404

    print(json.dumps({
        "previa_sem_gravacao": True,
        "execucao": inicio.json["id"],
        "pontos": len(final["resultado"]["pontos"]),
        "estado_final": final["estado"],
        "duracao_segundos": final["duracao_segundos"],
        "cancelamento": cancelada["estado"],
        "descarte": "CONFIRMADO",
        "cardinalidades_inalteradas": antes == depois_cancelamento,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
