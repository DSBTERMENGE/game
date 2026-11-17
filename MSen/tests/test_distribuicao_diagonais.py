"""Testes da distribuição histórica das categorias diagonais."""

from datetime import date
from decimal import Decimal
import unittest

from msen.modelos import ResultadoEntrada
from msen.padroes import (
    CODIGOS_CATEGORIAS_DIAGONAIS,
    calcular_distribuicao_categorias_diagonais,
)


def _resultado(numero: int, dezenas: tuple[int, ...]) -> ResultadoEntrada:
    return ResultadoEntrada(date(2026, 1, numero), numero, *dezenas)


class DistribuicaoDiagonaisTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.resultados = (
            _resultado(1, (4, 15, 26, 37, 48, 59)),
            _resultado(2, (1, 2, 3, 8, 9, 10)),
            _resultado(3, (1, 7, 25, 29, 44, 49)),
        )

    def test_cria_tabela_completa_no_mesmo_denominador(self) -> None:
        distribuicao = calcular_distribuicao_categorias_diagonais(self.resultados)

        self.assertEqual(3, distribuicao.total_resultados)
        self.assertEqual(
            CODIGOS_CATEGORIAS_DIAGONAIS,
            tuple(item.codigo for item in distribuicao.incidencias),
        )
        self.assertTrue(
            all(item.total_resultados == 3 for item in distribuicao.incidencias)
        )

    def test_conta_assinaturas_nao_exclusivas_uma_vez_por_resultado(self) -> None:
        distribuicao = calcular_distribuicao_categorias_diagonais(self.resultados)

        for codigo in ("0D0E", "0D1E", "1D0E", "1D1E", "0D5E"):
            with self.subTest(codigo=codigo):
                incidencia = distribuicao.obter(codigo)
                self.assertEqual(1, incidencia.ocorrencias)
                self.assertEqual(Decimal("33.333333"), incidencia.percentual)
        self.assertEqual(0, distribuicao.obter("5D0E").ocorrencias)
        self.assertEqual(Decimal("0.000000"), distribuicao.obter("5D0E").percentual)

    def test_sem_referencia_longa_e_categoria_exclusiva_do_resultado_vazio(self) -> None:
        distribuicao = calcular_distribuicao_categorias_diagonais(self.resultados)
        incidencia = distribuicao.obter("SEM_REFERENCIA_LONGA")

        self.assertEqual(1, incidencia.ocorrencias)
        self.assertEqual(Decimal("33.333333"), incidencia.percentual)

    def test_ordem_dos_resultados_nao_altera_distribuicao(self) -> None:
        primeira = calcular_distribuicao_categorias_diagonais(self.resultados)
        segunda = calcular_distribuicao_categorias_diagonais(
            tuple(reversed(self.resultados))
        )

        self.assertEqual(primeira, segunda)

    def test_rejeita_serie_vazia_tipo_invalido_e_concurso_repetido(self) -> None:
        with self.assertRaises(ValueError):
            calcular_distribuicao_categorias_diagonais(())
        with self.assertRaises(TypeError):
            calcular_distribuicao_categorias_diagonais((object(),))  # type: ignore[arg-type]
        with self.assertRaises(ValueError):
            calcular_distribuicao_categorias_diagonais(
                (self.resultados[0], self.resultados[0])
            )

    def test_codigo_desconhecido_nao_e_inventado(self) -> None:
        distribuicao = calcular_distribuicao_categorias_diagonais(self.resultados)

        with self.assertRaises(KeyError):
            distribuicao.obter("9D9E")


if __name__ == "__main__":
    unittest.main()
