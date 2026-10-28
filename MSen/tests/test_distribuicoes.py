"""Testes do histograma e da curva normal de referência."""

from decimal import Decimal
import unittest

from msen.services import calcular_perfil_estatistico, construir_distribuicao_visual


class DistribuicoesTestCase(unittest.TestCase):
    def test_histograma_reconcilia_frequencias_e_percentuais(self) -> None:
        perfil = calcular_perfil_estatistico((2, 4, 4, 4, 5, 5, 7, 9))
        visual = construir_distribuicao_visual(perfil, quantidade_classes=4)

        self.assertEqual(len(visual.classes), 4)
        self.assertEqual(sum(item.frequencia for item in visual.classes), 8)
        self.assertEqual(
            sum((item.percentual for item in visual.classes), Decimal(0)),
            Decimal("100.000000"),
        )
        self.assertTrue(visual.curva_normal_disponivel)
        self.assertEqual(len(visual.curva_normal), 4)
        self.assertTrue(all(item.densidade > 0 for item in visual.curva_normal))

    def test_serie_constante_tem_uma_classe_e_normal_indisponivel(self) -> None:
        perfil = calcular_perfil_estatistico((3, 3, 3))
        visual = construir_distribuicao_visual(perfil, quantidade_classes=10)

        self.assertEqual(len(visual.classes), 1)
        self.assertEqual(visual.classes[0].frequencia, 3)
        self.assertEqual(visual.classes[0].percentual, Decimal("100.000000"))
        self.assertFalse(visual.curva_normal_disponivel)
        self.assertEqual(visual.curva_normal, ())

    def test_rejeita_quantidade_de_classes_e_perfil_invalidos(self) -> None:
        perfil = calcular_perfil_estatistico((1, 2))
        for classes in (0, 51, True):
            with self.subTest(classes=classes):
                with self.assertRaises(ValueError):
                    construir_distribuicao_visual(perfil, quantidade_classes=classes)
        with self.assertRaises(TypeError):
            construir_distribuicao_visual(object(), quantidade_classes=10)  # type: ignore[arg-type]


if __name__ == "__main__":
    unittest.main()
