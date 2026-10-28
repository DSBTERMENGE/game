import unittest

from msen.modelos import EstadoClassificacaoPadrao
from msen.padroes import (
    CODIGO_DUAS_SEQUENCIAIS,
    CODIGO_GRUPO_SEQUENCIAIS,
    CODIGO_MAIS_DE_TRES_SEQUENCIAIS,
    CODIGO_TRES_SEQUENCIAIS,
    classificar_grupo_dezenas_sequenciais,
    detectar_duas_dezenas_sequenciais,
    detectar_mais_de_tres_dezenas_sequenciais,
    detectar_tres_dezenas_sequenciais,
)


class ClassificacaoGrupoSequenciaisTestCase(unittest.TestCase):
    def test_classifica_os_quatro_estados_aprovados(self):
        casos = (
            ((1, 3, 5, 7, 9, 11), None, 1),
            ((10, 25, 26, 38, 50, 58), CODIGO_DUAS_SEQUENCIAIS, 2),
            ((10, 25, 26, 27, 50, 58), CODIGO_TRES_SEQUENCIAIS, 3),
            ((1, 2, 3, 4, 20, 40), CODIGO_MAIS_DE_TRES_SEQUENCIAIS, 4),
            ((1, 2, 3, 4, 5, 40), CODIGO_MAIS_DE_TRES_SEQUENCIAIS, 5),
            ((1, 2, 3, 4, 5, 6), CODIGO_MAIS_DE_TRES_SEQUENCIAIS, 6),
        )
        for dezenas, codigo, tamanho in casos:
            with self.subTest(dezenas=dezenas):
                resultado = classificar_grupo_dezenas_sequenciais(dezenas)
                self.assertEqual(CODIGO_GRUPO_SEQUENCIAIS, resultado.grupo_cod)
                self.assertEqual(codigo, resultado.padrao_cod)
                self.assertEqual(tamanho, resultado.evidencia.maior_tamanho)
                estado = (
                    EstadoClassificacaoPadrao.SEM_CORRESPONDENCIA
                    if codigo is None
                    else EstadoClassificacaoPadrao.PADRAO_IDENTIFICADO
                )
                self.assertEqual(estado, resultado.estado)

    def test_nao_une_sessenta_com_um(self):
        resultado = classificar_grupo_dezenas_sequenciais((58, 59, 60, 1, 2, 3))
        self.assertEqual(CODIGO_TRES_SEQUENCIAIS, resultado.padrao_cod)
        self.assertEqual(3, resultado.evidencia.maior_tamanho)
        self.assertEqual(
            ((1, 2, 3), (58, 59, 60)),
            resultado.evidencia.maiores_blocos,
        )

    def test_maior_bloco_define_classe_sem_sobreposicao(self):
        resultado = classificar_grupo_dezenas_sequenciais((1, 2, 10, 11, 12, 50))
        self.assertEqual(CODIGO_TRES_SEQUENCIAIS, resultado.padrao_cod)
        self.assertEqual(((10, 11, 12),), resultado.evidencia.maiores_blocos)

    def test_ordem_da_entrada_nao_muda_resultado_ou_evidencia(self):
        ordenada = classificar_grupo_dezenas_sequenciais((10, 25, 26, 27, 50, 58))
        fora_de_ordem = classificar_grupo_dezenas_sequenciais((58, 27, 10, 50, 26, 25))
        self.assertEqual(ordenada, fora_de_ordem)

    def test_classificador_e_detectores_usam_a_mesma_regra_central(self):
        casos = (
            (1, 3, 5, 7, 9, 11),
            (10, 25, 26, 38, 50, 58),
            (10, 25, 26, 27, 50, 58),
            (10, 25, 26, 27, 28, 58),
        )
        detectores = {
            CODIGO_DUAS_SEQUENCIAIS: detectar_duas_dezenas_sequenciais,
            CODIGO_TRES_SEQUENCIAIS: detectar_tres_dezenas_sequenciais,
            CODIGO_MAIS_DE_TRES_SEQUENCIAIS: detectar_mais_de_tres_dezenas_sequenciais,
        }
        for dezenas in casos:
            with self.subTest(dezenas=dezenas):
                resultado = classificar_grupo_dezenas_sequenciais(dezenas)
                ativos = tuple(codigo for codigo, detector in detectores.items() if detector(dezenas))
                esperado = () if resultado.padrao_cod is None else (resultado.padrao_cod,)
                self.assertEqual(esperado, ativos)

    def test_rejeita_entradas_invalidas_pela_mesma_validacao_dos_detectores(self):
        casos = (
            ((1, 2, 3), ValueError),
            ((1, 2, 3, 4, 5, 61), ValueError),
            ((1, 2, 3, 4, 5, 5), ValueError),
            ((1, 2, 3, 4, 5, True), TypeError),
        )
        for dezenas, erro in casos:
            with self.subTest(dezenas=dezenas):
                with self.assertRaises(erro):
                    classificar_grupo_dezenas_sequenciais(dezenas)


if __name__ == "__main__":
    unittest.main()
