import tempfile
from decimal import Decimal
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
        self.assertEqual(Decimal("10.000000"), configuracao.limite_raridade_percentual)
        self.assertEqual(
            ("padroes_historicos", "medidas_estatisticas", "medidas_geometricas"),
            configuracao.ordem_filtros,
        )
        self.assertTrue(all(not item.habilitado for item in configuracao.criterios.values()))
        regra = configuracao.regras["PD_003"]
        self.assertEqual("ativo", regra.modo)
        self.assertEqual(3.0, regra.tolerancia_percentual)
        self.assertEqual(5, regra.num_ocorrencias)
        self.assertEqual(3069, regra.total_resultados)
        regra_pd002 = configuracao.regras["PD_002"]
        self.assertEqual("ativo", regra_pd002.modo)
        self.assertEqual(3.0, regra_pd002.tolerancia_percentual)
        self.assertEqual(92, regra_pd002.num_ocorrencias)
        self.assertEqual(3069, regra_pd002.total_resultados)
        regra_pd006 = configuracao.regras["PD_006"]
        self.assertEqual("ativo", regra_pd006.modo)
        self.assertEqual(3.0, regra_pd006.tolerancia_percentual)
        self.assertEqual(4, regra_pd006.num_ocorrencias)
        self.assertEqual(3069, regra_pd006.total_resultados)
        regra_pd005 = configuracao.regras["PD_005"]
        self.assertEqual("ativo", regra_pd005.modo)
        self.assertEqual(3.0, regra_pd005.tolerancia_percentual)
        self.assertEqual(66, regra_pd005.num_ocorrencias)
        self.assertEqual(3069, regra_pd005.total_resultados)
        regra_media = configuracao.regras_estatisticas["EST_MEDIA_P01_P99"]
        self.assertEqual("ativo", regra_media.modo)
        self.assertEqual(15.0, regra_media.limite_inferior)
        self.assertEqual(45.886666, regra_media.limite_superior)
        regra_desvio = configuracao.regras_estatisticas["EST_DESVIO_P01_P99"]
        self.assertEqual("ativo", regra_desvio.modo)
        self.assertEqual(7.145546, regra_desvio.limite_inferior)
        self.assertEqual(22.774694, regra_desvio.limite_superior)
        regra_mediana = configuracao.regras_estatisticas["EST_MEDIANA_P01_P99"]
        self.assertEqual("ativo", regra_mediana.modo)
        self.assertEqual(10.5, regra_mediana.limite_inferior)
        self.assertEqual(50.5, regra_mediana.limite_superior)
        regra_extensao = configuracao.regras_geometricas["GEO_EXTENSAO_P01_P99"]
        self.assertEqual("ativo", regra_extensao.modo)
        self.assertEqual(8.650282, regra_extensao.limite_inferior)
        self.assertEqual(32.300058, regra_extensao.limite_superior)

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

    def test_local_substitui_o_limite_unico_de_raridade(self):
        with tempfile.TemporaryDirectory() as pasta:
            local = Path(pasta) / "local.toml"
            local.write_text("[raridade]\nlimite_percentual = 3.25\n", encoding="utf-8")
            configuracao = carregar_configuracao_screener(PADRAO, local)
        self.assertEqual(Decimal("3.250000"), configuracao.limite_raridade_percentual)

    def test_rejeita_limite_de_raridade_invalido(self):
        for texto in (
            "[raridade]\nlimite_percentual = -0.1\n",
            "[raridade]\nlimite_percentual = 100.1\n",
            "[raridade]\nlimite_percentual = 'texto'\n",
        ):
            with self.subTest(texto=texto), tempfile.TemporaryDirectory() as pasta:
                local = Path(pasta) / "local.toml"
                local.write_text(texto, encoding="utf-8")
                with self.assertRaises(ErroConfiguracaoScreener) as contexto:
                    carregar_configuracao_screener(PADRAO, local)
                self.assertEqual("LIMITE_RARIDADE_INVALIDO", contexto.exception.codigo)

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
