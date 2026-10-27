"""Valida as APIs de grupos e padrões em PostgreSQL temporário."""

import json
import os
import sys

from dotenv import load_dotenv

from msen.api import criar_app
from suporte_banco_integracao import validar_nome


def validar_api(nome_database: str) -> dict[str, object]:
    """Percorre criação, filtro, transferência e exclusão pelas rotas reais."""

    nome = validar_nome(nome_database)
    os.environ["GAME_DB_NAME"] = nome
    cliente = criar_app({"TESTING": True}).test_client()

    resposta_grupo = cliente.post(
        "/api/grupos-padroes",
        json={"grupo_nome": "Mesma coluna", "grupo_descr": "Teste integrado"},
    )
    if resposta_grupo.status_code != 201:
        raise AssertionError(resposta_grupo.get_json())
    grupo_cod = resposta_grupo.get_json()["grupo"]["grupo_cod"]

    resposta_padrao = cliente.post(
        "/api/padroes",
        json={
            "grupo_cod": grupo_cod,
            "padrao_nome": "Duas dezenas na coluna",
            "padrao_descr": "Padrão temporário de integração",
        },
    )
    if resposta_padrao.status_code != 201:
        raise AssertionError(resposta_padrao.get_json())
    padrao = resposta_padrao.get_json()["padrao"]

    resposta_filtro = cliente.get(f"/api/padroes?grupo_cod={grupo_cod}")
    if resposta_filtro.status_code != 200 or resposta_filtro.get_json()["total"] != 1:
        raise AssertionError(resposta_filtro.get_json())

    resposta_edicao = cliente.put(
        f"/api/padroes/{padrao['padrao_cod']}",
        json={
            "grupo_cod": "PG_001",
            "padrao_nome": padrao["padrao_nome"],
            "padrao_descr": padrao["padrao_descr"],
        },
    )
    if resposta_edicao.status_code != 200:
        raise AssertionError(resposta_edicao.get_json())
    if resposta_edicao.get_json()["padrao"]["grupo_cod"] != "PG_001":
        raise AssertionError("A transferência de grupo não foi retornada pela API.")

    resposta_exclusao = cliente.delete(f"/api/grupos-padroes/{grupo_cod}")
    if resposta_exclusao.status_code != 200:
        raise AssertionError(resposta_exclusao.get_json())

    return {
        "grupo_criado": grupo_cod,
        "padrao_criado": padrao["padrao_cod"],
        "filtro": True,
        "transferencia": True,
        "grupo_vazio_excluido": True,
    }


def main() -> None:
    """Executa a validação no database temporário informado."""

    load_dotenv()
    if len(sys.argv) != 2:
        raise SystemExit("Uso: validar_api_catalogo_padroes.py NOME_DATABASE")
    print(json.dumps(validar_api(sys.argv[1]), ensure_ascii=False))


if __name__ == "__main__":
    main()
