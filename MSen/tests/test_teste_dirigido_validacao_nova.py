import unittest

from msen.services import (
    ErroTesteDirigidoValidacaoNova,
    gerar_colecao_dirigida_validacao_nova,
)


class GeradorControlado:
    def __init__(self, itens):
        self.itens = iter(itens)

    def __call__(self):
        return next(self.itens)


class TesteDirigidoValidacaoNovaTestCase(unittest.TestCase):
    def test_mantem_dez_positivas_unicas_em_memoria(self):
        negativas = ((1, 3, 5, 7, 9, 11),)
        positivas = tuple(
            (inicio, inicio + 1, 40, 45, 50, 60)
            for inicio in range(1, 11)
        )
        origem = negativas + (positivas[0][::-1], positivas[0]) + positivas[1:]

        colecao = gerar_colecao_dirigida_validacao_nova(
            2,
            lambda item: item[1] == item[0] + 1 or item[0] == item[1] + 1,
            gerar_combinacao=GeradorControlado(origem),
        )

        self.assertEqual(10, colecao.quantidade)
        self.assertEqual(12, colecao.tentativas)
        self.assertEqual(10, len({tuple(sorted(item)) for item in colecao.combinacoes}))
        self.assertTrue(all(
            item[1] == item[0] + 1 or item[0] == item[1] + 1
            for item in colecao.combinacoes
        ))

    def test_informa_quando_nao_encontra_dez_ocorrencias(self):
        with self.assertRaises(ErroTesteDirigidoValidacaoNova) as contexto:
            gerar_colecao_dirigida_validacao_nova(
                2,
                lambda _item: False,
                quantidade=10,
                maximo_tentativas=10,
                gerar_combinacao=lambda: (1, 2, 3, 4, 5, 6),
            )
        self.assertEqual("OCORRENCIAS_INSUFICIENTES", contexto.exception.codigo)

    def test_rejeita_combinacao_invalida_do_gerador(self):
        with self.assertRaises(ErroTesteDirigidoValidacaoNova) as contexto:
            gerar_colecao_dirigida_validacao_nova(
                2,
                lambda _item: True,
                gerar_combinacao=lambda: (1, 1, 2, 3, 4, 5),
            )
        self.assertEqual("COMBINACAO_GERADA_INVALIDA", contexto.exception.codigo)

    def test_valida_parametros(self):
        with self.assertRaises(ValueError):
            gerar_colecao_dirigida_validacao_nova(0, lambda _item: True)
        with self.assertRaises(ValueError):
            gerar_colecao_dirigida_validacao_nova(
                1, lambda _item: True, quantidade=10, maximo_tentativas=9
            )


if __name__ == "__main__":
    unittest.main()
