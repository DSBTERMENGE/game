"""Testes do contrato HTTP da Gestão do desenvolvimento."""

from datetime import date, datetime, timezone
import unittest

from msen.api import criar_app
from msen.database.gestao_desenvolvimento_repository import (
    ErroRepositorioGestaoDesenvolvimento, EventoManutencaoPersistido,
    ManutencaoPersistida,
)


def registro(versao=1):
    agora = datetime(2026, 11, 11, tzinfo=timezone.utc)
    return ManutencaoPersistida(
        7, "MODIFICACAO", "Pesquisa", date(2026, 11, 11), "Busca parcial",
        "NAO_INICIADO", "NAO_APLICAVEL", None, None,
        versao, agora, agora, None, None, None, None,
    )


class ApiGestaoDesenvolvimentoTest(unittest.TestCase):
    def setUp(self):
        self.criados = []
        self.atualizados = []
        self.arquivamentos = []
        self.app = criar_app({
            "TESTING": True,
            "LISTAR_GESTAO_DESENVOLVIMENTO": lambda **consulta: ((registro(),), 1),
            "CONSULTAR_GESTAO_DESENVOLVIMENTO": lambda identificador: registro(),
            "HISTORICO_GESTAO_DESENVOLVIMENTO": lambda identificador: (
                EventoManutencaoPersistido(
                    1, identificador, "CRIADO", 1,
                    {"titulo": "Pesquisa"}, datetime(2026, 11, 11, tzinfo=timezone.utc),
                ),
            ),
            "CRIAR_GESTAO_DESENVOLVIMENTO": self._criar,
            "ATUALIZAR_GESTAO_DESENVOLVIMENTO": self._atualizar,
            "ARQUIVAR_GESTAO_DESENVOLVIMENTO": self._arquivar,
        })
        self.cliente = self.app.test_client()

    def _criar(self, dados, chave):
        self.criados.append((dados, chave))
        return registro(), True

    def _atualizar(self, identificador, versao, dados):
        self.atualizados.append((identificador, versao, dados))
        return registro(2)

    def _arquivar(self, identificador, versao, arquivar):
        self.arquivamentos.append((identificador, versao, arquivar))
        return registro(versao + 1)

    @staticmethod
    def dados():
        return {"tipo": "MODIFICACAO", "titulo": "Pesquisa", "data_registro": "2026-11-11", "descricao": "Busca parcial"}

    def test_lista_com_paginacao_e_filtros(self):
        resposta = self.cliente.get("/api/gestao-desenvolvimento?busca=pesq&pagina=1&por_pagina=20")
        self.assertEqual(200, resposta.status_code)
        self.assertEqual(1, resposta.json["total"])
        self.assertEqual("Pesquisa", resposta.json["registros"][0]["titulo"])

    def test_rejeita_filtros_desconhecidos(self):
        for consulta in ("tipo=OUTRO", "arquivados=talvez"):
            with self.subTest(consulta=consulta):
                resposta = self.cliente.get(f"/api/gestao-desenvolvimento?{consulta}")
                self.assertEqual(400, resposta.status_code)

    def test_cria_somente_com_chave_valida(self):
        resposta = self.cliente.post("/api/gestao-desenvolvimento", json={
            "dados": self.dados(), "chave_idempotencia": "a" * 64,
        })
        self.assertEqual(201, resposta.status_code)
        self.assertTrue(resposta.json["criado"])
        self.assertEqual("Pesquisa", self.criados[0][0].titulo)

    def test_consulta_historico(self):
        resposta = self.cliente.get("/api/gestao-desenvolvimento/7/historico")
        self.assertEqual(200, resposta.status_code)
        self.assertEqual("CRIADO", resposta.json["eventos"][0]["tipo_evento"])

    def test_repeticao_idempotente_retorna_200(self):
        self.app.config["CRIAR_GESTAO_DESENVOLVIMENTO"] = lambda dados, chave: (registro(), False)
        resposta = self.cliente.post("/api/gestao-desenvolvimento", json={
            "dados": self.dados(), "chave_idempotencia": "b" * 64,
        })
        self.assertEqual(200, resposta.status_code)
        self.assertFalse(resposta.json["criado"])

    def test_atualiza_com_versao(self):
        resposta = self.cliente.put("/api/gestao-desenvolvimento/7", json={
            "dados": self.dados(), "versao_registro": 1,
        })
        self.assertEqual(200, resposta.status_code)
        self.assertEqual((7, 1), self.atualizados[0][:2])

    def test_arquiva_e_desarquiva_sem_excluir(self):
        primeira = self.cliente.post(
            "/api/gestao-desenvolvimento/7/arquivamento", json={"versao_registro": 1}
        )
        segunda = self.cliente.delete(
            "/api/gestao-desenvolvimento/7/arquivamento", json={"versao_registro": 2}
        )
        self.assertEqual(200, primeira.status_code)
        self.assertEqual(200, segunda.status_code)
        self.assertEqual([(7, 1, True), (7, 2, False)], self.arquivamentos)

    def test_conflito_de_versao_e_mensagem_segura(self):
        def conflito(*_args):
            raise ErroRepositorioGestaoDesenvolvimento("CONFLITO_VERSAO", "SQL secreto")
        self.app.config["ATUALIZAR_GESTAO_DESENVOLVIMENTO"] = conflito
        resposta = self.cliente.put("/api/gestao-desenvolvimento/7", json={
            "dados": self.dados(), "versao_registro": 1,
        })
        self.assertEqual(409, resposta.status_code)
        self.assertNotIn("SQL secreto", resposta.get_data(as_text=True))

    def test_rejeita_chave_e_campos_tecnicos(self):
        for corpo in (
            {"dados": self.dados(), "chave_idempotencia": "curta"},
            {"dados": self.dados() | {"id_manutencao": 2}, "chave_idempotencia": "a" * 64},
        ):
            with self.subTest(corpo=corpo):
                self.assertEqual(400, self.cliente.post("/api/gestao-desenvolvimento", json=corpo).status_code)


if __name__ == "__main__":
    unittest.main()
