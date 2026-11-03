from io import StringIO
import unittest

from msen.services import (
    ErroCombinacoesSelecao,
    calcular_previa_combinacoes,
    exportar_combinacoes_csv,
    gerar_combinacoes_seis_dezenas,
)


class CombinacoesSelecaoDezenasTest(unittest.TestCase):
    def test_calcula_c_n_6_sem_materializar(self) -> None:
        previa = calcular_previa_combinacoes(range(1, 61))
        self.assertEqual(previa.quantidade_combinacoes, 50_063_860)
        self.assertTrue(previa.volume_elevado)
        self.assertTrue(previa.exige_confirmacao)

    def test_gera_sem_repeticao_em_ordem_deterministica(self) -> None:
        jogos = tuple(gerar_combinacoes_seis_dezenas((8, 1, 7, 2, 6, 3, 5)))
        self.assertEqual(len(jogos), 7)
        self.assertEqual(jogos[0], (1, 2, 3, 5, 6, 7))
        self.assertEqual(jogos[-1], (2, 3, 5, 6, 7, 8))
        self.assertEqual(len(jogos), len(set(jogos)))

    def test_rejeita_dezenas_repetidas(self) -> None:
        with self.assertRaisesRegex(ValueError, "não podem se repetir"):
            calcular_previa_combinacoes((1, 2, 3, 4, 5, 5))

    def test_exportacao_exige_autorizacao(self) -> None:
        with self.assertRaises(ErroCombinacoesSelecao) as contexto:
            exportar_combinacoes_csv(range(1, 7), StringIO())
        self.assertEqual(contexto.exception.codigo, "OPERACAO_NAO_AUTORIZADA")

    def test_exporta_csv_autorizado(self) -> None:
        destino = StringIO()
        total = exportar_combinacoes_csv(
            range(1, 8), destino, autorizar_exportacao=True
        )
        self.assertEqual(total, 7)
        linhas = destino.getvalue().splitlines()
        self.assertEqual(len(linhas), 8)
        self.assertEqual(linhas[1], "1,1,2,3,4,5,6")

    def test_volume_elevado_exige_confirmacao_adicional(self) -> None:
        with self.assertRaises(ErroCombinacoesSelecao) as contexto:
            exportar_combinacoes_csv(
                range(1, 21), StringIO(), autorizar_exportacao=True
            )
        self.assertEqual(
            contexto.exception.codigo, "VOLUME_ELEVADO_NAO_CONFIRMADO"
        )


if __name__ == "__main__":
    unittest.main()
