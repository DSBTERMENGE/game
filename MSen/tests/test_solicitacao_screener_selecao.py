import unittest

from msen.services.solicitacao_screener_selecao import (
    ErroSolicitacaoScreenerSelecao,
    SolicitacaoScreenerSelecao,
)


class SolicitacaoScreenerSelecaoTestCase(unittest.TestCase):
    def test_cria_contrato_sem_executar_processamento(self):
        solicitacao = SolicitacaoScreenerSelecao.criar(
            id_alvo=9,
            quantidade_maxima_jogos=120,
            valor_unitario_centavos=500,
            limite_raridade="10.000000",
        )
        self.assertEqual(9, solicitacao.id_alvo)
        self.assertEqual(120, solicitacao.quantidade_maxima_jogos)
        self.assertEqual(500, solicitacao.valor_unitario_centavos)
        self.assertEqual("10.000000", str(solicitacao.limite_raridade))

    def test_rejeita_identificador_invalido(self):
        self._rejeita(id_alvo=0)

    def test_rejeita_quantidade_fora_do_limite(self):
        self._rejeita(quantidade_maxima_jogos=0)
        self._rejeita(quantidade_maxima_jogos=50_063_861)

    def test_rejeita_valor_unitario_invalido(self):
        self._rejeita(valor_unitario_centavos=0)

    def test_rejeita_limite_de_raridade_invalido(self):
        for limite in ("texto", -1, 101, "NaN"):
            with self.subTest(limite=limite):
                self._rejeita(limite_raridade=limite)

    def _rejeita(self, **alteracao):
        dados = {
            "id_alvo": 9,
            "quantidade_maxima_jogos": 120,
            "valor_unitario_centavos": 500,
            "limite_raridade": 10,
        }
        dados.update(alteracao)
        with self.assertRaises(ErroSolicitacaoScreenerSelecao):
            SolicitacaoScreenerSelecao.criar(**dados)


if __name__ == "__main__":
    unittest.main()
