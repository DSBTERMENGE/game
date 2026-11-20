import unittest
from unittest.mock import Mock

from msen.api import criar_app
from msen.services import (
    ErroCatalogoFiltrosValidacao,
    FiltroExecutavelValidacao,
    GrupoFiltrosValidacao,
)


class ApiValidacaoNovaTestCase(unittest.TestCase):
    def _cliente(self, catalogo=(), gerenciador=None, dirigido=None):
        servico = catalogo if callable(catalogo) else lambda: catalogo
        gerenciador = gerenciador or Mock()
        return criar_app({
            "TESTING": True,
            "CONSULTAR_CATALOGO_VALIDACAO_NOVA": servico,
            "GERENCIADOR_VALIDACAO_NOVA": gerenciador,
            "GERENCIADOR_TESTES_DIRIGIDOS_VALIDACAO_NOVA": dirigido or Mock(),
        }).test_client()

    def test_lista_somente_ids_nomes_e_descricoes(self):
        grupos = (
            GrupoFiltrosValidacao(
                9,
                "1 linha e 1 coluna",
                (FiltroExecutavelValidacao(16, "Linha e coluna", "Descrição"),),
            ),
        )
        resposta = self._cliente(grupos).get("/api/validacao-nova/filtros")
        corpo = resposta.get_json()

        self.assertEqual(200, resposta.status_code)
        self.assertEqual(1, corpo["total_grupos"])
        self.assertEqual(1, corpo["total_filtros"])
        self.assertEqual({
            "id_grupo", "nome_grupo", "filtros"
        }, set(corpo["grupos"][0]))
        self.assertEqual({
            "id_filtro", "nome_filtro", "descricao"
        }, set(corpo["grupos"][0]["filtros"][0]))
        texto = repr(corpo).lower()
        self.assertNotIn("codigo", texto)
        self.assertNotIn("funcao", texto)

    def test_catalogo_vazio_e_resposta_valida(self):
        resposta = self._cliente().get("/api/validacao-nova/filtros")
        self.assertEqual(200, resposta.status_code)
        self.assertEqual(
            {"total_grupos": 0, "total_filtros": 0, "grupos": []},
            resposta.get_json(),
        )

    def test_rejeita_parametros(self):
        resposta = self._cliente().get("/api/validacao-nova/filtros?grupo=9")
        self.assertEqual(400, resposta.status_code)
        self.assertEqual(
            "PARAMETROS_NAO_PERMITIDOS", resposta.get_json()["erro"]["codigo"]
        )

    def test_falha_do_catalogo_retorna_mensagem_segura(self):
        def falhar():
            raise ErroCatalogoFiltrosValidacao("falha interna")

        resposta = self._cliente(falhar).get("/api/validacao-nova/filtros")
        self.assertEqual(503, resposta.status_code)
        self.assertEqual("CATALOGO_INDISPONIVEL", resposta.get_json()["erro"]["codigo"])
        self.assertNotIn("falha interna", resposta.get_data(as_text=True))

    def test_inicia_todos_ou_lista_de_filtros(self):
        gerenciador = Mock()
        gerenciador.iniciar.side_effect = (
            {"id": "todos", "estado": "AGUARDANDO"},
            {"id": "alguns", "estado": "AGUARDANDO"},
        )
        cliente = self._cliente(gerenciador=gerenciador)

        todos = cliente.post("/api/validacao-nova/execucoes", json={})
        alguns = cliente.post(
            "/api/validacao-nova/execucoes", json={"ids_filtros": [10, 20]}
        )

        self.assertEqual(202, todos.status_code)
        self.assertEqual(202, alguns.status_code)
        self.assertEqual([unittest.mock.call(None), unittest.mock.call((10, 20))],
                         gerenciador.iniciar.call_args_list)

    def test_rejeita_selecao_invalida_antes_de_iniciar(self):
        gerenciador = Mock()
        cliente = self._cliente(gerenciador=gerenciador)
        casos = (
            ({"ids_filtros": []}, "SELECAO_VAZIA"),
            ({"ids_filtros": [True]}, "IDENTIFICADOR_INVALIDO"),
            ({"ids_filtros": [2, 2]}, "FILTRO_REPETIDO"),
            ({"outro": 1}, "SOLICITACAO_INVALIDA"),
        )
        for corpo, codigo in casos:
            with self.subTest(codigo=codigo):
                resposta = cliente.post("/api/validacao-nova/execucoes", json=corpo)
                self.assertEqual(400, resposta.status_code)
                self.assertEqual(codigo, resposta.get_json()["erro"]["codigo"])
        gerenciador.iniciar.assert_not_called()

    def test_consulta_e_cancela_execucao(self):
        gerenciador = Mock()
        gerenciador.obter.return_value = {"id": "abc", "estado": "EXECUTANDO"}
        gerenciador.cancelar.return_value = {"id": "abc", "estado": "CANCELANDO"}
        gerenciador.continuar.return_value = {"id": "abc", "estado": "EXECUTANDO"}
        gerenciador.concluir.return_value = {"id": "abc", "estado": "EXECUTANDO"}
        cliente = self._cliente(gerenciador=gerenciador)

        consulta = cliente.get("/api/validacao-nova/execucoes/abc")
        cancelamento = cliente.post(
            "/api/validacao-nova/execucoes/abc/cancelamento"
        )
        continuacao = cliente.post(
            "/api/validacao-nova/execucoes/abc/continuacao"
        )
        conclusao = cliente.post("/api/validacao-nova/execucoes/abc/conclusao")

        self.assertEqual(200, consulta.status_code)
        self.assertEqual(202, cancelamento.status_code)
        self.assertEqual(202, continuacao.status_code)
        self.assertEqual(202, conclusao.status_code)
        self.assertEqual("CANCELANDO", cancelamento.get_json()["estado"])

    def test_execucao_inexistente_retorna_404(self):
        gerenciador = Mock()
        gerenciador.obter.side_effect = KeyError("ausente")
        gerenciador.cancelar.side_effect = KeyError("ausente")
        gerenciador.continuar.side_effect = KeyError("ausente")
        gerenciador.concluir.side_effect = KeyError("ausente")
        cliente = self._cliente(gerenciador=gerenciador)
        self.assertEqual(404, cliente.get(
            "/api/validacao-nova/execucoes/ausente"
        ).status_code)
        self.assertEqual(404, cliente.post(
            "/api/validacao-nova/execucoes/ausente/cancelamento"
        ).status_code)
        self.assertEqual(404, cliente.post(
            "/api/validacao-nova/execucoes/ausente/continuacao"
        ).status_code)
        self.assertEqual(404, cliente.post(
            "/api/validacao-nova/execucoes/ausente/conclusao"
        ).status_code)

    def test_gera_consulta_e_executa_teste_dirigido(self):
        dirigido = Mock()
        dirigido.criar.return_value = {"id": "dir-1", "estado": "GERADO"}
        dirigido.obter.return_value = {"id": "dir-1", "estado": "GERADO"}
        dirigido.testar.return_value = {"id": "dir-1", "estado": "TESTADO"}
        dirigido.continuar.return_value = {
            "id": "dir-1", "estado": "AGUARDANDO_CONFIRMACAO"
        }
        dirigido.cancelar.return_value = {"id": "dir-1", "estado": "CANCELADO"}
        dirigido.concluir.return_value = {"id": "dir-1", "estado": "TESTADO"}
        cliente = self._cliente(dirigido=dirigido)

        criado = cliente.post(
            "/api/validacao-nova/testes-dirigidos",
            json={"id_grupo": 2, "id_filtro": 12},
        )
        consulta = cliente.get("/api/validacao-nova/testes-dirigidos/dir-1")
        teste = cliente.post(
            "/api/validacao-nova/testes-dirigidos/dir-1/execucao"
        )
        continuacao = cliente.post(
            "/api/validacao-nova/testes-dirigidos/dir-1/continuacao"
        )
        cancelamento = cliente.post(
            "/api/validacao-nova/testes-dirigidos/dir-1/cancelamento"
        )
        conclusao = cliente.post(
            "/api/validacao-nova/testes-dirigidos/dir-1/conclusao"
        )

        self.assertEqual(201, criado.status_code)
        self.assertEqual(200, consulta.status_code)
        self.assertEqual("TESTADO", teste.get_json()["estado"])
        self.assertEqual(202, continuacao.status_code)
        self.assertEqual(202, cancelamento.status_code)
        self.assertEqual(202, conclusao.status_code)
        self.assertEqual("CANCELADO", cancelamento.get_json()["estado"])
        dirigido.criar.assert_called_once_with(2, 12)

    def test_teste_dirigido_exige_grupo_e_filtro_especificos(self):
        dirigido = Mock()
        cliente = self._cliente(dirigido=dirigido)
        for corpo in ({}, {"id_grupo": 2}, {"id_grupo": 0, "id_filtro": 12}):
            with self.subTest(corpo=corpo):
                resposta = cliente.post(
                    "/api/validacao-nova/testes-dirigidos", json=corpo
                )
                self.assertEqual(400, resposta.status_code)
        dirigido.criar.assert_not_called()

    def test_teste_dirigido_inexistente_retorna_404(self):
        dirigido = Mock()
        dirigido.obter.side_effect = KeyError("ausente")
        dirigido.testar.side_effect = KeyError("ausente")
        dirigido.continuar.side_effect = KeyError("ausente")
        dirigido.cancelar.side_effect = KeyError("ausente")
        dirigido.concluir.side_effect = KeyError("ausente")
        cliente = self._cliente(dirigido=dirigido)
        self.assertEqual(404, cliente.get(
            "/api/validacao-nova/testes-dirigidos/ausente"
        ).status_code)
        self.assertEqual(404, cliente.post(
            "/api/validacao-nova/testes-dirigidos/ausente/execucao"
        ).status_code)
        self.assertEqual(404, cliente.post(
            "/api/validacao-nova/testes-dirigidos/ausente/continuacao"
        ).status_code)
        self.assertEqual(404, cliente.post(
            "/api/validacao-nova/testes-dirigidos/ausente/cancelamento"
        ).status_code)
        self.assertEqual(404, cliente.post(
            "/api/validacao-nova/testes-dirigidos/ausente/conclusao"
        ).status_code)


if __name__ == "__main__":
    unittest.main()
