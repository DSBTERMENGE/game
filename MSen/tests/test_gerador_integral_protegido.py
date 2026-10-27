from dataclasses import replace
from pathlib import Path
import unittest

from msen.screener import (
    CONFIRMACAO_INTEGRAL,
    TOTAL_COMBINACOES,
    ErroGeracaoIntegral,
    carregar_configuracao_screener,
    criar_iterador_combinacoes,
)


PADRAO = Path(__file__).resolve().parents[1] / "config" / "screener.toml"


class GeradorIntegralProtegidoTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.configuracao = carregar_configuracao_screener(PADRAO)

    def test_total_matematico_do_universo(self):
        self.assertEqual(50_063_860, TOTAL_COMBINACOES)

    def test_modo_amostra_interrompe_exatamente_em_cinco_mil(self):
        combinacoes = tuple(criar_iterador_combinacoes(self.configuracao))
        self.assertEqual(5_000, len(combinacoes))
        self.assertEqual((1, 2, 3, 4, 5, 6), combinacoes[0])
        self.assertEqual(5_000, len(set(combinacoes)))

    def test_amostra_lexicografica_contem_somente_combinacoes_validas(self):
        for combinacao in criar_iterador_combinacoes(self.configuracao):
            self.assertEqual(tuple(sorted(combinacao)), combinacao)
            self.assertEqual(6, len(set(combinacao)))
            self.assertGreaterEqual(combinacao[0], 1)
            self.assertLessEqual(combinacao[-1], 60)

    def test_modo_integral_exige_confirmacao_na_configuracao(self):
        integral = replace(self.configuracao, modo="integral")
        with self.assertRaises(ErroGeracaoIntegral) as contexto:
            criar_iterador_combinacoes(
                integral, confirmacao_integral=CONFIRMACAO_INTEGRAL
            )
        self.assertEqual(
            "CONFIGURACAO_INTEGRAL_NAO_CONFIRMADA", contexto.exception.codigo
        )

    def test_modo_integral_exige_frase_explicita(self):
        integral = replace(
            self.configuracao,
            modo="integral",
            confirmacao_processamento_integral=True,
        )
        with self.assertRaises(ErroGeracaoIntegral) as contexto:
            criar_iterador_combinacoes(integral)
        self.assertEqual("CONFIRMACAO_INTEGRAL_AUSENTE", contexto.exception.codigo)

    def test_iterador_integral_confirmado_e_preguicoso(self):
        integral = replace(
            self.configuracao,
            modo="integral",
            confirmacao_processamento_integral=True,
        )
        iterador = criar_iterador_combinacoes(
            integral, confirmacao_integral=CONFIRMACAO_INTEGRAL
        )
        self.assertEqual((1, 2, 3, 4, 5, 6), next(iterador))
        self.assertEqual((1, 2, 3, 4, 5, 7), next(iterador))

    def test_exige_configuracao_validada(self):
        with self.assertRaises(TypeError):
            criar_iterador_combinacoes(object())


if __name__ == "__main__":
    unittest.main()
