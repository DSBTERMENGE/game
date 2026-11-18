from collections.abc import Iterator
import unittest

from msen.services.combinacoes_selecao_dezenas import ErroCombinacoesSelecao
from msen.services.inicializacao_screener_selecao import (
    criar_dicionario_combinacoes,
)


class InicializacaoScreenerSelecaoTestCase(unittest.TestCase):
    def test_cria_uma_combinacao_com_exatamente_seis_dezenas(self):
        dados = criar_dicionario_combinacoes((6, 1, 5, 2, 4, 3))

        self.assertEqual("SELECAO_DE_DEZENAS", dados["origem"])
        self.assertEqual((1, 2, 3, 4, 5, 6), dados["dezenas_selecionadas"])
        self.assertEqual(6, dados["quantidade_dezenas"])
        self.assertEqual(1, dados["quantidade_combinacoes"])
        self.assertEqual(((1, 2, 3, 4, 5, 6),), tuple(dados["itens"]))

    def test_cria_todas_as_combinacoes_em_ordem(self):
        dados = criar_dicionario_combinacoes(range(1, 8))
        itens = tuple(dados["itens"])

        self.assertEqual(7, dados["quantidade_combinacoes"])
        self.assertEqual((1, 2, 3, 4, 5, 6), itens[0])
        self.assertEqual((2, 3, 4, 5, 6, 7), itens[-1])
        self.assertEqual(7, len(set(itens)))

    def test_mantem_iterador_sem_materializar_volume(self):
        dados = criar_dicionario_combinacoes(range(1, 27))

        self.assertIsInstance(dados["itens"], Iterator)
        self.assertEqual(230_230, dados["quantidade_combinacoes"])
        self.assertTrue(dados["volume_elevado"])

    def test_rejeita_menos_de_seis_dezenas(self):
        with self.assertRaises(ErroCombinacoesSelecao) as contexto:
            criar_dicionario_combinacoes(range(1, 6))
        self.assertEqual("DEZENAS_INSUFICIENTES", contexto.exception.codigo)

    def test_rejeita_repeticao_e_limites_invalidos(self):
        for dezenas in ((1, 2, 3, 4, 5, 5), (1, 2, 3, 4, 5, 61)):
            with self.subTest(dezenas=dezenas):
                with self.assertRaises(ValueError):
                    criar_dicionario_combinacoes(dezenas)


if __name__ == "__main__":
    unittest.main()
