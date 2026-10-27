from decimal import Decimal
import unittest

from msen.api import criar_app
from msen.database import ErroRepositorioPadrao, PadraoPersistido


def padrao(
    codigo="PD_001",
    nome="Duas dezenas sequenciais",
    descricao="Descrição do padrão",
    *,
    identificador=1,
    num_oco=2,
    intervalo=Decimal("15.000000"),
    desvio=Decimal("0.000000"),
):
    return PadraoPersistido(
        identificador,
        codigo,
        nome,
        descricao,
        num_oco,
        intervalo,
        desvio,
    )


class ApiPadroesTestCase(unittest.TestCase):
    def _cliente(self, **servicos):
        configuracao = {
            "TESTING": True,
            "LISTAR_PADROES": lambda: (),
            "CRIAR_PADRAO": lambda nome, descricao: padrao(
                "PD_004",
                nome,
                descricao,
                identificador=4,
                num_oco=None,
                intervalo=None,
                desvio=None,
            ),
            "EDITAR_PADRAO": lambda codigo, nome, descricao: padrao(
                codigo, nome, descricao
            ),
            "EXCLUIR_PADRAO": lambda codigo: padrao(codigo),
        }
        configuracao.update(servicos)
        return criar_app(configuracao).test_client()

    def test_lista_estatisticas_e_detector_implementado(self):
        itens = (
            padrao(),
            padrao(
                "PD_004",
                "Ideia futura",
                "Sem detector",
                identificador=4,
                num_oco=None,
                intervalo=None,
                desvio=None,
            ),
        )
        resposta = self._cliente(LISTAR_PADROES=lambda: itens).get("/api/padroes")
        corpo = resposta.get_json()

        self.assertEqual(200, resposta.status_code)
        self.assertEqual(2, corpo["total"])
        self.assertEqual("15.000000", corpo["padroes"][0]["intervalo_medio"])
        self.assertTrue(corpo["padroes"][0]["detector_implementado"])
        self.assertFalse(corpo["padroes"][1]["detector_implementado"])
        self.assertIsNone(corpo["padroes"][1]["num_oco"])

    def test_cria_com_codigo_automatico_e_estatisticas_nulas(self):
        recebidos = []

        def criar(nome, descricao):
            recebidos.append((nome, descricao))
            return padrao(
                "PD_004", nome, descricao, identificador=4,
                num_oco=None, intervalo=None, desvio=None,
            )

        resposta = self._cliente(CRIAR_PADRAO=criar).post(
            "/api/padroes",
            json={"padrao_nome": "  Novo padrão  ", "padrao_descr": "  Regra  "},
        )

        self.assertEqual(201, resposta.status_code)
        self.assertEqual([("Novo padrão", "Regra")], recebidos)
        self.assertEqual("PD_004", resposta.get_json()["padrao"]["padrao_cod"])
        self.assertFalse(resposta.get_json()["padrao"]["detector_implementado"])

    def test_edita_somente_nome_e_descricao(self):
        recebidos = []

        def editar(codigo, nome, descricao):
            recebidos.append((codigo, nome, descricao))
            return padrao(codigo, nome, descricao)

        resposta = self._cliente(EDITAR_PADRAO=editar).put(
            "/api/padroes/PD_001",
            json={"padrao_nome": "Nome revisto", "padrao_descr": "Texto revisto"},
        )

        self.assertEqual(200, resposta.status_code)
        self.assertEqual(
            [("PD_001", "Nome revisto", "Texto revisto")], recebidos
        )
        self.assertEqual(2, resposta.get_json()["padrao"]["num_oco"])

    def test_exclui_e_devolve_o_registro_removido(self):
        resposta = self._cliente().delete("/api/padroes/PD_001")
        self.assertEqual(200, resposta.status_code)
        self.assertEqual("Padrão excluído.", resposta.get_json()["mensagem"])
        self.assertEqual("PD_001", resposta.get_json()["padrao"]["padrao_cod"])

    def test_rejeita_campos_calculados_e_codigo_enviados_pelo_usuario(self):
        for campo, valor in (
            ("padrao_cod", "PD_999"),
            ("id_padrao", 999),
            ("num_oco", 999),
            ("intervalo_medio", "1.000000"),
            ("desv_padrao", "1.000000"),
        ):
            with self.subTest(campo=campo):
                resposta = self._cliente().post(
                    "/api/padroes",
                    json={
                        "padrao_nome": "Nome",
                        "padrao_descr": "Descrição",
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
            ({"padrao_nome": "Nome", "padrao_descr": "Texto", "extra": 1}, "CAMPOS_DESCONHECIDOS"),
            ({"padrao_nome": " ", "padrao_descr": "Texto"}, "NOME_INVALIDO"),
            ({"padrao_nome": "Nome", "padrao_descr": " "}, "DESCRICAO_INVALIDA"),
        )
        for corpo, codigo in casos:
            with self.subTest(codigo=codigo):
                resposta = self._cliente().post("/api/padroes", json=corpo)
                self.assertEqual(400, resposta.status_code)
                self.assertEqual(codigo, resposta.get_json()["erro"]["codigo"])

    def test_rejeita_codigo_de_url_invalido(self):
        resposta = self._cliente().delete("/api/padroes/pd-1")
        self.assertEqual(400, resposta.status_code)
        self.assertEqual("CODIGO_INVALIDO", resposta.get_json()["erro"]["codigo"])

    def test_duplicidade_retorna_conflito(self):
        def duplicar(_nome, _descricao):
            raise ErroRepositorioPadrao("PADRAO_DUPLICADO", "detalhe interno")

        resposta = self._cliente(CRIAR_PADRAO=duplicar).post(
            "/api/padroes",
            json={"padrao_nome": "Nome", "padrao_descr": "Descrição"},
        )
        self.assertEqual(409, resposta.status_code)
        self.assertEqual("PADRAO_DUPLICADO", resposta.get_json()["erro"]["codigo"])

    def test_registro_ausente_retorna_404(self):
        def ausente(_codigo):
            raise ErroRepositorioPadrao("PADRAO_NAO_ENCONTRADO", "interno")

        resposta = self._cliente(EXCLUIR_PADRAO=ausente).delete(
            "/api/padroes/PD_999"
        )
        self.assertEqual(404, resposta.status_code)
        self.assertEqual(
            "PADRAO_NAO_ENCONTRADO", resposta.get_json()["erro"]["codigo"]
        )

    def test_erro_do_banco_nao_expoe_detalhes(self):
        segredo = "senha-nao-pode-vazar"

        def falhar():
            raise ErroRepositorioPadrao("FALHA_LISTAGEM", segredo)

        resposta = self._cliente(LISTAR_PADROES=falhar).get("/api/padroes")
        self.assertEqual(503, resposta.status_code)
        self.assertEqual("BANCO_INDISPONIVEL", resposta.get_json()["erro"]["codigo"])
        self.assertNotIn(segredo, resposta.get_data(as_text=True))


if __name__ == "__main__":
    unittest.main()
