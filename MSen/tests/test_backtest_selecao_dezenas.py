from decimal import Decimal

import unittest

from msen.services.backtest_selecao_dezenas import (
    PontoBacktest,
    resumir_pontos,
)


class BacktestSelecaoDezenasTest(unittest.TestCase):
  def test_resumo_backtest_mantem_classes_exclusivas(self):
    pontos = (
        PontoBacktest(500, 10, 0),
        PontoBacktest(501, 14, 2),
        PontoBacktest(502, 18, 4),
        PontoBacktest(503, 22, 6),
    )

    resumo = resumir_pontos(pontos)

    self.assertEqual(resumo.testes_efetuados, 4)
    self.assertEqual([item.quantidade for item in resumo.classes], [1, 0, 1, 0, 1, 0, 1])
    self.assertEqual(sum(item.quantidade for item in resumo.classes), 4)
    self.assertEqual(resumo.minimo_dezenas, 10)
    self.assertEqual(resumo.maximo_dezenas, 22)
    self.assertEqual(resumo.media_dezenas, Decimal("16.000000"))
    self.assertEqual(resumo.media_acertos, Decimal("3.000000"))
    self.assertEqual(resumo.concursos_premiados, 2)
    self.assertEqual(resumo.percentual_premiados, Decimal("50.000000"))


  def test_resumo_backtest_rejeita_lista_vazia(self):
    with self.assertRaisesRegex(ValueError, "ao menos um"):
        resumir_pontos(())


  def test_resumo_backtest_rejeita_acerto_fora_de_zero_a_seis(self):
    with self.assertRaisesRegex(ValueError, "entre 0 e 6"):
        resumir_pontos((PontoBacktest(500, 10, 7),))
