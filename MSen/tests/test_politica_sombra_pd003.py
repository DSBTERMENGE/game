from dataclasses import replace
from pathlib import Path
import unittest

from msen.padroes import detectar_mais_de_tres_dezenas_sequenciais
from msen.screener import (
    AdaptadorPadroesHistoricos,
    EvidenciaHistoricaPadrao,
    PoliticaPadraoSombra,
    carregar_configuracao_screener,
    executar_funil,
)


PADRAO = Path(__file__).resolve().parents[1] / "config" / "screener.toml"
COM_PD003 = (1, 2, 3, 4, 20, 40)
SEM_PD003 = (1, 2, 3, 20, 21, 22)


class PoliticaSombraPD003TestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.configuracao = carregar_configuracao_screener(PADRAO)
        cls.evidencia = EvidenciaHistoricaPadrao(
            "PD_003", 5, 3069, True, "PD_003:3069:2026-10-27"
        )

    def _adaptador(self, *, evidencia=None, tolerancia=3.0):
        configuracao = replace(
            self.configuracao.criterios["padroes_historicos"],
            habilitado=True,
            tolerancias={"tolerancia_ocorrencia_percentual": tolerancia},
        )
        politica = PoliticaPadraoSombra(
            detectar_mais_de_tres_dezenas_sequenciais,
            self.evidencia if evidencia is None else evidencia,
        )
        return AdaptadorPadroesHistoricos("PD_003", configuracao, politica)

    def test_marca_pd003_abaixo_de_tres_por_cento_sem_reprovar(self):
        decisao = self._adaptador().avaliar(COM_PD003)
        self.assertTrue(decisao.aprovada)
        self.assertTrue(decisao.valores["detector_encontrou"])
        self.assertTrue(decisao.valores["marcaria_exclusao"])
        self.assertEqual("0.162920", decisao.valores["percentual_historico"])
        self.assertEqual("marcaria", decisao.valores["decisao_sombra"])

    def test_combinacao_sem_pd003_passa_sem_marca(self):
        decisao = self._adaptador().avaliar(SEM_PD003)
        self.assertTrue(decisao.aprovada)
        self.assertFalse(decisao.valores["detector_encontrou"])
        self.assertFalse(decisao.valores["marcaria_exclusao"])

    def test_percentual_acima_da_tolerancia_nao_marca(self):
        decisao = self._adaptador(tolerancia=0.1).avaliar(COM_PD003)
        self.assertTrue(decisao.aprovada)
        self.assertFalse(decisao.valores["marcaria_exclusao"])

    def test_operador_menor_ou_igual_inclui_a_fronteira(self):
        evidencia = EvidenciaHistoricaPadrao("PD_TESTE", 3, 100, True, "fronteira")
        decisao = self._adaptador(evidencia=evidencia).avaliar(COM_PD003)
        self.assertTrue(decisao.valores["marcaria_exclusao"])

    def test_evidencia_nao_reconciliada_falha_sem_excluir(self):
        evidencia = replace(self.evidencia, reconciliada=False)
        decisao = self._adaptador(evidencia=evidencia).avaliar(COM_PD003)
        self.assertTrue(decisao.aprovada)
        self.assertFalse(decisao.valores["marcaria_exclusao"])
        self.assertEqual("nao_avaliavel", decisao.valores["decisao_sombra"])

    def test_funil_preserva_todas_as_combinacoes_em_sombra(self):
        relatorio = executar_funil((COM_PD003, SEM_PD003), (self._adaptador(),))
        self.assertEqual(2, relatorio.total_recebido)
        self.assertEqual(2, relatorio.total_aprovado)
        self.assertEqual(0, relatorio.exclusoes_por_criterio["PD_003"])


if __name__ == "__main__":
    unittest.main()
