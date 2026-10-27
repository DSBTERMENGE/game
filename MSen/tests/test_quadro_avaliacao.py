import json
from pathlib import Path
import unittest

from msen.screener import (
    DecisaoCriterio,
    carregar_configuracao_screener,
    executar_ensaio,
    gerar_amostra,
    serializar_quadro_avaliacao,
)


PADRAO = Path(__file__).resolve().parents[1] / "config" / "screener.toml"


class CriterioArtificial:
    def __init__(self, codigo, reprovar_primeira_dezena):
        self.codigo = codigo
        self.reprovar_primeira_dezena = reprovar_primeira_dezena

    def avaliar(self, combinacao):
        aprovada = combinacao[0] != self.reprovar_primeira_dezena
        return DecisaoCriterio(aprovada, self.codigo, {"primeira": combinacao[0]})


class RelogioArtificial:
    def __init__(self, *valores):
        self.valores = iter(valores)

    def __call__(self):
        return next(self.valores)


class QuadroAvaliacaoTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.configuracao = carregar_configuracao_screener(PADRAO)

    def test_quadro_sem_filtros_registra_ensaio_de_cinco_mil(self):
        amostra = gerar_amostra(self.configuracao)
        quadro = executar_ensaio(
            amostra, (), self.configuracao, relogio=RelogioArtificial(10.0, 10.25)
        )
        self.assertEqual(5_000, quadro.total_recebido)
        self.assertEqual(5_000, quadro.total_aprovado)
        self.assertEqual(0.25, quadro.duracao_segundos)
        self.assertEqual(20261027, quadro.semente)
        self.assertEqual((), quadro.linhas)

    def test_linhas_mostram_ordem_exclusoes_e_saldo(self):
        combinacoes = (
            (1, 10, 20, 30, 40, 50),
            (2, 10, 20, 30, 40, 50),
            (3, 10, 20, 30, 40, 50),
        )
        quadro = executar_ensaio(
            combinacoes,
            (CriterioArtificial("C1", 1), CriterioArtificial("C2", 2)),
            self.configuracao,
            relogio=RelogioArtificial(2.0, 2.5),
        )
        self.assertEqual(
            [(1, "C1", 3, 1, 2), (2, "C2", 2, 1, 1)],
            [
                (linha.ordem, linha.codigo_criterio, linha.avaliacoes,
                 linha.exclusoes, linha.saldo)
                for linha in quadro.linhas
            ],
        )
        self.assertEqual(1, quadro.total_aprovado)

    def test_serializacao_json_preserva_configuracao_e_semente(self):
        quadro = executar_ensaio(
            (), (), self.configuracao, relogio=RelogioArtificial(1.0, 1.0)
        )
        dados = serializar_quadro_avaliacao(quadro)
        self.assertEqual("amostra", dados["configuracao"]["modo"])
        self.assertEqual(20261027, dados["configuracao"]["semente"])
        self.assertFalse(
            dados["configuracao"]["criterios"]["padroes_historicos"]["habilitado"]
        )
        json.dumps(dados)

    def test_rejeita_relogio_que_retrocede(self):
        with self.assertRaises(ValueError):
            executar_ensaio(
                (), (), self.configuracao, relogio=RelogioArtificial(2.0, 1.0)
            )

    def test_exige_configuracao_validada(self):
        with self.assertRaises(TypeError):
            executar_ensaio((), (), object())


if __name__ == "__main__":
    unittest.main()
