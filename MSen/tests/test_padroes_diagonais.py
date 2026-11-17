"""Testes da análise de assinaturas diagonais."""

from dataclasses import FrozenInstanceError
import unittest

from msen.padroes.diagonais import (
    AssinaturaDiagonal,
    analisar_assinaturas_diagonais,
)


class AssinaturasDiagonaisTestCase(unittest.TestCase):
    def test_analisa_exatamente_as_quatro_referencias_intermediarias(self) -> None:
        analise = analisar_assinaturas_diagonais((1, 4, 10, 20, 30, 60))

        self.assertEqual((2, 3, 4, 5), tuple(r.posicao for r in analise.referencias))
        self.assertEqual((4, 10, 20, 30), tuple(r.dezena for r in analise.referencias))

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

    def test_lacunas_de_18_continuam_na_diagonal_direita(self) -> None:
        analise = analisar_assinaturas_diagonais((1, 17, 20, 35, 53, 60))
        referencia = analise.referencias[2]

        self.assertEqual(35, referencia.dezena)
        self.assertEqual(AssinaturaDiagonal(2, 0), referencia.assinatura)

    def test_lacunas_de_22_continuam_na_diagonal_esquerda(self) -> None:
        analise = analisar_assinaturas_diagonais((1, 4, 26, 48, 50, 60))
        referencia = analise.referencias[1]

        self.assertEqual(26, referencia.dezena)
        self.assertEqual(AssinaturaDiagonal(0, 2), referencia.assinatura)

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

    def test_consolida_multiplas_assinaturas_em_ordem_estavel(self) -> None:
        analise = analisar_assinaturas_diagonais((1, 7, 25, 29, 44, 49))

        self.assertEqual(
            ("0D0E", "0D1E", "1D0E", "1D1E"),
            tuple(item.codigo for item in analise.assinaturas),
        )
        self.assertEqual(
            ("1D1E", "1D0E", "0D1E", "0D0E"),
            tuple(
                referencia.assinatura.codigo
                for referencia in analise.referencias
                if referencia.assinatura is not None
            ),
        )

    def test_limite_do_volante_nao_conecta_extremos_da_mesma_linha(self) -> None:
        analise = analisar_assinaturas_diagonais((1, 10, 19, 28, 37, 55))
        referencia = analise.referencias[0]

        self.assertEqual(10, referencia.dezena)
        self.assertEqual((10, 19, 28, 37, 46, 55), referencia.diagonal_direita)
        self.assertEqual((10,), referencia.diagonal_esquerda)
        self.assertFalse(referencia.elegivel)

    def test_retorno_e_objetos_internos_sao_imutaveis(self) -> None:
        analise = analisar_assinaturas_diagonais((15, 17, 26, 35, 37, 60))

        with self.assertRaises(FrozenInstanceError):
            analise.dezenas_ordenadas = (1, 2, 3, 4, 5, 6)  # type: ignore[misc]
        with self.assertRaises(FrozenInstanceError):
            analise.assinaturas[0].direita = 5  # type: ignore[misc]

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

    def test_rejeita_quantidade_faixa_e_tipos_invalidos(self) -> None:
        casos = (
            ((1, 2, 3, 4, 5), ValueError),
            ((1, 2, 3, 4, 5, 6, 7), ValueError),
            ((0, 2, 3, 4, 5, 6), ValueError),
            ((1, 2, 3, 4, 5, 61), ValueError),
            ((1, 2, 3, 4, 5, True), TypeError),
            ((1, 2, 3, 4, 5, 6.0), TypeError),
            ("010203040506", TypeError),
            ({1, 2, 3, 4, 5, 6}, TypeError),
        )
        for entrada, erro in casos:
            with self.subTest(entrada=entrada, erro=erro):
                with self.assertRaises(erro):
                    analisar_assinaturas_diagonais(entrada)  # type: ignore[arg-type]


if __name__ == "__main__":
    unittest.main()
