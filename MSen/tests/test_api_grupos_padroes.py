"""Testes da API CRUD dos grupos de padrões."""

import unittest

from msen.api import criar_app
from msen.database import ErroRepositorioGrupoPadrao, GrupoPadraoPersistido


def grupo(
    codigo: str = "PG_001",
    nome: str = "Dezenas sequenciais",
    descricao: str = "Descrição do grupo",
    *,
    identificador: int = 1,
) -> GrupoPadraoPersistido:
    """Cria um grupo persistido simples para os testes simulados."""

    return GrupoPadraoPersistido(identificador, codigo, nome, descricao)


class ApiGruposPadroesTestCase(unittest.TestCase):
    """Confere respostas e proteções HTTP sem acessar PostgreSQL."""

    def _cliente(self, **servicos):
        configuracao = {
            "TESTING": True,
            "LISTAR_GRUPOS_PADROES": lambda: (),
            "CRIAR_GRUPO_PADRAO": lambda nome, descricao: grupo(
                "PG_002", nome, descricao, identificador=2
            ),
            "EDITAR_GRUPO_PADRAO": lambda codigo, nome, descricao: grupo(
                codigo, nome, descricao
            ),
            "EXCLUIR_GRUPO_PADRAO": lambda codigo: grupo(codigo),
        }
        configuracao.update(servicos)
        return criar_app(configuracao).test_client()

    def test_lista_grupos(self):
        resposta = self._cliente(
            LISTAR_GRUPOS_PADROES=lambda: (grupo(),)
        ).get("/api/grupos-padroes")
        corpo = resposta.get_json()
        self.assertEqual(200, resposta.status_code)
        self.assertEqual(1, corpo["total"])
        self.assertEqual("PG_001", corpo["grupos"][0]["grupo_cod"])

    def test_cria_com_codigo_automatico(self):
        recebidos = []

        def criar(nome, descricao):
            recebidos.append((nome, descricao))
            return grupo("PG_002", nome, descricao, identificador=2)

        resposta = self._cliente(CRIAR_GRUPO_PADRAO=criar).post(
            "/api/grupos-padroes",
            json={"grupo_nome": "  Colunas  ", "grupo_descr": "  Regra  "},
        )
        self.assertEqual(201, resposta.status_code)
        self.assertEqual([("Colunas", "Regra")], recebidos)
        self.assertEqual("PG_002", resposta.get_json()["grupo"]["grupo_cod"])

    def test_edita_nome_e_descricao(self):
        recebidos = []

        def editar(codigo, nome, descricao):
            recebidos.append((codigo, nome, descricao))
            return grupo(codigo, nome, descricao)

        resposta = self._cliente(EDITAR_GRUPO_PADRAO=editar).put(
            "/api/grupos-padroes/PG_001",
            json={"grupo_nome": "Novo nome", "grupo_descr": "Novo texto"},
        )
        self.assertEqual(200, resposta.status_code)
        self.assertEqual(
            [("PG_001", "Novo nome", "Novo texto")], recebidos
        )

    def test_exclui_grupo_vazio(self):
        resposta = self._cliente().delete("/api/grupos-padroes/PG_002")
        self.assertEqual(200, resposta.status_code)
        self.assertEqual("Grupo excluído.", resposta.get_json()["mensagem"])

    def test_rejeita_campos_protegidos(self):
        for campo, valor in (("id_grupo", 9), ("grupo_cod", "PG_999")):
            with self.subTest(campo=campo):
                resposta = self._cliente().post(
                    "/api/grupos-padroes",
                    json={
                        "grupo_nome": "Nome",
                        "grupo_descr": "Descrição",
                        campo: valor,
                    },
                )
                self.assertEqual(400, resposta.status_code)
                self.assertEqual(
                    "CAMPOS_PROTEGIDOS", resposta.get_json()["erro"]["codigo"]
                )

    def test_rejeita_json_campos_e_textos_invalidos(self):
        casos = (
            ([], "JSON_INVALIDO"),
            ({"grupo_nome": "Nome", "grupo_descr": "Texto", "extra": 1}, "CAMPOS_DESCONHECIDOS"),
            ({"grupo_nome": " ", "grupo_descr": "Texto"}, "NOME_INVALIDO"),
            ({"grupo_nome": "Nome", "grupo_descr": " "}, "DESCRICAO_INVALIDA"),
        )
        for corpo, codigo in casos:
            with self.subTest(codigo=codigo):
                resposta = self._cliente().post("/api/grupos-padroes", json=corpo)
                self.assertEqual(400, resposta.status_code)
                self.assertEqual(codigo, resposta.get_json()["erro"]["codigo"])

    def test_rejeita_codigo_invalido(self):
        resposta = self._cliente().delete("/api/grupos-padroes/pg-1")
        self.assertEqual(400, resposta.status_code)
        self.assertEqual("CODIGO_INVALIDO", resposta.get_json()["erro"]["codigo"])

    def test_duplicidade_retorna_conflito(self):
        def duplicar(_nome, _descricao):
            raise ErroRepositorioGrupoPadrao("GRUPO_DUPLICADO", "interno")

        resposta = self._cliente(CRIAR_GRUPO_PADRAO=duplicar).post(
            "/api/grupos-padroes",
            json={"grupo_nome": "Nome", "grupo_descr": "Descrição"},
        )
        self.assertEqual(409, resposta.status_code)
        self.assertEqual("GRUPO_DUPLICADO", resposta.get_json()["erro"]["codigo"])

    def test_grupo_em_uso_retorna_conflito(self):
        def em_uso(_codigo):
            raise ErroRepositorioGrupoPadrao("GRUPO_EM_USO", "interno")

        resposta = self._cliente(EXCLUIR_GRUPO_PADRAO=em_uso).delete(
            "/api/grupos-padroes/PG_001"
        )
        self.assertEqual(409, resposta.status_code)
        self.assertEqual("GRUPO_EM_USO", resposta.get_json()["erro"]["codigo"])

    def test_ausente_retorna_404(self):
        def ausente(_codigo):
            raise ErroRepositorioGrupoPadrao("GRUPO_NAO_ENCONTRADO", "interno")

        resposta = self._cliente(EXCLUIR_GRUPO_PADRAO=ausente).delete(
            "/api/grupos-padroes/PG_999"
        )
        self.assertEqual(404, resposta.status_code)
        self.assertEqual(
            "GRUPO_NAO_ENCONTRADO", resposta.get_json()["erro"]["codigo"]
        )

    def test_erro_do_banco_nao_expoe_detalhes(self):
        segredo = "senha-nao-pode-vazar"

        def falhar():
            raise ErroRepositorioGrupoPadrao("FALHA_LISTAGEM", segredo)

        resposta = self._cliente(LISTAR_GRUPOS_PADROES=falhar).get(
            "/api/grupos-padroes"
        )
        self.assertEqual(503, resposta.status_code)
        self.assertNotIn(segredo, resposta.get_data(as_text=True))


if __name__ == "__main__":
    unittest.main()
