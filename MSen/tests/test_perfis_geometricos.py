"""Testes dos perfis geométricos e da preservação de valores ausentes."""

from decimal import Decimal, localcontext
from fractions import Fraction
import unittest

from msen.database import AnaliseGeometricaPersistida
from msen.geometria import (
    calcular_area_e_centro_gravidade,
    calcular_extensao_aberta,
    calcular_perimetro_fechado,
)
from msen.services import calcular_perfis_geometricos


DOZE_CASAS = Decimal("0.000000000001")


def decimal_fracao(valor: Fraction) -> Decimal:
    with localcontext() as contexto:
        contexto.prec = 30
        return (Decimal(valor.numerator) / Decimal(valor.denominator)).quantize(
            DOZE_CASAS
        )


def criar_analise(id_resultado: int, dezenas: tuple[int, ...]) -> AnaliseGeometricaPersistida:
    geometria = calcular_area_e_centro_gravidade(dezenas)
    centro = geometria.centro_gravidade
    return AnaliseGeometricaPersistida(
        id_resultado=id_resultado,
        extensao_aberta=calcular_extensao_aberta(dezenas).quantize(DOZE_CASAS),
        perimetro_fechado=calcular_perimetro_fechado(dezenas).quantize(DOZE_CASAS),
        quantidade_regioes=len(geometria.regioes),
        area_total=decimal_fracao(geometria.area_total),
        centro_gravidade_x=None if centro is None else decimal_fracao(centro.x),
        centro_gravidade_y=None if centro is None else decimal_fracao(centro.y),
        versao_calculo=1,
    )


class PerfisGeometricosTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.analises = (
            criar_analise(1, (1, 20, 30, 40, 50, 51)),  # uma região, área 36
            criar_analise(2, (1, 2, 3, 10, 11, 20)),    # duas regiões, área 4,5
            criar_analise(3, (1, 2, 3, 4, 5, 6)),       # sem área ou centro
        )

    def test_cria_os_seis_perfis_na_ordem_do_catalogo(self) -> None:
        perfis = calcular_perfis_geometricos(reversed(self.analises))

        self.assertEqual(
            tuple(item.codigo for item in perfis.parametros),
            (
                "GEO_EXTENSAO_ABERTA", "GEO_PERIMETRO_FECHADO",
                "GEO_QUANTIDADE_REGIOES", "GEO_AREA_TOTAL",
                "GEO_CENTRO_GRAVIDADE_X", "GEO_CENTRO_GRAVIDADE_Y",
            ),
        )
        for parametro in perfis.parametros:
            self.assertEqual(parametro.quantidade_total, 3)

    def test_reconcilia_area_e_regioes_calculadas_pelas_funcoes_reais(self) -> None:
        perfis = calcular_perfis_geometricos(self.analises)

        self.assertEqual(perfis.area_total.perfil.minimo, Decimal("0E-12"))
        self.assertEqual(perfis.area_total.perfil.maximo, Decimal("36.000000000000"))
        self.assertEqual(
            tuple(
                (ponto.valor, ponto.frequencia)
                for ponto in perfis.quantidade_regioes.perfil.distribuicao
            ),
            ((Decimal(0), 1), (Decimal(1), 1), (Decimal(2), 1)),
        )

    def test_centro_ausente_nao_e_substituido_por_zero(self) -> None:
        perfis = calcular_perfis_geometricos(self.analises)

        for centro in (perfis.centro_gravidade_x, perfis.centro_gravidade_y):
            self.assertEqual(centro.quantidade_total, 3)
            self.assertEqual(centro.quantidade_com_valor, 2)
            self.assertEqual(centro.quantidade_ausente, 1)
            self.assertEqual(centro.perfil.quantidade, 2)

        valores_x = tuple(p.valor for p in perfis.centro_gravidade_x.perfil.distribuicao)
        self.assertNotIn(Decimal(0), valores_x)

    def test_zeros_validos_participam_de_area_e_quantidade_de_regioes(self) -> None:
        perfis = calcular_perfis_geometricos(self.analises)

        for parametro in (perfis.area_total, perfis.quantidade_regioes):
            self.assertEqual(parametro.quantidade_com_valor, 3)
            self.assertEqual(parametro.quantidade_ausente, 0)
            self.assertEqual(parametro.perfil.quantidade, 3)

    def test_colecao_vazia_retorna_contagens_zero_sem_inventar_medidas(self) -> None:
        perfis = calcular_perfis_geometricos(())

        for parametro in perfis.parametros:
            self.assertEqual(parametro.quantidade_total, 0)
            self.assertEqual(parametro.quantidade_com_valor, 0)
            self.assertEqual(parametro.quantidade_ausente, 0)
            self.assertIsNone(parametro.perfil)

    def test_rejeita_id_duplicado_e_incoerencias_de_centro(self) -> None:
        duplicada = (self.analises[0], self.analises[0])
        with self.assertRaisesRegex(ValueError, "duas vezes"):
            calcular_perfis_geometricos(duplicada)

        base = self.analises[0]
        centro_parcial = AnaliseGeometricaPersistida(
            base.id_resultado, base.extensao_aberta, base.perimetro_fechado,
            base.quantidade_regioes, base.area_total, base.centro_gravidade_x,
            None, base.versao_calculo,
        )
        with self.assertRaisesRegex(ValueError, "presentes ou ausentes"):
            calcular_perfis_geometricos((centro_parcial,))

        centro_sem_area = AnaliseGeometricaPersistida(
            base.id_resultado, base.extensao_aberta, base.perimetro_fechado,
            0, Decimal(0), base.centro_gravidade_x, base.centro_gravidade_y,
            base.versao_calculo,
        )
        with self.assertRaisesRegex(ValueError, "Área e centro"):
            calcular_perfis_geometricos((centro_sem_area,))

    def test_rejeita_colecao_ou_item_invalido(self) -> None:
        with self.assertRaisesRegex(TypeError, "iteráveis"):
            calcular_perfis_geometricos(None)  # type: ignore[arg-type]
        with self.assertRaisesRegex(TypeError, "persistidas"):
            calcular_perfis_geometricos((object(),))  # type: ignore[arg-type]


if __name__ == "__main__":
    unittest.main()
