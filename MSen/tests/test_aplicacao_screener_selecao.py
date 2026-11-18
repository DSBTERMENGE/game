import unittest
from types import SimpleNamespace

from msen.services.aplicacao_screener_selecao import aplicar_screener_selecao
from msen.services.solicitacao_screener_selecao import SolicitacaoScreenerSelecao


class AplicacaoScreenerSelecaoTestCase(unittest.TestCase):
    def test_entrega_contrato_e_plano_ao_motor_comum(self):
        recebidos = {}
        solicitacao = SolicitacaoScreenerSelecao.criar(
            id_alvo=9, quantidade_maxima_jogos=10,
            valor_unitario_centavos=500, limite_raridade=10,
        )

        familias = (object(),)

        def executar(combinacoes, plano_recebido, *, limite_aprovadas):
            recebidos.update(
                combinacoes=combinacoes, familias=plano_recebido,
                limite_aprovadas=limite_aprovadas,
            )
            return SimpleNamespace(
                total_inicial=7,
                total_aprovado=2,
                total_excluido=5,
                combinacoes_aprovadas=((1, 2, 3, 4, 5, 6), (1, 2, 3, 4, 5, 7)),
            )

        resultado = aplicar_screener_selecao(
            solicitacao,
            verificar_referencias=lambda: {
                "atualizado": True, "quantidade_resultados": 3069,
            },
            carregar_dezenas=lambda id_alvo: (1, 2, 3, 4, 5, 6, 7),
            montar_plano=lambda _limite: SimpleNamespace(familias=familias),
            executar=executar,
        )
        self.assertEqual(7, resultado["total_recebido"])
        self.assertEqual(2, resultado["total_aprovado"])
        self.assertEqual(7, recebidos["combinacoes"].total_combinacoes)
        self.assertIs(familias, recebidos["familias"])
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
                montar_plano=lambda _limite: chamadas.append("plano"),
            )
        self.assertEqual([], chamadas)


if __name__ == "__main__":
    unittest.main()
