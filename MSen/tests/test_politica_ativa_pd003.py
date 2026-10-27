from pathlib import Path
import unittest

from msen.padroes import detectar_mais_de_tres_dezenas_sequenciais
from msen.screener import (
    EvidenciaHistoricaPadrao,
    PoliticaPadraoAtiva,
    carregar_configuracao_screener,
)


PADRAO = Path(__file__).resolve().parents[1] / "config" / "screener.toml"


class PoliticaAtivaPD003TestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        config = carregar_configuracao_screener(PADRAO)
        regra = config.regras["PD_003"]
        cls.tolerancias = {"tolerancia_ocorrencia_percentual": regra.tolerancia_percentual}
        cls.politica = PoliticaPadraoAtiva(
            detectar_mais_de_tres_dezenas_sequenciais,
            EvidenciaHistoricaPadrao(
                regra.codigo,
                regra.num_ocorrencias,
                regra.total_resultados,
                True,
                regra.reconciliacao,
            ),
        )

    def test_exclui_combinacao_que_atende_pd003(self):
        resultado = self.politica((1, 2, 3, 4, 20, 40), self.tolerancias)
        self.assertFalse(resultado.aprovada)
        self.assertEqual("reprovou", resultado.valores["decisao"])

    def test_aprova_combinacao_que_nao_atende_pd003(self):
        resultado = self.politica((1, 3, 5, 7, 9, 11), self.tolerancias)
        self.assertTrue(resultado.aprovada)
        self.assertEqual("passou", resultado.valores["decisao"])

    def test_evidencia_nao_reconciliada_nao_exclui(self):
        politica = PoliticaPadraoAtiva(
            detectar_mais_de_tres_dezenas_sequenciais,
            EvidenciaHistoricaPadrao("PD_003", 5, 3069, False, "teste"),
        )
        resultado = politica((1, 2, 3, 4, 20, 40), self.tolerancias)
        self.assertTrue(resultado.aprovada)
        self.assertEqual("nao_avaliavel", resultado.valores["decisao"])


if __name__ == "__main__":
    unittest.main()
