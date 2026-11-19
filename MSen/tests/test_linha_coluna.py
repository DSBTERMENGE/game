import unittest

from msen.padroes.linha_coluna import (
    detectar_dezenas_em_uma_linha_e_uma_coluna,
)
from msen.padroes import criar_registro_detectores_aprovados


class LinhaColunaTestCase(unittest.TestCase):
    def test_pd010_esta_no_catalogo_oficial(self):
        registro = criar_registro_detectores_aprovados()

        self.assertIs(
            detectar_dezenas_em_uma_linha_e_uma_coluna,
            registro.obter("PD_010"),
        )

    def test_detecta_com_intersecao_ocupada(self):
        # Linha 1 e coluna 8; a dezena 08 ocupa a interseção.
        self.assertTrue(
            detectar_dezenas_em_uma_linha_e_uma_coluna((1, 2, 3, 8, 18, 28))
        )

    def test_detecta_com_intersecao_vazia(self):
        # Linha 1 e coluna 8; a dezena 08 não pertence à combinação.
        self.assertTrue(
            detectar_dezenas_em_uma_linha_e_uma_coluna((1, 2, 3, 4, 18, 28))
        )

    def test_detecta_distribuicoes_diferentes_entre_os_bracos(self):
        self.assertTrue(
            detectar_dezenas_em_uma_linha_e_uma_coluna((4, 14, 24, 34, 35, 36))
        )
        self.assertTrue(
            detectar_dezenas_em_uma_linha_e_uma_coluna((21, 22, 23, 24, 25, 35))
        )

    def test_recusa_quando_uma_linha_e_uma_coluna_nao_cobrem_tudo(self):
        self.assertFalse(
            detectar_dezenas_em_uma_linha_e_uma_coluna((1, 2, 13, 14, 25, 36))
        )

    def test_recusa_linha_ou_coluna_isolada(self):
        self.assertFalse(
            detectar_dezenas_em_uma_linha_e_uma_coluna((1, 2, 3, 4, 5, 6))
        )
        self.assertFalse(
            detectar_dezenas_em_uma_linha_e_uma_coluna((1, 11, 21, 31, 41, 51))
        )

    def test_trata_corretamente_dezenas_terminadas_em_zero(self):
        self.assertTrue(
            detectar_dezenas_em_uma_linha_e_uma_coluna((1, 2, 3, 10, 20, 30))
        )
        self.assertTrue(
            detectar_dezenas_em_uma_linha_e_uma_coluna((1, 2, 3, 4, 20, 30))
        )

    def test_valida_quantidade_repeticao_tipo_e_limites(self):
        invalidas = (
            (1, 2, 3, 4, 5),
            (1, 2, 3, 4, 5, 5),
            (0, 1, 2, 3, 4, 5),
            (1, 2, 3, 4, 5, 61),
            (1, 2, 3, 4, 5, "6"),
        )
        for dezenas in invalidas:
            with self.subTest(dezenas=dezenas):
                with self.assertRaises((TypeError, ValueError)):
                    detectar_dezenas_em_uma_linha_e_uma_coluna(dezenas)


if __name__ == "__main__":
    unittest.main()
