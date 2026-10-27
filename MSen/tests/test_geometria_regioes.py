"""Testes de interseções, subdivisão e regiões geométricas."""

from fractions import Fraction
import inspect
import unittest

from msen.geometria import (
    PontoGeometrico,
    SegmentoGeometrico,
    construir_percurso_fechado,
    dividir_segmentos,
    encontrar_intersecoes,
    identificar_regioes_fechadas,
)


def ponto(x: int | Fraction, y: int | Fraction) -> PontoGeometrico:
    return PontoGeometrico(Fraction(x), Fraction(y))


class GeometriaRegioesTestCase(unittest.TestCase):
    def test_encontra_cruzamento_exato_do_exemplo_b(self) -> None:
        segmentos = construir_percurso_fechado([1, 2, 3, 10, 11, 20])

        self.assertEqual(
            encontrar_intersecoes(segmentos),
            (ponto(Fraction(9, 2), Fraction(1, 2)),),
        )

    def test_omite_juncoes_normais_entre_segmentos_consecutivos(self) -> None:
        segmentos = construir_percurso_fechado([1, 20, 30, 40, 50, 51])

        self.assertEqual(encontrar_intersecoes(segmentos), ())

    def test_divide_as_duas_diagonais_no_cruzamento(self) -> None:
        segmentos = construir_percurso_fechado([1, 2, 3, 10, 11, 20])
        atomicos = dividir_segmentos(segmentos)
        cruzamento = ponto(Fraction(9, 2), Fraction(1, 2))

        incidentes = [
            aresta
            for aresta in atomicos
            if cruzamento in (aresta.inicio, aresta.fim)
        ]
        self.assertEqual(len(incidentes), 4)

    def test_exemplo_a_forma_uma_regiao(self) -> None:
        regioes = identificar_regioes_fechadas(
            construir_percurso_fechado([1, 20, 30, 40, 50, 51])
        )

        self.assertEqual(len(regioes), 1)

    def test_exemplo_b_forma_duas_regioes(self) -> None:
        regioes = identificar_regioes_fechadas(
            construir_percurso_fechado([1, 2, 3, 10, 11, 20])
        )

        self.assertEqual(len(regioes), 2)
        self.assertTrue(all(len(regiao.vertices) == 3 for regiao in regioes))

    def test_varios_cruzamentos_formam_tres_regioes(self) -> None:
        segmentos = construir_percurso_fechado([1, 2, 3, 11, 12, 22])

        self.assertEqual(
            encontrar_intersecoes(segmentos),
            (ponto(Fraction(2, 5), Fraction(4, 5)), ponto(Fraction(1, 2), 1)),
        )
        regioes = identificar_regioes_fechadas(segmentos)
        self.assertEqual(len(regioes), 3)
        self.assertTrue(all(len(regiao.vertices) == 3 for regiao in regioes))

    def test_figura_colinear_nao_forma_regiao(self) -> None:
        regioes = identificar_regioes_fechadas(
            construir_percurso_fechado([1, 2, 3, 4, 5, 6])
        )

        self.assertEqual(regioes, ())

    def test_normaliza_sobreposicao_sem_duplicar_arestas(self) -> None:
        segmentos = (
            SegmentoGeometrico(ponto(0, 0), ponto(4, 0)),
            SegmentoGeometrico(ponto(2, 0), ponto(6, 0)),
        )

        atomicos = dividir_segmentos(segmentos)

        self.assertEqual(len(atomicos), 3)
        self.assertEqual(
            {(aresta.inicio, aresta.fim) for aresta in atomicos},
            {
                (ponto(0, 0), ponto(2, 0)),
                (ponto(2, 0), ponto(4, 0)),
                (ponto(4, 0), ponto(6, 0)),
            },
        )

    def test_tres_segmentos_no_mesmo_ponto_criam_um_unico_no(self) -> None:
        segmentos = (
            SegmentoGeometrico(ponto(-1, 0), ponto(1, 0)),
            SegmentoGeometrico(ponto(0, -1), ponto(0, 1)),
            SegmentoGeometrico(ponto(-1, -1), ponto(1, 1)),
        )

        self.assertEqual(encontrar_intersecoes(segmentos), (ponto(0, 0),))
        incidentes = [
            aresta
            for aresta in dividir_segmentos(segmentos)
            if ponto(0, 0) in (aresta.inicio, aresta.fim)
        ]
        self.assertEqual(len(incidentes), 6)

    def test_contato_com_vertice_nao_adjacente_divide_o_segmento(self) -> None:
        segmentos = (
            SegmentoGeometrico(ponto(0, 0), ponto(4, 0)),
            SegmentoGeometrico(ponto(2, 0), ponto(2, 2)),
        )

        self.assertEqual(encontrar_intersecoes(segmentos), (ponto(2, 0),))
        self.assertEqual(len(dividir_segmentos(segmentos)), 3)

    def test_rejeita_segmento_nulo_e_itens_invalidos(self) -> None:
        with self.assertRaisesRegex(ValueError, "comprimento zero"):
            dividir_segmentos((SegmentoGeometrico(ponto(0, 0), ponto(0, 0)),))
        with self.assertRaises(TypeError):
            dividir_segmentos(("segmento",))

    def test_funcoes_publicas_possuem_docstrings_em_portugues(self) -> None:
        for funcao in (encontrar_intersecoes, dividir_segmentos, identificar_regioes_fechadas):
            with self.subTest(funcao=funcao.__name__):
                documentacao = inspect.getdoc(funcao)
                self.assertTrue(documentacao)
                self.assertIn("segmentos", documentacao.casefold())


if __name__ == "__main__":
    unittest.main()
