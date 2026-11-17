import unittest

from msen.validacao import criar_registro_criterios_producao


class TestMotorValidacaoCategorico(unittest.TestCase):
    def test_catalogo_possui_um_criterio_categorico_executavel(self):
        categoricos = tuple(
            item
            for item in criar_registro_criterios_producao().listar()
            if item.tipo_resultado == "CATEGORICO"
        )
        self.assertEqual(("PAD_PG_004",), tuple(item.codigo for item in categoricos))
        self.assertTrue(all(callable(item.funcao) for item in categoricos))


if __name__ == "__main__":
    unittest.main()
