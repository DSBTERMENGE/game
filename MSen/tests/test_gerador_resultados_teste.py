import unittest

from msen.validacao import chave_canonica, gerar_combinacoes_teste


class GeradorResultadosTesteTestCase(unittest.TestCase):
    def test_gera_exatamente_mil_combinacoes_validas_e_unicas(self):
        combinacoes = gerar_combinacoes_teste()

        self.assertEqual(1_000, len(combinacoes))
        self.assertTrue(all(len(item) == 6 for item in combinacoes))
        self.assertTrue(all(len(set(item)) == 6 for item in combinacoes))
        self.assertTrue(
            all(1 <= dezena <= 60 for item in combinacoes for dezena in item)
        )
        self.assertEqual(
            1_000,
            len({chave_canonica(item) for item in combinacoes}),
        )

    def test_chave_canonica_reconhece_permutacoes_como_mesma_combinacao(self):
        primeira = (1, 50, 15, 20, 40, 5)
        permutacao = (15, 50, 1, 20, 40, 5)

        self.assertEqual(
            (1, 5, 15, 20, 40, 50),
            chave_canonica(primeira),
        )
        self.assertEqual(chave_canonica(primeira), chave_canonica(permutacao))

    def test_descarta_permutacao_repetida_e_preserva_ordem_dos_aceitos(self):
        sorteios = iter((
            (1, 50, 15, 20, 40, 5),
            (15, 50, 1, 20, 40, 5),
            (60, 2, 31, 9, 47, 18),
        ))

        combinacoes = gerar_combinacoes_teste(2, sortear=lambda: next(sorteios))

        self.assertEqual((
            (1, 50, 15, 20, 40, 5),
            (60, 2, 31, 9, 47, 18),
        ), combinacoes)

    def test_rejeita_quantidade_invalida(self):
        for quantidade in (True, 1.5, "1000"):
            with self.subTest(quantidade=quantidade):
                with self.assertRaises(TypeError):
                    gerar_combinacoes_teste(quantidade)  # type: ignore[arg-type]
        for quantidade in (0, -1, 50_063_861):
            with self.subTest(quantidade=quantidade):
                with self.assertRaises(ValueError):
                    gerar_combinacoes_teste(quantidade)

    def test_rejeita_sorteio_com_quantidade_de_dezenas_invalida(self):
        for combinacao in ((1, 2, 3, 4, 5), (1, 2, 3, 4, 5, 6, 7)):
            with self.subTest(combinacao=combinacao):
                with self.assertRaises(ValueError):
                    gerar_combinacoes_teste(1, sortear=lambda: combinacao)

    def test_rejeita_sorteio_com_dezenas_repetidas_ou_fora_do_intervalo(self):
        for combinacao in (
            (1, 1, 2, 3, 4, 5),
            (0, 1, 2, 3, 4, 5),
            (1, 2, 3, 4, 5, 61),
        ):
            with self.subTest(combinacao=combinacao):
                with self.assertRaises(ValueError):
                    gerar_combinacoes_teste(1, sortear=lambda: combinacao)

    def test_rejeita_sorteio_com_tipo_invalido(self):
        for combinacao in (
            "1,2,3,4,5,6",
            (1, 2, 3, 4, 5, True),
            (1, 2, 3, 4, 5, 6.0),
        ):
            with self.subTest(combinacao=combinacao):
                with self.assertRaises(TypeError):
                    gerar_combinacoes_teste(1, sortear=lambda: combinacao)


if __name__ == "__main__":
    unittest.main()
