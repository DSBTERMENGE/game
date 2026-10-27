import tempfile
from pathlib import Path
import unittest

from msen.screener import ErroConfiguracaoScreener, carregar_configuracao_screener


RAIZ = Path(__file__).resolve().parents[1]
PADRAO = RAIZ / "config" / "screener.toml"


class ConfiguracaoScreenerTestCase(unittest.TestCase):
    def test_carrega_contrato_padrao_seguro(self):
        configuracao = carregar_configuracao_screener(PADRAO)
        self.assertEqual("amostra", configuracao.modo)
        self.assertEqual(5_000, configuracao.limite_combinacoes)
        self.assertEqual(20261027, configuracao.semente)
        self.assertFalse(configuracao.confirmacao_processamento_integral)
        self.assertEqual(
            ("padroes_historicos", "medidas_estatisticas", "medidas_geometricas"),
            configuracao.ordem_filtros,
        )
        self.assertTrue(all(not item.habilitado for item in configuracao.criterios.values()))

    def test_arquivo_local_substitui_somente_valor_informado(self):
        with tempfile.TemporaryDirectory() as pasta:
            local = Path(pasta) / "local.toml"
            local.write_text("[execucao]\nsemente = 42\n", encoding="utf-8")
            configuracao = carregar_configuracao_screener(PADRAO, local)
        self.assertEqual(42, configuracao.semente)
        self.assertEqual(5_000, configuracao.limite_combinacoes)

    def test_local_ausente_nao_impede_carregamento(self):
        configuracao = carregar_configuracao_screener(PADRAO, "inexistente.toml")
        self.assertEqual(5_000, configuracao.limite_combinacoes)

    def test_rejeita_alteracao_do_limite_experimental(self):
        with tempfile.TemporaryDirectory() as pasta:
            local = Path(pasta) / "local.toml"
            local.write_text("[execucao]\nlimite_combinacoes = 5001\n", encoding="utf-8")
            with self.assertRaises(ErroConfiguracaoScreener) as contexto:
                carregar_configuracao_screener(PADRAO, local)
        self.assertEqual("LIMITE_EXPERIMENTAL_INVALIDO", contexto.exception.codigo)

    def test_rejeita_criterio_habilitado_antes_da_aprovacao(self):
        with tempfile.TemporaryDirectory() as pasta:
            local = Path(pasta) / "local.toml"
            local.write_text("[criterios.padroes_historicos]\nhabilitado = true\n", encoding="utf-8")
            with self.assertRaises(ErroConfiguracaoScreener) as contexto:
                carregar_configuracao_screener(PADRAO, local)
        self.assertEqual("CRITERIO_NAO_AUTORIZADO", contexto.exception.codigo)

    def test_rejeita_ordem_incompleta(self):
        with tempfile.TemporaryDirectory() as pasta:
            local = Path(pasta) / "local.toml"
            local.write_text('[funil]\nordem = ["medidas_geometricas"]\n', encoding="utf-8")
            with self.assertRaises(ErroConfiguracaoScreener) as contexto:
                carregar_configuracao_screener(PADRAO, local)
        self.assertEqual("ORDEM_FILTROS_INVALIDA", contexto.exception.codigo)


if __name__ == "__main__":
    unittest.main()
