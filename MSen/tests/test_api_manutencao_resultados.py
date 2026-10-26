import unittest
from datetime import datetime, timezone

from msen.api import criar_app
from msen.calculos import calcular_resultado
from msen.database import ErroRepositorioResultado, ResultadoPersistido


def persistir_em_memoria(entrada, identificador=10):
    instante = datetime(2026, 10, 26, tzinfo=timezone.utc)
    return ResultadoPersistido(
        identificador,
        calcular_resultado(entrada),
        instante,
        instante,
    )


class ApiManutencaoResultadosTestCase(unittest.TestCase):
    def _cliente(self, incluir=persistir_em_memoria, editar=persistir_em_memoria):
        return criar_app({
            "TESTING": True,
            "INCLUIR_RESULTADO": incluir,
            "EDITAR_RESULTADO": editar,
        }).test_client()

    def test_inclusao_valida_recalcula_e_retorna_201(self):
        resposta = self._cliente().post("/api/resultados", json={
            "numero_ap": 3070,
            "data_resultado": "20/10/2026",
            "dezenas": [1, 10, 20, 30, 40, 60],
            "soma_res": 9999,
        })

        resultado = resposta.get_json()["resultado"]
        self.assertEqual(201, resposta.status_code)
        self.assertEqual(161, resultado["soma_res"])
        self.assertEqual("26.833333", resultado["media_aritmetica_res"])
        self.assertEqual("25.0", resultado["mediana_res"])
        self.assertEqual([1, 10, 20, 30, 40, 60], resultado["dezenas"])

    def test_edicao_valida_usa_numero_da_url_e_recalcula_tudo(self):
        recebidas = []

        def editar(entrada):
            recebidas.append(entrada)
            return persistir_em_memoria(entrada)

        resposta = self._cliente(editar=editar).put("/api/resultados/12", json={
            "data_resultado": "2026-10-21",
            "dezenas": [2, 12, 22, 32, 42, 52],
        })

        resultado = resposta.get_json()["resultado"]
        self.assertEqual(200, resposta.status_code)
        self.assertEqual(12, recebidas[0].numero_ap)
        self.assertEqual("2026-10-21", resultado["data_resultado"])
        self.assertEqual(162, resultado["soma_res"])
        self.assertEqual("27.000000", resultado["media_aritmetica_res"])

    def test_aceita_seis_campos_res_em_vez_do_vetor_dezenas(self):
        resposta = self._cliente().post("/api/resultados", json={
            "numero_ap": 3070,
            "data_resultado": "2026-10-20",
            "res_01": 1, "res_02": 2, "res_03": 3,
            "res_04": 4, "res_05": 5, "res_06": 6,
        })
        self.assertEqual(201, resposta.status_code)
        self.assertEqual(21, resposta.get_json()["resultado"]["soma_res"])

    def test_rejeita_entrada_invalida_antes_de_chamar_servico(self):
        chamado = False

        def incluir(_entrada):
            nonlocal chamado
            chamado = True

        resposta = self._cliente(incluir=incluir).post("/api/resultados", json={
            "numero_ap": 3070,
            "data_resultado": "20/10/2026",
            "dezenas": [1, 2, 3, 4, 5, 5],
        })
        self.assertEqual(400, resposta.status_code)
        self.assertEqual("RESULTADO_REPETIDO", resposta.get_json()["erro"]["codigo"])
        self.assertFalse(chamado)

    def test_rejeita_corpo_que_nao_seja_objeto_json(self):
        resposta = self._cliente().post("/api/resultados", json=[1, 2, 3])
        self.assertEqual(400, resposta.status_code)
        self.assertEqual("JSON_INVALIDO", resposta.get_json()["erro"]["codigo"])

    def test_duplicidade_retorna_conflito(self):
        def duplicado(_entrada):
            raise ErroRepositorioResultado("RESULTADO_DUPLICADO", "detalhe interno")

        resposta = self._cliente(incluir=duplicado).post("/api/resultados", json={
            "numero_ap": 3069,
            "data_resultado": "20/10/2026",
            "dezenas": [1, 2, 3, 4, 5, 6],
        })
        self.assertEqual(409, resposta.status_code)
        self.assertEqual("RESULTADO_DUPLICADO", resposta.get_json()["erro"]["codigo"])

    def test_edicao_inexistente_retorna_404(self):
        def inexistente(_entrada):
            raise ErroRepositorioResultado("RESULTADO_NAO_ENCONTRADO", "interno")

        resposta = self._cliente(editar=inexistente).put("/api/resultados/9999", json={
            "data_resultado": "20/10/2026",
            "dezenas": [1, 2, 3, 4, 5, 6],
        })
        self.assertEqual(404, resposta.status_code)
        self.assertEqual("RESULTADO_NAO_ENCONTRADO", resposta.get_json()["erro"]["codigo"])

    def test_numero_do_corpo_divergente_da_url_retorna_conflito(self):
        resposta = self._cliente().put("/api/resultados/3070", json={
            "numero_ap": 3071,
            "data_resultado": "20/10/2026",
            "dezenas": [1, 2, 3, 4, 5, 6],
        })
        self.assertEqual(409, resposta.status_code)
        self.assertEqual("NUMERO_AP_DIVERGENTE", resposta.get_json()["erro"]["codigo"])

    def test_falha_de_banco_nao_expoe_detalhes(self):
        segredo = "senha-nao-pode-vazar"

        def falhar(_entrada):
            raise ErroRepositorioResultado("FALHA_ATUALIZACAO", segredo)

        resposta = self._cliente(editar=falhar).put("/api/resultados/3070", json={
            "data_resultado": "20/10/2026",
            "dezenas": [1, 2, 3, 4, 5, 6],
        })
        self.assertEqual(503, resposta.status_code)
        self.assertEqual("GRAVACAO_INDISPONIVEL", resposta.get_json()["erro"]["codigo"])
        self.assertNotIn(segredo, resposta.get_data(as_text=True))


if __name__ == "__main__":
    unittest.main()
