"""Testes da análise de assinaturas diagonais."""

import unittest

from msen.padroes.diagonais import (
    AssinaturaDiagonal,
    analisar_assinaturas_diagonais,
)


class AssinaturasDiagonaisTestCase(unittest.TestCase):
    def test_constroi_arrays_direita_e_esquerda_da_referencia(self) -> None:
        analise = analisar_assinaturas_diagonais((1, 4, 10, 20, 30, 60))
        referencia = analise.referencias[0]

        self.assertEqual(2, referencia.posicao)
        self.assertEqual(4, referencia.dezena)
        self.assertEqual((4, 13, 22, 31), referencia.diagonal_direita)
        self.assertEqual((4, 15, 26, 37, 48, 59), referencia.diagonal_esquerda)
        self.assertTrue(referencia.elegivel)

    def test_identifica_2d2e_sem_considerar_posicao_relativa(self) -> None:
        analise = analisar_assinaturas_diagonais((15, 17, 26, 35, 37, 60))
        referencia = analise.referencias[1]

        self.assertEqual(26, referencia.dezena)
        self.assertEqual(AssinaturaDiagonal(2, 2), referencia.assinatura)
        self.assertIn(AssinaturaDiagonal(2, 2), analise.assinaturas)

    def test_identifica_0d0e_em_referencia_longa(self) -> None:
        analise = analisar_assinaturas_diagonais((2, 14, 26, 39, 51, 60))
        referencia = analise.referencias[1]

        self.assertEqual(26, referencia.dezena)
        self.assertEqual(AssinaturaDiagonal(0, 0), referencia.assinatura)

    def test_seis_dezenas_na_esquerda_produzem_0d5e(self) -> None:
        analise = analisar_assinaturas_diagonais((4, 15, 26, 37, 48, 59))

        self.assertIn(AssinaturaDiagonal(0, 5), analise.assinaturas)
        self.assertTrue(
            all(
                referencia.assinatura == AssinaturaDiagonal(0, 5)
                for referencia in analise.referencias
            )
        )

    def test_ignora_referencias_com_alguma_diagonal_curta(self) -> None:
        analise = analisar_assinaturas_diagonais((1, 2, 3, 8, 9, 10))

        self.assertTrue(analise.sem_referencia_longa)
        self.assertEqual((), analise.assinaturas)
        self.assertTrue(all(not item.elegivel for item in analise.referencias))

    def test_consolida_assinatura_repetida_uma_unica_vez(self) -> None:
        analise = analisar_assinaturas_diagonais((4, 15, 26, 37, 48, 59))

        self.assertEqual((AssinaturaDiagonal(0, 5),), analise.assinaturas)

    def test_codigo_da_assinatura_segue_notacao_curta(self) -> None:
        self.assertEqual("2D2E", AssinaturaDiagonal(2, 2).codigo)

    def test_rejeita_assinatura_impossivel(self) -> None:
        with self.assertRaises(ValueError):
            AssinaturaDiagonal(2, 4)

    def test_ordem_da_entrada_nao_altera_analise(self) -> None:
        primeira = analisar_assinaturas_diagonais((15, 17, 26, 35, 37, 60))
        segunda = analisar_assinaturas_diagonais((60, 35, 15, 37, 17, 26))

        self.assertEqual(primeira, segunda)

    def test_rejeita_entrada_invalida_pelo_contrato_compartilhado(self) -> None:
        with self.assertRaises(ValueError):
            analisar_assinaturas_diagonais((4, 15, 26, 37, 48, 48))


if __name__ == "__main__":
    unittest.main()
