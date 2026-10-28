"""Testes dos grupos de padrões conectados ao funil extensível."""

from datetime import date
from decimal import Decimal
from unittest.mock import Mock
import unittest

from msen.screener import (
    ClassificacaoGrupoFunil,
    ErroFamiliaPadroes,
    FrequenciaPadraoFotografada,
    classificar_sequenciais_para_funil,
    criar_familia_padroes,
    criar_grupo_padroes_fotografado,
    executar_funil_extensivel,
)


def grupo(
    codigo: str = "PG_001", excludente_percentual: int = 3
):
    return criar_grupo_padroes_fotografado(
        grupo_cod=codigo,
        limite_raridade=10,
        operador="<",
        numero_ap_inicial=1,
        numero_ap_final=100,
        data_inicial=date(2020, 1, 1),
        data_final=date(2026, 10, 28),
        denominador=100,
        frequencias=(
            FrequenciaPadraoFotografada("PD_001", 70, Decimal("70")),
            FrequenciaPadraoFotografada("PD_002", 20, Decimal("20")),
            FrequenciaPadraoFotografada(
                "PD_003", excludente_percentual, Decimal(excludente_percentual)
            ),
            FrequenciaPadraoFotografada(
                None, 10 - excludente_percentual, Decimal(10 - excludente_percentual)
            ),
        ),
    )


class FamiliaPadroesExtensivelTests(unittest.TestCase):
    def test_classificador_oficial_exclui_somente_padrao_raro_fotografado(self) -> None:
        familia = criar_familia_padroes(
            grupos_fotografados=(grupo(),),
            classificadores={"PG_001": classificar_sequenciais_para_funil},
        )
        combinacoes = (
            (1, 2, 3, 4, 20, 40),       # PD_003: raro
            (1, 2, 10, 20, 30, 40),     # PD_001: aceito
            (1, 10, 20, 30, 40, 50),    # sem correspondência: aceito
        )
        relatorio = executar_funil_extensivel(combinacoes, (familia,))

        self.assertEqual(1, relatorio.total_excluido)
        self.assertEqual(2, relatorio.total_aprovado)
        self.assertEqual(combinacoes[1:], relatorio.combinacoes_aprovadas)

    def test_grupo_classifica_cada_combinacao_uma_unica_vez(self) -> None:
        classificador = Mock(wraps=classificar_sequenciais_para_funil)
        familia = criar_familia_padroes(
            grupos_fotografados=(grupo(),),
            classificadores={"PG_001": classificador},
        )
        combinacoes = ((1, 2, 10, 20, 30, 40), (1, 10, 20, 30, 40, 50))
        executar_funil_extensivel(combinacoes, (familia,))

        self.assertEqual(2, classificador.call_count)

    def test_evidencia_informa_classe_e_base_historica_congelada(self) -> None:
        fotografado = grupo()
        familia = criar_familia_padroes(
            grupos_fotografados=(fotografado,),
            classificadores={"PG_001": classificar_sequenciais_para_funil},
        )
        decisao = familia.filtros[0].avaliador((1, 2, 3, 4, 20, 40))

        self.assertFalse(decisao.aprovada)
        self.assertEqual("PADRAO_RARO_FOTOGRAFADO", decisao.motivo)
        self.assertEqual("PD_003", decisao.evidencias["padrao_cod"])
        self.assertEqual("3", decisao.evidencias["percentual_historico"])
        self.assertEqual(100, decisao.evidencias["denominador_historico"])
        self.assertEqual(("PD_003",), decisao.evidencias["padroes_excludentes"])

    def test_sem_correspondencia_completa_o_perfil_mas_nao_exclui(self) -> None:
        familia = criar_familia_padroes(
            grupos_fotografados=(grupo(),),
            classificadores={"PG_001": classificar_sequenciais_para_funil},
        )
        decisao = familia.filtros[0].avaliador((1, 10, 20, 30, 40, 50))

        self.assertTrue(decisao.aprovada)
        self.assertIsNone(decisao.evidencias["padrao_cod"])
        self.assertEqual("SEM_CORRESPONDENCIA", decisao.evidencias["classe"])
        self.assertNotIn(None, decisao.evidencias["padroes_excludentes"])

    def test_multiplos_grupos_formam_funil_com_exclusoes_liquidas(self) -> None:
        primeiro = grupo("G001")
        segundo = grupo("G002")
        contagens = {"G001": 0, "G002": 0}

        def classificar(codigo):
            def interno(combinacao):
                contagens[codigo] += 1
                padrao = "PD_003" if combinacao[0] == (1 if codigo == "G001" else 2) else "PD_001"
                return ClassificacaoGrupoFunil.criar(
                    grupo_cod=codigo, padrao_cod=padrao, evidencias={"primeira": combinacao[0]}
                )
            return interno

        familia = criar_familia_padroes(
            grupos_fotografados=(segundo, primeiro),
            classificadores={"G001": classificar("G001"), "G002": classificar("G002")},
        )
        combinacoes = tuple((i, 10, 20, 30, 40, 50) for i in (1, 2, 3))
        relatorio = executar_funil_extensivel(combinacoes, (familia,))

        self.assertEqual((3, 2), tuple(item.avaliacoes for item in relatorio.familias[0].filtros))
        self.assertEqual((1, 1), tuple(item.exclusoes for item in relatorio.familias[0].filtros))
        self.assertEqual({"G001": 3, "G002": 2}, contagens)
        self.assertEqual(1, relatorio.total_aprovado)

    def test_rejeita_classificador_ausente_ou_classe_nao_fotografada(self) -> None:
        fotografado = grupo()
        with self.assertRaises(ErroFamiliaPadroes) as ausente:
            criar_familia_padroes(grupos_fotografados=(fotografado,), classificadores={})
        self.assertEqual("CLASSIFICADORES_INCOMPLETOS", ausente.exception.codigo)

        familia = criar_familia_padroes(
            grupos_fotografados=(fotografado,),
            classificadores={
                "PG_001": lambda _: ClassificacaoGrupoFunil.criar(
                    grupo_cod="PG_001", padrao_cod="PD_999", evidencias={}
                )
            },
        )
        with self.assertRaises(ErroFamiliaPadroes) as desconhecida:
            familia.filtros[0].avaliador((1, 2, 3, 4, 5, 6))
        self.assertEqual("CLASSE_NAO_FOTOGRAFADA", desconhecida.exception.codigo)


if __name__ == "__main__":
    unittest.main()
