"""Testes da família estatística conectada ao funil extensível."""

from decimal import Decimal
import unittest

from msen.screener import (
    ErroFamiliaEstatistica,
    FaixaEstatistica,
    criar_familia_estatistica,
    executar_funil_extensivel,
)


class FamiliaEstatisticaExtensivelTests(unittest.TestCase):
    def _familia(
        self,
        soma=(21, 345),
        mediana=(Decimal("3.5"), Decimal("57.5")),
        desvio=(Decimal("0"), Decimal("30")),
    ):
        return criar_familia_estatistica(
            faixa_soma=FaixaEstatistica.criar(*soma),
            faixa_mediana=FaixaEstatistica.criar(*mediana),
            faixa_desvio_padrao=FaixaEstatistica.criar(*desvio),
        )

    def test_soma_e_media_sao_um_unico_filtro_e_uma_unica_exclusao(self) -> None:
        familia = self._familia(soma=(100, 200))
        relatorio = executar_funil_extensivel(((1, 2, 3, 4, 5, 6),), (familia,))
        linha = relatorio.familias[0]

        self.assertEqual(
            ("EST_SOMA_MEDIA", "EST_MEDIANA", "EST_DESVIO_PADRAO"),
            tuple(item.codigo_filtro for item in linha.filtros),
        )
        self.assertEqual(1, linha.exclusoes)
        self.assertEqual((1, 0, 0), tuple(item.avaliacoes for item in linha.filtros))
        decisao = familia.filtros[0].avaliador((1, 2, 3, 4, 5, 6))
        self.assertEqual("3.500000", decisao.evidencias["media_equivalente"])
        self.assertEqual(
            "16.66666666666666666666666667",
            decisao.evidencias["limite_inferior_media_equivalente"],
        )
        self.assertEqual("unica", decisao.evidencias["contabilizacao"])

    def test_valores_exatamente_nos_limites_sao_aceitos(self) -> None:
        combinacao = (1, 2, 3, 4, 5, 6)
        desvio = Decimal("1.707825")
        familia = self._familia(
            soma=(21, 21), mediana=(Decimal("3.5"), Decimal("3.5")),
            desvio=(desvio, desvio),
        )
        relatorio = executar_funil_extensivel((combinacao,), (familia,))

        self.assertEqual(1, relatorio.total_aprovado)
        self.assertEqual(0, relatorio.total_excluido)
        self.assertEqual((1, 1, 1), tuple(
            item.avaliacoes for item in relatorio.familias[0].filtros
        ))

    def test_cada_filtro_exclui_somente_o_saldo_que_recebe(self) -> None:
        combinacoes = (
            (1, 2, 3, 4, 5, 6),             # soma abaixo
            (10, 20, 30, 40, 50, 60),       # mediana acima
            (20, 21, 22, 23, 24, 25),       # desvio abaixo
            (5, 10, 15, 20, 25, 30),        # aprovada
        )
        familia = self._familia(
            soma=(80, 220), mediana=(10, 30), desvio=(Decimal("5"), Decimal("20"))
        )
        relatorio = executar_funil_extensivel(combinacoes, (familia,))
        linhas = relatorio.familias[0].filtros

        self.assertEqual((4, 3, 2), tuple(item.avaliacoes for item in linhas))
        self.assertEqual((1, 1, 1), tuple(item.exclusoes for item in linhas))
        self.assertEqual(3, relatorio.total_excluido)
        self.assertEqual(1, relatorio.total_aprovado)
        self.assertTrue(relatorio.reconciliado)

    def test_evidencias_usam_funcoes_oficiais_e_explicam_limites(self) -> None:
        familia = self._familia()
        combinacao = (10, 20, 30, 40, 50, 60)
        soma_media = familia.filtros[0].avaliador(combinacao)
        mediana = familia.filtros[1].avaliador(combinacao)
        desvio = familia.filtros[2].avaliador(combinacao)

        self.assertEqual(210, soma_media.evidencias["soma"])
        self.assertEqual("35.000000", soma_media.evidencias["media_equivalente"])
        self.assertEqual("35.0", mediana.evidencias["mediana"])
        self.assertEqual("17.078251", desvio.evidencias["desvio_padrao_populacional"])
        self.assertTrue(all(item.evidencias["intervalo"] == "fechado" for item in (
            soma_media, mediana, desvio
        )))

    def test_faixa_invertida_nao_e_aceita(self) -> None:
        with self.assertRaises(ErroFamiliaEstatistica) as contexto:
            FaixaEstatistica.criar(20, 10)
        self.assertEqual("FAIXA_INVERTIDA", contexto.exception.codigo)


if __name__ == "__main__":
    unittest.main()
