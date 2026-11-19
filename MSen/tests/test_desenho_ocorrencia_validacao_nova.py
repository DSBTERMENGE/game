import unittest

from msen.padroes import (
    calcular_categorias_diagonais,
    detectar_dezenas_em_duas_linhas,
    detectar_dezenas_em_uma_linha_e_uma_coluna,
    detectar_tres_dezenas_na_mesma_coluna,
    detectar_tres_dezenas_na_mesma_linha,
    detectar_tres_dezenas_sequenciais,
)
from msen.services import construir_desenho_ocorrencia_validacao


class DesenhoOcorrenciaValidacaoNovaTestCase(unittest.TestCase):
    def test_marca_sempre_as_seis_dezenas_ordenadas(self):
        desenho = construir_desenho_ocorrencia_validacao(
            detectar_tres_dezenas_sequenciais, (41, 5, 4, 52, 30, 33)
        )
        self.assertEqual((4, 5, 30, 33, 41, 52), desenho.dezenas_marcadas)
        self.assertTrue(all(item.tipo == "sequencial" for item in desenho.segmentos))

    def test_linha_e_coluna_cruzam_centros_de_borda_a_borda(self):
        combinacao = (2, 5, 7, 9, 29, 49)
        desenho = construir_desenho_ocorrencia_validacao(
            detectar_dezenas_em_uma_linha_e_uma_coluna, combinacao
        )
        self.assertEqual(
            [("horizontal", 0.0, 0.5, 10.0, 0.5),
             ("vertical", 8.5, 0.0, 8.5, 6.0)],
            [(s.tipo, s.x1, s.y1, s.x2, s.y2) for s in desenho.segmentos],
        )

    def test_duas_linhas_desenha_exatamente_duas_horizontais(self):
        desenho = construir_desenho_ocorrencia_validacao(
            detectar_dezenas_em_duas_linhas, (1, 2, 3, 14, 15, 16)
        )
        self.assertEqual([0.5, 1.5], [item.y1 for item in desenho.segmentos])

    def test_mesma_linha_e_coluna_desenham_eixos_correspondentes(self):
        horizontal = construir_desenho_ocorrencia_validacao(
            detectar_tres_dezenas_na_mesma_linha, (1, 2, 3, 14, 25, 36)
        )
        vertical = construir_desenho_ocorrencia_validacao(
            detectar_tres_dezenas_na_mesma_coluna, (1, 11, 21, 34, 45, 56)
        )
        self.assertEqual(["horizontal"], [item.tipo for item in horizontal.segmentos])
        self.assertEqual(["vertical"], [item.tipo for item in vertical.segmentos])

    def test_diagonal_entrega_segmentos_recortados_no_painel(self):
        desenho = construir_desenho_ocorrencia_validacao(
            calcular_categorias_diagonais, (4, 15, 26, 37, 48, 59)
        )
        self.assertTrue(desenho.segmentos)
        for item in desenho.segmentos:
            self.assertTrue(0 <= item.x1 <= 10 and 0 <= item.x2 <= 10)
            self.assertTrue(0 <= item.y1 <= 6 and 0 <= item.y2 <= 6)

    def test_contrato_serializado_nao_expoe_codigo_nem_funcao(self):
        desenho = construir_desenho_ocorrencia_validacao(
            detectar_dezenas_em_duas_linhas, (1, 2, 3, 14, 15, 16)
        ).como_dict()
        texto = repr(desenho).lower()
        self.assertNotIn("codigo", texto)
        self.assertNotIn("funcao", texto)


if __name__ == "__main__":
    unittest.main()
