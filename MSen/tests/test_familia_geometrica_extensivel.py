"""Testes da família geométrica conectada ao funil extensível."""

from decimal import Decimal
from unittest.mock import patch
import unittest

from msen.screener import (
    ErroFamiliaGeometrica,
    FaixaGeometrica,
    MedidasGeometricasCombinacao,
    calcular_medidas_geometricas,
    criar_familia_geometrica,
    executar_funil_extensivel,
)


class FamiliaGeometricaExtensivelTests(unittest.TestCase):
    def _familia(self, **alteracoes):
        dados = {
            "faixa_extensao": FaixaGeometrica.criar(0, 100),
            "faixa_perimetro": FaixaGeometrica.criar(0, 100),
            "faixa_area": FaixaGeometrica.criar(0, 100),
            "faixa_quantidade_regioes": FaixaGeometrica.criar(0, 10),
            "faixa_centro_x": FaixaGeometrica.criar(0, 9),
            "faixa_centro_y": FaixaGeometrica.criar(0, 5),
            "politica_centro_ausente": "aprovar",
        }
        dados.update(alteracoes)
        return criar_familia_geometrica(**dados)

    def test_figura_controlada_produz_medidas_oficiais(self) -> None:
        medidas = calcular_medidas_geometricas((1, 20, 30, 40, 50, 51))

        self.assertEqual(1, medidas.quantidade_regioes)
        self.assertEqual(Decimal(36), medidas.area_total)
        self.assertEqual(Decimal("4.125"), medidas.centro_gravidade_x)
        self.assertEqual(Decimal("2.5"), medidas.centro_gravidade_y)
        self.assertGreater(medidas.perimetro_fechado, medidas.extensao_aberta)

    def test_uma_combinacao_e_calculada_uma_vez_para_todos_os_filtros(self) -> None:
        familia = self._familia()
        combinacao = (1, 20, 30, 40, 50, 51)
        with patch(
            "msen.screener.familia_geometrica.calcular_medidas_geometricas",
            wraps=calcular_medidas_geometricas,
        ) as calculo:
            relatorio = executar_funil_extensivel((combinacao,), (familia,))

        self.assertEqual(1, relatorio.total_aprovado)
        self.assertEqual(1, calculo.call_count)
        self.assertEqual((1, 1, 1, 1, 1), tuple(
            item.avaliacoes for item in relatorio.familias[0].filtros
        ))

    def test_primeiro_filtro_excludente_interrompe_a_combinacao(self) -> None:
        familia = self._familia(faixa_extensao=FaixaGeometrica.criar(0, 1))
        relatorio = executar_funil_extensivel(
            ((1, 20, 30, 40, 50, 51),), (familia,)
        )
        linhas = relatorio.familias[0].filtros

        self.assertEqual(1, relatorio.total_excluido)
        self.assertEqual((1, 0, 0, 0, 0), tuple(item.avaliacoes for item in linhas))
        self.assertEqual((1, 0, 0, 0, 0), tuple(item.exclusoes for item in linhas))

    def test_centro_ausente_obedece_politica_explicita(self) -> None:
        colinear = (1, 2, 3, 4, 5, 6)
        aprovar = self._familia(politica_centro_ausente="aprovar")
        excluir = self._familia(politica_centro_ausente="excluir")

        decisao_aprovar = aprovar.filtros[-1].avaliador(colinear)
        decisao_excluir = excluir.filtros[-1].avaliador(colinear)
        self.assertTrue(decisao_aprovar.aprovada)
        self.assertFalse(decisao_excluir.aprovada)
        self.assertEqual("CENTRO_AUSENTE_EXCLUIDO", decisao_excluir.motivo)

    def test_limites_de_todas_as_medidas_sao_inclusivos(self) -> None:
        combinacao = (1, 20, 30, 40, 50, 51)
        medidas = calcular_medidas_geometricas(combinacao)
        familia = self._familia(
            faixa_extensao=FaixaGeometrica.criar(
                medidas.extensao_aberta, medidas.extensao_aberta
            ),
            faixa_perimetro=FaixaGeometrica.criar(
                medidas.perimetro_fechado, medidas.perimetro_fechado
            ),
            faixa_area=FaixaGeometrica.criar(36, 36),
            faixa_quantidade_regioes=FaixaGeometrica.criar(1, 1),
            faixa_centro_x=FaixaGeometrica.criar("4.125", "4.125"),
            faixa_centro_y=FaixaGeometrica.criar("2.5", "2.5"),
        )
        relatorio = executar_funil_extensivel((combinacao,), (familia,))
        self.assertEqual(1, relatorio.total_aprovado)

    def test_subtotal_contabiliza_exclusoes_liquidas_por_filtro(self) -> None:
        combinacoes = tuple((indice, 10, 20, 30, 40, 50) for indice in (1, 2, 3, 4, 5, 6))
        retornos = {
            item: MedidasGeometricasCombinacao(
                Decimal(item[0]), Decimal(item[0]), item[0], Decimal(item[0]),
                Decimal(item[0]), Decimal(item[0]),
            )
            for item in combinacoes
        }
        familia = self._familia(
            faixa_extensao=FaixaGeometrica.criar(2, 6),
            faixa_perimetro=FaixaGeometrica.criar(3, 6),
            faixa_area=FaixaGeometrica.criar(4, 6),
            faixa_quantidade_regioes=FaixaGeometrica.criar(5, 6),
            faixa_centro_x=FaixaGeometrica.criar(6, 6),
            faixa_centro_y=FaixaGeometrica.criar(6, 6),
        )
        with patch(
            "msen.screener.familia_geometrica.calcular_medidas_geometricas",
            side_effect=lambda item: retornos[item],
        ):
            relatorio = executar_funil_extensivel(combinacoes, (familia,))

        linhas = relatorio.familias[0].filtros
        self.assertEqual((6, 5, 4, 3, 2), tuple(item.avaliacoes for item in linhas))
        self.assertEqual((1, 1, 1, 1, 1), tuple(item.exclusoes for item in linhas))
        self.assertEqual(5, relatorio.total_excluido)
        self.assertEqual(1, relatorio.total_aprovado)
        self.assertTrue(relatorio.reconciliado)

    def test_politica_ausente_invalida_e_rejeitada(self) -> None:
        with self.assertRaises(ErroFamiliaGeometrica) as contexto:
            self._familia(politica_centro_ausente="ignorar")
        self.assertEqual("POLITICA_CENTRO_INVALIDA", contexto.exception.codigo)


if __name__ == "__main__":
    unittest.main()
