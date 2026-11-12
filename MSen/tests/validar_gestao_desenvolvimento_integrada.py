"""Valida Gestão do desenvolvimento no PostgreSQL real com rollback obrigatório."""

from __future__ import annotations

import json

from dotenv import load_dotenv

from msen.api import criar_app
from msen.config import carregar_configuracao_banco
from msen.database import abrir_conexao
from msen.database.gestao_desenvolvimento_repository import RepositorioGestaoDesenvolvimento


CHAVE = "d" * 64


def corpo(status="NAO_INICIADO"):
    return {
        "tipo": "MODIFICACAO",
        "titulo": "Validação transitória da etapa 27.6",
        "data_registro": "2026-11-11",
        "descricao": "Registro criado dentro de transação obrigatoriamente revertida.",
        "status_trabalho": status,
        "status_publicacao": "NAO_APLICAVEL",
        "pagina_origem": "/validacao-integrada",
        "observacao_publicacao": None,
    }


def quantidade(conexao):
    with conexao.cursor() as cursor:
        cursor.execute("SELECT count(id_manutencao) FROM manutencao_sistema")
        return cursor.fetchone()[0]


def main():
    load_dotenv()
    configuracao = carregar_configuracao_banco()
    if configuracao.nome != "games":
        raise RuntimeError("A validação exige GAME_DB_NAME=games.")
    with abrir_conexao(configuracao) as conexao:
        antes = quantidade(conexao)
        resumo = {}
        with conexao.transaction(force_rollback=True):
            repositorio = RepositorioGestaoDesenvolvimento(conexao)
            app = criar_app({
                "TESTING": True,
                "LISTAR_GESTAO_DESENVOLVIMENTO": repositorio.listar,
                "CONSULTAR_GESTAO_DESENVOLVIMENTO": repositorio.consultar,
                "HISTORICO_GESTAO_DESENVOLVIMENTO": repositorio.listar_historico,
                "CRIAR_GESTAO_DESENVOLVIMENTO": repositorio.criar,
                "ATUALIZAR_GESTAO_DESENVOLVIMENTO": repositorio.atualizar,
                "ARQUIVAR_GESTAO_DESENVOLVIMENTO": repositorio.definir_arquivamento,
            })
            cliente = app.test_client()
            primeira = cliente.post("/api/gestao-desenvolvimento", json={
                "dados": corpo(), "chave_idempotencia": CHAVE,
            })
            repetida = cliente.post("/api/gestao-desenvolvimento", json={
                "dados": corpo(), "chave_idempotencia": CHAVE,
            })
            assert primeira.status_code == 201 and repetida.status_code == 200, (
                primeira.status_code, primeira.get_json(),
                repetida.status_code, repetida.get_json(),
            )
            assert primeira.json["registro"]["id_manutencao"] == repetida.json["registro"]["id_manutencao"]
            identificador = primeira.json["registro"]["id_manutencao"]

            conflito = cliente.put(f"/api/gestao-desenvolvimento/{identificador}", json={
                "dados": corpo(), "versao_registro": 99,
            })
            assert conflito.status_code == 409
            concluida = cliente.put(f"/api/gestao-desenvolvimento/{identificador}", json={
                "dados": corpo("CONCLUIDO"), "versao_registro": 1,
            })
            assert concluida.status_code == 200
            reaberta = cliente.put(f"/api/gestao-desenvolvimento/{identificador}", json={
                "dados": corpo("EM_ANDAMENTO"), "versao_registro": 2,
            })
            assert reaberta.status_code == 200
            arquivada = cliente.post(
                f"/api/gestao-desenvolvimento/{identificador}/arquivamento",
                json={"versao_registro": 3},
            )
            assert arquivada.status_code == 200
            desarquivada = cliente.delete(
                f"/api/gestao-desenvolvimento/{identificador}/arquivamento",
                json={"versao_registro": 4},
            )
            assert desarquivada.status_code == 200
            arquivada_novamente = cliente.post(
                f"/api/gestao-desenvolvimento/{identificador}/arquivamento",
                json={"versao_registro": 5},
            )
            assert arquivada_novamente.status_code == 200
            lista = cliente.get("/api/gestao-desenvolvimento?arquivados=true")
            historico = cliente.get(f"/api/gestao-desenvolvimento/{identificador}/historico")
            eventos = [item["tipo_evento"] for item in historico.json["eventos"]]
            assert lista.status_code == 200 and lista.json["total"] == 1
            assert eventos == [
                "CRIADO", "STATUS_ALTERADO", "REABERTO", "ARQUIVADO",
                "DESARQUIVADO", "ARQUIVADO",
            ]
            assert quantidade(conexao) == antes + 1
            resumo = {
                "criacao": primeira.status_code,
                "repeticao_idempotente": repetida.status_code,
                "conflito": conflito.status_code,
                "eventos": eventos,
                "rollback_planejado": True,
            }
        assert quantidade(conexao) == antes
        resumo["registros_antes"] = antes
        resumo["registros_depois"] = quantidade(conexao)
        print(json.dumps(resumo, ensure_ascii=False))


if __name__ == "__main__":
    main()
