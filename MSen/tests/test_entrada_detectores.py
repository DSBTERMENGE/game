"""Testes da validação compartilhada da entrada dos detectores."""

import unittest

from msen.padroes.entrada import validar_dezenas


class EntradaDetectoresTestCase(unittest.TestCase):
    def test_valida_e_ordena_seis_dezenas(self) -> None:
        self.assertEqual(
            (1, 7, 15, 26, 42, 60),
            validar_dezenas([60, 7, 42, 1, 26, 15]),
        )

    def test_rejeita_objeto_que_nao_e_sequencia(self) -> None:
        with self.assertRaises(TypeError):
            validar_dezenas({1, 2, 3, 4, 5, 6})

    def test_rejeita_texto_mesmo_sendo_sequencia(self) -> None:
        with self.assertRaises(TypeError):
            validar_dezenas("123456")

    def test_rejeita_quantidade_diferente_de_seis(self) -> None:
        for dezenas in ((1, 2, 3, 4, 5), (1, 2, 3, 4, 5, 6, 7)):
            with self.subTest(dezenas=dezenas), self.assertRaises(ValueError):
                validar_dezenas(dezenas)

    def test_rejeita_booleano_e_numero_nao_inteiro(self) -> None:
        for invalida in (True, 3.5):
            dezenas = (1, 2, invalida, 4, 5, 6)
            with self.subTest(invalida=invalida), self.assertRaises(TypeError):
                validar_dezenas(dezenas)

    def test_rejeita_dezena_fora_da_faixa(self) -> None:
        for dezenas in ((0, 2, 3, 4, 5, 6), (1, 2, 3, 4, 5, 61)):
            with self.subTest(dezenas=dezenas), self.assertRaises(ValueError):
                validar_dezenas(dezenas)

    def test_rejeita_dezenas_repetidas(self) -> None:
        with self.assertRaises(ValueError):
            validar_dezenas((1, 2, 3, 4, 5, 5))


if __name__ == "__main__":
    unittest.main()
