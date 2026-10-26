import unittest
from datetime import datetime, timezone

from msen.api import criar_app
from msen.calculos import calcular_resultado
from msen.database import ErroConexaoBanco, ResultadoPersistido
from msen.modelos import ResultadoEntrada


def persistido(id_resultado, numero_ap, data, dezenas):
    calculado = calcular_resultado(ResultadoEntrada.criar(
        numero_ap=numero_ap, data_resultado=data, resultados=dezenas,
    ))
    instante = datetime(2026, 10, 26, tzinfo=timezone.utc)
    return ResultadoPersistido(id_resultado, calculado, instante, instante)


class ApiResultadosTestCase(unittest.TestCase):
    def _cliente(self, resultados=()):
        return criar_app({
            "TESTING": True,
            "LISTAR_RESULTADOS": lambda: tuple(resultados),
        }).test_client()

    def test_lista_vazia(self):
        resposta = self._cliente().get("/api/resultados")
        self.assertEqual(200, resposta.status_code)
        self.assertEqual({"resultados": [], "total": 0}, resposta.get_json())

    def test_lista_valida_no_contrato_do_frontend(self):
        item = persistido(1, 3069, "11/10/2026", [47, 5, 22, 44, 57, 19])
        resposta = self._cliente([item]).get("/api/resultados")
        corpo = resposta.get_json()
        self.assertEqual(200, resposta.status_code)
        self.assertEqual(1, corpo["total"])
        resultado = corpo["resultados"][0]
        self.assertEqual(3069, resultado["numero_ap"])
        self.assertEqual("2026-10-11", resultado["data_resultado"])
        self.assertEqual([47, 5, 22, 44, 57, 19], resultado["dezenas"])
        self.assertEqual(47, resultado["res_01"])
        self.assertEqual(194, resultado["soma_res"])

    def test_decimais_sao_texto_com_precisao_preservada(self):
        item = persistido(1, 3069, "11/10/2026", [47, 5, 22, 44, 57, 19])
        resultado = self._cliente([item]).get("/api/resultados").get_json()["resultados"][0]
        self.assertEqual("32.333333", resultado["media_aritmetica_res"])
        self.assertEqual("33.0", resultado["mediana_res"])
        self.assertEqual("18.217818", resultado["desvio_padrao_media"])
        self.assertEqual("4.666667", resultado["media_coordenada_x"])
        self.assertEqual("2.666667", resultado["media_coordenada_y"])

    def test_ordena_por_numero_ap_crescente(self):
        itens = [
            persistido(3, 3, "03/01/2026", [3, 13, 23, 33, 43, 53]),
            persistido(1, 1, "01/01/2026", [1, 11, 21, 31, 41, 51]),
            persistido(2, 2, "02/01/2026", [2, 12, 22, 32, 42, 52]),
        ]
        resultados = self._cliente(itens).get("/api/resultados").get_json()["resultados"]
        self.assertEqual([1, 2, 3], [item["numero_ap"] for item in resultados])

    def test_erro_do_banco_nao_expoe_credenciais(self):
        segredo = "senha-que-nao-pode-aparecer"

        def falhar():
            raise ErroConexaoBanco("FALHA_CONEXAO", f"falha com {segredo}")

        cliente = criar_app({"TESTING": True, "LISTAR_RESULTADOS": falhar}).test_client()
        resposta = cliente.get("/api/resultados")
        texto = resposta.get_data(as_text=True)
        self.assertEqual(503, resposta.status_code)
        self.assertNotIn(segredo, texto)
        self.assertEqual("BANCO_INDISPONIVEL", resposta.get_json()["erro"]["codigo"])

    def test_resposta_e_json(self):
        resposta = self._cliente().get("/api/resultados")
        self.assertEqual("application/json", resposta.content_type)


if __name__ == "__main__":
    unittest.main()
