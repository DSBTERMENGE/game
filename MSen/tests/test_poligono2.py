import unittest

from msen.geometria import calcular_poligono2, encontrar_intersecoes, SegmentoGeometrico


class Poligono2Test(unittest.TestCase):
    def test_usa_as_seis_dezenas_em_circuito_simples(self):
        resultado = calcular_poligono2((41, 5, 4, 52, 30, 33))

        self.assertIsNotNone(resultado)
        self.assertEqual({4, 5, 30, 33, 41, 52}, set(resultado.dezenas))
        self.assertEqual(6, len(resultado.vertices))
        segmentos = tuple(
            SegmentoGeometrico(a, b)
            for a, b in zip(resultado.vertices, resultado.vertices[1:] + resultado.vertices[:1])
        )
        self.assertEqual((), encontrar_intersecoes(segmentos))
        self.assertGreater(resultado.area, 0)

    def test_escolhe_maior_area_entre_todos_os_circuitos_validos(self):
        resultado = calcular_poligono2((9, 39, 37, 49, 43, 41))
        self.assertEqual(60, resultado.circuitos_avaliados)
        self.assertGreater(resultado.circuitos_validos, 0)
        self.assertEqual(resultado.area, 15)

    def test_resultado_independe_da_ordem_de_entrada(self):
        primeira = calcular_poligono2((19, 40, 7, 13, 22, 47))
        segunda = calcular_poligono2((47, 22, 13, 7, 40, 19))
        self.assertEqual(primeira, segunda)

    def test_desempate_e_orientacao_sao_deterministicos(self):
        resultado = calcular_poligono2((1, 2, 3, 4, 5, 11))
        self.assertEqual(1, resultado.dezenas[0])
        area_assinada = sum(
            a.x * b.y - b.x * a.y
            for a, b in zip(resultado.vertices, resultado.vertices[1:] + resultado.vertices[:1])
        )
        self.assertGreater(area_assinada, 0)

    def test_seis_pontos_colineares_nao_formam_poligono(self):
        self.assertIsNone(calcular_poligono2((1, 2, 3, 4, 5, 6)))


if __name__ == "__main__":
    unittest.main()
