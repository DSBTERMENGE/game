"""Exemplos manuais do contrato extensível da Etapa 18.1."""

from decimal import Decimal
import unittest

from msen.screener import (
    DecisaoFiltro,
    DefinicaoFamilia,
    DefinicaoFiltro,
    ErroContratoFunil,
    executar_funil_extensivel,
)


def combinacao(indice: int) -> tuple[int, int, int, int, int, int]:
    return (indice, 10, 20, 30, 40, 50)


def avaliador(codigo: str, excluidas: set[int]):
    def avaliar(item):
        valor = item[0]
        excluir = valor in excluidas
        return DecisaoFiltro.criar(
            codigo_filtro=codigo,
            aprovada=not excluir,
            motivo="FORA_DA_FAIXA" if excluir else "DENTRO_DA_FAIXA",
            evidencias={"valor": valor, "limite": tuple(sorted(excluidas))},
        )
    return avaliar


def plano_base() -> tuple[DefinicaoFamilia, ...]:
    return (
        DefinicaoFamilia(
            "ESTATISTICA", "Valores estatísticos", 1,
            (
                DefinicaoFiltro("EST_SOMA", "Soma", 1, avaliador("EST_SOMA", {1})),
                DefinicaoFiltro("EST_DESVIO", "Desvio", 2, avaliador("EST_DESVIO", {2})),
            ),
        ),
        DefinicaoFamilia(
            "GEOMETRIA", "Análise geométrica", 2,
            (DefinicaoFiltro("GEO_AREA", "Área", 1, avaliador("GEO_AREA", {3})),),
        ),
        DefinicaoFamilia(
            "PADROES", "Padrões históricos", 3,
            (DefinicaoFiltro("PAD_GRUPO_1", "Grupo 1", 1, avaliador("PAD_GRUPO_1", {4, 5})),),
        ),
    )


class ContratoFunilExtensivelTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.combinacoes = tuple(combinacao(indice) for indice in range(1, 9))

    def test_fecha_exemplo_manual_em_tres_familias(self) -> None:
        relatorio = executar_funil_extensivel(self.combinacoes, plano_base())

        self.assertEqual(relatorio.total_inicial, 8)
        self.assertEqual(relatorio.total_excluido, 5)
        self.assertEqual(relatorio.total_aprovado, 3)
        self.assertTrue(relatorio.reconciliado)
        self.assertEqual(tuple(item[0] for item in relatorio.combinacoes_aprovadas), (6, 7, 8))
        self.assertEqual(
            tuple((familia.entrada, familia.exclusoes, familia.saldo) for familia in relatorio.familias),
            ((8, 2, 6), (6, 1, 5), (5, 2, 3)),
        )

    def test_percentuais_usam_total_inicial_e_saldo_recebido(self) -> None:
        relatorio = executar_funil_extensivel(self.combinacoes, plano_base())
        estatistica, geometria, padroes = relatorio.familias

        self.assertEqual(estatistica.percentual_total_inicial, Decimal("25.000000"))
        self.assertEqual(estatistica.percentual_saldo_recebido, Decimal("25.000000"))
        self.assertEqual(geometria.percentual_total_inicial, Decimal("12.500000"))
        self.assertEqual(geometria.percentual_saldo_recebido, Decimal("16.666667"))
        self.assertEqual(padroes.percentual_total_inicial, Decimal("25.000000"))
        self.assertEqual(padroes.percentual_saldo_recebido, Decimal("40.000000"))

    def test_primeira_exclusao_interrompe_e_e_contada_uma_vez(self) -> None:
        relatorio = executar_funil_extensivel(self.combinacoes, plano_base())
        estatistica, geometria, padroes = relatorio.familias

        self.assertEqual(
            tuple((linha.avaliacoes, linha.exclusoes) for linha in estatistica.filtros),
            ((8, 1), (7, 1)),
        )
        self.assertEqual((geometria.filtros[0].avaliacoes, geometria.filtros[0].exclusoes), (6, 1))
        self.assertEqual((padroes.filtros[0].avaliacoes, padroes.filtros[0].exclusoes), (5, 2))
        self.assertEqual(sum(f.exclusoes for familia in relatorio.familias for f in familia.filtros), 5)

    def test_novo_filtro_e_inserido_por_dados_sem_mudar_o_executor(self) -> None:
        estatistica, geometria, padroes = plano_base()
        geometria_ampliada = DefinicaoFamilia(
            geometria.codigo, geometria.nome, geometria.ordem,
            geometria.filtros + (
                DefinicaoFiltro("GEO_CENTRO", "Centro", 2, avaliador("GEO_CENTRO", {4})),
            ),
        )

        relatorio = executar_funil_extensivel(
            self.combinacoes, (padroes, geometria_ampliada, estatistica)
        )

        self.assertEqual(tuple(f.codigo_familia for f in relatorio.familias), ("ESTATISTICA", "GEOMETRIA", "PADROES"))
        self.assertEqual(tuple(f.codigo_filtro for f in relatorio.familias[1].filtros), ("GEO_AREA", "GEO_CENTRO"))
        self.assertEqual(relatorio.familias[1].exclusoes, 2)
        self.assertEqual(relatorio.familias[2].entrada, 4)
        self.assertEqual(relatorio.total_aprovado, 3)

    def test_decisao_exige_motivo_e_congela_evidencias(self) -> None:
        evidencias = {"valor": 10}
        decisao = DecisaoFiltro.criar(
            codigo_filtro="F1", aprovada=True, motivo="DENTRO", evidencias=evidencias
        )
        evidencias["valor"] = 99

        self.assertEqual(decisao.evidencias["valor"], 10)
        with self.assertRaises(TypeError):
            decisao.evidencias["novo"] = 1
        with self.assertRaises(ErroContratoFunil) as contexto:
            DecisaoFiltro.criar(
                codigo_filtro="F1", aprovada=False, motivo=" ", evidencias={}
            )
        self.assertEqual(contexto.exception.codigo, "MOTIVO_AUSENTE")

    def test_rejeita_plano_ambiguo_e_decisao_divergente(self) -> None:
        familia = plano_base()[0]
        duplicada = DefinicaoFamilia("OUTRA", "Outra", 2, (familia.filtros[0],))
        with self.assertRaises(ErroContratoFunil) as duplicado:
            executar_funil_extensivel(self.combinacoes, (familia, duplicada))
        self.assertEqual(duplicado.exception.codigo, "FILTRO_DUPLICADO")

        filtro = DefinicaoFiltro("F1", "Filtro", 1, avaliador("OUTRO", set()))
        with self.assertRaises(ErroContratoFunil) as divergente:
            executar_funil_extensivel(self.combinacoes, (DefinicaoFamilia("X", "X", 1, (filtro,)),))
        self.assertEqual(divergente.exception.codigo, "CODIGO_DECISAO_DIVERGENTE")

    def test_historico_vazio_ainda_fecha_em_zero(self) -> None:
        relatorio = executar_funil_extensivel((), plano_base())

        self.assertEqual(relatorio.total_inicial, 0)
        self.assertEqual(relatorio.total_aprovado, 0)
        self.assertTrue(relatorio.reconciliado)
        self.assertTrue(all(f.percentual_saldo_recebido == 0 for f in relatorio.familias))


if __name__ == "__main__":
    unittest.main()
