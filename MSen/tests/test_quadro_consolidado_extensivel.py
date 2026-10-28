"""Testes do quadro contábil consolidado das três famílias."""

from dataclasses import replace
from decimal import Decimal
import json
import unittest

from msen.screener import (
    DecisaoFiltro,
    DefinicaoFamilia,
    DefinicaoFiltro,
    ErroQuadroConsolidado,
    criar_quadro_consolidado,
    executar_funil_extensivel,
    serializar_quadro_consolidado,
)


def avaliador(codigo: str, excluidas: set[int]):
    def interno(combinacao):
        excluir = combinacao[0] in excluidas
        return DecisaoFiltro.criar(
            codigo_filtro=codigo,
            aprovada=not excluir,
            motivo="FORA" if excluir else "DENTRO",
            evidencias={"primeira": combinacao[0]},
        )
    return interno


def plano():
    return (
        DefinicaoFamilia(
            "ESTATISTICA", "Valores estatísticos", 1,
            (
                DefinicaoFiltro("EST_1", "Estatístico 1", 1, avaliador("EST_1", {1})),
                DefinicaoFiltro("EST_2", "Estatístico 2", 2, avaliador("EST_2", {2})),
            ),
        ),
        DefinicaoFamilia(
            "GEOMETRIA", "Análise geométrica", 2,
            (DefinicaoFiltro("GEO_1", "Geométrico", 1, avaliador("GEO_1", {3})),),
        ),
        DefinicaoFamilia(
            "PADROES", "Padrões históricos", 3,
            (DefinicaoFiltro("PAD_1", "Grupo", 1, avaliador("PAD_1", {4, 5})),),
        ),
    )


class QuadroConsolidadoExtensivelTests(unittest.TestCase):
    def setUp(self) -> None:
        self.combinacoes = tuple((i, 10, 20, 30, 40, 50) for i in range(1, 9))
        self.relatorio = executar_funil_extensivel(self.combinacoes, plano())

    def test_consolida_as_tres_familias_e_fecha_contabilidade(self) -> None:
        quadro = criar_quadro_consolidado(
            self.relatorio, tipo_escopo="amostra", total_universo=50_063_860
        )

        self.assertEqual(8, quadro.total_analisado)
        self.assertEqual(5, quadro.total_excluido)
        self.assertEqual(3, quadro.total_aprovado)
        self.assertEqual(Decimal("62.500000"), quadro.percentual_excluido)
        self.assertEqual(Decimal("37.500000"), quadro.percentual_aprovado)
        self.assertEqual(
            ((8, 2, 6), (6, 1, 5), (5, 2, 3)),
            tuple((item.entrada, item.exclusoes, item.saldo) for item in quadro.familias),
        )
        self.assertTrue(quadro.reconciliado)

    def test_linhas_mostram_entrada_avaliacoes_percentuais_e_saldo(self) -> None:
        quadro = criar_quadro_consolidado(self.relatorio, tipo_escopo="amostra")
        primeiro, segundo = quadro.familias[0].filtros

        self.assertEqual((8, 8, 1, 7), (
            primeiro.entrada, primeiro.avaliacoes, primeiro.exclusoes, primeiro.saldo
        ))
        self.assertEqual((7, 7, 1, 6), (
            segundo.entrada, segundo.avaliacoes, segundo.exclusoes, segundo.saldo
        ))
        self.assertEqual(Decimal("12.500000"), segundo.percentual_total_inicial)
        self.assertEqual(Decimal("14.285714"), segundo.percentual_saldo_recebido)

    def test_serializacao_reune_escopo_resumo_familias_e_fechamento(self) -> None:
        quadro = criar_quadro_consolidado(self.relatorio, tipo_escopo="amostra")
        dados = serializar_quadro_consolidado(quadro)

        self.assertFalse(dados["escopo"]["processamento_integral"])
        self.assertEqual(3, len(dados["familias"]))
        self.assertEqual("62.500000", dados["resumo"]["percentual_excluido"])
        self.assertEqual(8, dados["fechamento"]["lado_esquerdo"])
        self.assertEqual(8, dados["fechamento"]["lado_direito"])
        self.assertTrue(dados["fechamento"]["valido"])
        json.dumps(dados)

    def test_recusa_saldo_ou_percentual_adulterado(self) -> None:
        familia = self.relatorio.familias[0]
        filtro = replace(familia.filtros[0], saldo=999)
        adulterada = replace(familia, filtros=(filtro,) + familia.filtros[1:])
        relatorio = replace(
            self.relatorio, familias=(adulterada,) + self.relatorio.familias[1:]
        )
        with self.assertRaises(ErroQuadroConsolidado) as saldo:
            criar_quadro_consolidado(relatorio, tipo_escopo="amostra")
        self.assertEqual("SALDO_FILTRO_DIVERGENTE", saldo.exception.codigo)

        filtro = replace(
            familia.filtros[0], percentual_saldo_recebido=Decimal("99")
        )
        adulterada = replace(familia, filtros=(filtro,) + familia.filtros[1:])
        relatorio = replace(
            self.relatorio, familias=(adulterada,) + self.relatorio.familias[1:]
        )
        with self.assertRaises(ErroQuadroConsolidado) as percentual:
            criar_quadro_consolidado(relatorio, tipo_escopo="amostra")
        self.assertEqual("PERCENTUAL_FILTRO_DIVERGENTE", percentual.exception.codigo)

    def test_recusa_familias_ausentes_ou_fora_da_ordem(self) -> None:
        relatorio = replace(self.relatorio, familias=self.relatorio.familias[:2])
        with self.assertRaises(ErroQuadroConsolidado) as contexto:
            criar_quadro_consolidado(relatorio, tipo_escopo="amostra")
        self.assertEqual("FAMILIAS_DIVERGENTES", contexto.exception.codigo)

    def test_escopo_integral_exige_todo_o_universo(self) -> None:
        with self.assertRaises(ErroQuadroConsolidado) as contexto:
            criar_quadro_consolidado(
                self.relatorio, tipo_escopo="integral", total_universo=50_063_860
            )
        self.assertEqual("INTEGRAL_INCOMPLETO", contexto.exception.codigo)

    def test_amostra_vazia_tambem_reconcilia_sem_divisao_por_zero(self) -> None:
        relatorio = executar_funil_extensivel((), plano())
        quadro = criar_quadro_consolidado(relatorio, tipo_escopo="amostra")

        self.assertEqual(Decimal("0.000000"), quadro.percentual_excluido)
        self.assertEqual(Decimal("0.000000"), quadro.percentual_aprovado)
        self.assertTrue(quadro.reconciliado)


if __name__ == "__main__":
    unittest.main()
