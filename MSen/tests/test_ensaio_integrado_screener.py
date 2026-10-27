from dataclasses import replace
from pathlib import Path
import unittest

from msen.screener import (
    ErroEnsaioIntegrado,
    carregar_configuracao_screener,
    executar_ensaio_amostral,
)


PADRAO = Path(__file__).resolve().parents[1] / "config" / "screener.toml"


class RelogioArtificial:
    def __init__(self):
        self.valores = iter((5.0, 5.1))

    def __call__(self):
        return next(self.valores)


class EnsaioIntegradoScreenerTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.configuracao = carregar_configuracao_screener(PADRAO)

    def test_fluxo_integrado_recebe_e_aprova_cinco_mil(self):
        quadro = executar_ensaio_amostral(
            self.configuracao, relogio=RelogioArtificial()
        )
        self.assertEqual(5_000, quadro.total_recebido)
        self.assertEqual(5_000, quadro.total_aprovado)
        self.assertEqual(0.1, round(quadro.duracao_segundos, 1))
        self.assertEqual((), quadro.linhas)
        self.assertEqual(5_000, len(quadro.relatorio.combinacoes_aprovadas))

    def test_mesma_semente_reproduz_as_combinacoes_aprovadas(self):
        primeiro = executar_ensaio_amostral(self.configuracao)
        segundo = executar_ensaio_amostral(self.configuracao)
        self.assertEqual(
            primeiro.relatorio.combinacoes_aprovadas,
            segundo.relatorio.combinacoes_aprovadas,
        )

    def test_semente_diferente_altera_o_ensaio(self):
        outro = replace(self.configuracao, semente=42)
        primeiro = executar_ensaio_amostral(self.configuracao)
        segundo = executar_ensaio_amostral(outro)
        self.assertNotEqual(
            primeiro.relatorio.combinacoes_aprovadas,
            segundo.relatorio.combinacoes_aprovadas,
        )

    def test_bloqueia_criterio_real_habilitado(self):
        criterios = dict(self.configuracao.criterios)
        criterios["padroes_historicos"] = replace(
            criterios["padroes_historicos"], habilitado=True
        )
        configuracao = replace(self.configuracao, criterios=criterios)
        with self.assertRaises(ErroEnsaioIntegrado) as contexto:
            executar_ensaio_amostral(configuracao)
        self.assertEqual("CRITERIO_REAL_NAO_AUTORIZADO", contexto.exception.codigo)

    def test_modo_integral_permanece_bloqueado_pelo_gerador_amostral(self):
        integral = replace(self.configuracao, modo="integral")
        with self.assertRaises(ValueError):
            executar_ensaio_amostral(integral)


if __name__ == "__main__":
    unittest.main()
