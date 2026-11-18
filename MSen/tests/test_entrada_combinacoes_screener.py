import unittest

from msen.screener.entrada_combinacoes import (
    ORIGEM_APLICACAO_INTEGRAL,
    ORIGEM_SELECAO_DEZENAS,
    ORIGEM_TESTE_5000,
    ErroEntradaCombinacoes,
    criar_entrada_combinacoes,
)


class EntradaCombinacoesScreenerTestCase(unittest.TestCase):
    def test_representa_as_tres_origens_do_motor_comum(self):
        for origem in (
            ORIGEM_TESTE_5000,
            ORIGEM_APLICACAO_INTEGRAL,
            ORIGEM_SELECAO_DEZENAS,
        ):
            with self.subTest(origem=origem):
                entrada = criar_entrada_combinacoes(
                    origem=origem,
                    total_combinacoes=1,
                    itens=[(6, 5, 4, 3, 2, 1)],
                )
                self.assertEqual(origem, entrada.origem)
                self.assertEqual((1, 2, 3, 4, 5, 6), next(iter(entrada.itens)))

    def test_nao_percorre_a_colecao_ao_criar_o_contrato(self):
        percorridos = []

        def gerar():
            percorridos.append(True)
            yield (1, 2, 3, 4, 5, 6)

        entrada = criar_entrada_combinacoes(
            origem=ORIGEM_APLICACAO_INTEGRAL,
            total_combinacoes=50_063_860,
            itens=gerar(),
        )

        self.assertEqual([], percorridos)
        self.assertEqual((1, 2, 3, 4, 5, 6), next(iter(entrada.itens)))
        self.assertEqual([True], percorridos)

    def test_rejeita_combinacao_invalida_quando_for_consumida(self):
        entrada = criar_entrada_combinacoes(
            origem=ORIGEM_TESTE_5000,
            total_combinacoes=1,
            itens=[(1, 2, 3, 4, 5, 5)],
        )

        with self.assertRaises(ErroEntradaCombinacoes):
            tuple(entrada.itens)

    def test_preserva_contexto_sem_permitir_alteracao(self):
        entrada = criar_entrada_combinacoes(
            origem=ORIGEM_SELECAO_DEZENAS,
            total_combinacoes=1,
            itens=[(1, 2, 3, 4, 5, 6)],
            contexto={"quantidade_dezenas": 6},
        )

        self.assertEqual(6, entrada.contexto["quantidade_dezenas"])
        with self.assertRaises(TypeError):
            entrada.contexto["quantidade_dezenas"] = 7

    def test_rejeita_envelope_invalido_sem_consumir_itens(self):
        casos = (
            {"origem": "DESCONHECIDA", "total_combinacoes": 1, "itens": []},
            {"origem": ORIGEM_TESTE_5000, "total_combinacoes": 0, "itens": []},
            {"origem": ORIGEM_TESTE_5000, "total_combinacoes": 1, "itens": 42},
        )
        for caso in casos:
            with self.subTest(caso=caso):
                with self.assertRaises(ErroEntradaCombinacoes):
                    criar_entrada_combinacoes(**caso)


if __name__ == "__main__":
    unittest.main()
