import unittest

from msen.services.aplicacao_screener_selecao import aplicar_screener_selecao
from msen.services.solicitacao_screener_selecao import SolicitacaoScreenerSelecao


class AplicacaoScreenerSelecaoTestCase(unittest.TestCase):
    def test_monta_dois_dicionarios_e_chama_orquestradora(self):
        recebidos = {}
        solicitacao = SolicitacaoScreenerSelecao.criar(
            id_alvo=9, quantidade_maxima_jogos=10,
            valor_unitario_centavos=500, limite_raridade=10,
        )

        def orquestrar(combinacoes, filtros, *, limite_aprovadas):
            recebidos.update(
                combinacoes=combinacoes, filtros=filtros,
                limite_aprovadas=limite_aprovadas,
            )
            return {"total_recebido": combinacoes["quantidade_combinacoes"]}

        resultado = aplicar_screener_selecao(
            solicitacao,
            verificar_referencias=lambda: {
                "atualizado": True, "quantidade_resultados": 3069,
            },
            carregar_dezenas=lambda id_alvo: (1, 2, 3, 4, 5, 6, 7),
            carregar_filtros=lambda limite: ({
                "grupo": "estatisticos", "chave": "soma", "id_filtro": 1,
                "id_grupo": None, "nome_filtro": "Soma",
                "tipo_resultado": "NUMERICO", "metodo_comparacao": "FAIXA",
                "referencia": {"limite_inferior": 21, "limite_superior": 300},
            },),
            orquestrar=orquestrar,
        )
        self.assertEqual(7, resultado["total_recebido"])
        self.assertEqual(7, recebidos["combinacoes"]["quantidade_combinacoes"])
        self.assertEqual({"soma"}, set(recebidos["filtros"]["estatisticos"]))
        self.assertNotIn("funcao", recebidos["filtros"]["estatisticos"]["soma"])
        self.assertEqual(10, recebidos["limite_aprovadas"])

    def test_verifica_referencias_antes_de_buscar_dezenas(self):
        chamadas = []

        def falhar():
            chamadas.append("referencias")
            raise RuntimeError("desatualizadas")

        solicitacao = SolicitacaoScreenerSelecao.criar(
            id_alvo=9, quantidade_maxima_jogos=10,
            valor_unitario_centavos=500, limite_raridade=10,
        )
        with self.assertRaises(RuntimeError):
            aplicar_screener_selecao(
                solicitacao, verificar_referencias=falhar,
                carregar_dezenas=lambda _id: chamadas.append("dezenas") or (),
            )
        self.assertEqual(["referencias"], chamadas)

    def test_recusa_volume_elevado_antes_de_carregar_filtros(self):
        chamadas = []
        solicitacao = SolicitacaoScreenerSelecao.criar(
            id_alvo=9, quantidade_maxima_jogos=10,
            valor_unitario_centavos=500, limite_raridade=10,
        )
        with self.assertRaisesRegex(RuntimeError, "10.000"):
            aplicar_screener_selecao(
                solicitacao,
                verificar_referencias=lambda: {
                    "atualizado": True, "quantidade_resultados": 3069,
                },
                carregar_dezenas=lambda _id: tuple(range(1, 20)),
                carregar_filtros=lambda _limite: chamadas.append("filtros") or (),
            )
        self.assertEqual([], chamadas)


if __name__ == "__main__":
    unittest.main()
