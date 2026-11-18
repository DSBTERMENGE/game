from dataclasses import replace
from pathlib import Path
import unittest

from msen.screener import (
    CONFIRMACAO_INTEGRAL,
    ORIGEM_APLICACAO_INTEGRAL,
    ORIGEM_SELECAO_DEZENAS,
    ORIGEM_TESTE_5000,
    TOTAL_COMBINACOES,
    ErroGeracaoIntegral,
    carregar_configuracao_screener,
)
from msen.services.combinacoes_selecao_dezenas import ErroCombinacoesSelecao
from msen.services.entradas_motor_screener import (
    adaptar_aplicacao_integral,
    adaptar_selecao_dezenas,
    adaptar_teste_5000,
)


RAIZ = Path(__file__).resolve().parents[1]


class EntradasMotorScreenerTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.configuracao = carregar_configuracao_screener(
            RAIZ / "config" / "screener.toml"
        )

    def test_adapta_amostra_reproduzivel_de_5000(self):
        entrada = adaptar_teste_5000(self.configuracao)

        self.assertEqual(ORIGEM_TESTE_5000, entrada.origem)
        self.assertEqual(5_000, entrada.total_combinacoes)
        self.assertEqual(self.configuracao.semente, entrada.contexto["semente"])
        self.assertEqual(5_000, len(tuple(entrada.itens)))

    def test_adapta_universo_integral_sem_materializa_lo(self):
        integral = replace(
            self.configuracao,
            modo="integral",
            confirmacao_processamento_integral=True,
        )
        entrada = adaptar_aplicacao_integral(
            integral, confirmacao_integral=CONFIRMACAO_INTEGRAL
        )

        self.assertEqual(ORIGEM_APLICACAO_INTEGRAL, entrada.origem)
        self.assertEqual(TOTAL_COMBINACOES, entrada.total_combinacoes)
        self.assertEqual((1, 2, 3, 4, 5, 6), next(iter(entrada.itens)))

    def test_preserva_trava_da_aplicacao_integral(self):
        integral = replace(
            self.configuracao,
            modo="integral",
            confirmacao_processamento_integral=True,
        )

        with self.assertRaises(ErroGeracaoIntegral):
            adaptar_aplicacao_integral(integral)

    def test_adapta_quantidade_variavel_da_selecao(self):
        entrada = adaptar_selecao_dezenas((8, 1, 7, 2, 6, 3, 5))

        self.assertEqual(ORIGEM_SELECAO_DEZENAS, entrada.origem)
        self.assertEqual(7, entrada.total_combinacoes)
        self.assertEqual(7, entrada.contexto["quantidade_dezenas"])
        self.assertEqual((1, 2, 3, 5, 6, 7), next(iter(entrada.itens)))

    def test_selecao_exige_ao_menos_seis_dezenas(self):
        with self.assertRaises(ErroCombinacoesSelecao) as contexto:
            adaptar_selecao_dezenas(range(1, 6))

        self.assertEqual("DEZENAS_INSUFICIENTES", contexto.exception.codigo)


if __name__ == "__main__":
    unittest.main()
