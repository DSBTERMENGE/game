from pathlib import Path
import unittest

from msen.screener import (
    comparar_ordens_filtros,
    carregar_configuracao_screener,
    executar_padroes_ativos,
)


PADRAO = Path(__file__).resolve().parents[1] / "config" / "screener.toml"


class ComparacaoOrdensFiltrosTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.configuracao = carregar_configuracao_screener(PADRAO)
        instantes = iter((0.0, 1.0, 2.0, 3.0, 4.0, 5.0))
        cls.resultados = comparar_ordens_filtros(
            cls.configuracao, relogio=lambda: next(instantes)
        )

    def test_ordens_preservam_as_mesmas_aprovadas(self):
        self.assertEqual([4_409, 4_409, 4_409], [r.total_aprovado for r in self.resultados])
        self.assertTrue(all(r.duracao_segundos == 1.0 for r in self.resultados))

    def test_compara_avaliacoes_evitadas(self):
        por_nome = {resultado.nome: resultado for resultado in self.resultados}
        self.assertEqual(37_985, por_nome["atual"].total_avaliacoes)
        self.assertEqual(2_015, por_nome["atual"].avaliacoes_evitadas)
        self.assertEqual(
            37_569, por_nome["historicos_frequentes_primeiro"].total_avaliacoes
        )
        self.assertEqual(
            2_431, por_nome["historicos_frequentes_primeiro"].avaliacoes_evitadas
        )
        self.assertEqual(
            37_315, por_nome["geometria_e_estatisticas_primeiro"].total_avaliacoes
        )
        self.assertEqual(
            2_685, por_nome["geometria_e_estatisticas_primeiro"].avaliacoes_evitadas
        )

    def test_rejeita_ordem_incompleta(self):
        with self.assertRaises(ValueError):
            executar_padroes_ativos(self.configuracao, ("PD_003",))


if __name__ == "__main__":
    unittest.main()
