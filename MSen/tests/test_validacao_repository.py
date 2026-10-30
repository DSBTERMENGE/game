from dataclasses import FrozenInstanceError
from datetime import datetime, timezone
from decimal import Decimal
import unittest

from msen.database import RepositorioValidacao
from msen.database.validacao_repository import (
    AmostraValidacao,
    AvaliacaoValidacaoDetalhada,
    _id_positivo,
    _linha_para_amostra,
    _linha_para_avaliacao,
)


class RepositorioValidacaoMapeamentoTestCase(unittest.TestCase):
    def setUp(self):
        self.momento = datetime(2026, 10, 30, tzinfo=timezone.utc)

    def test_mapeia_amostra_sem_duplicar_dezenas_no_modelo_de_banco(self):
        amostra = _linha_para_amostra(
            (7, 1, True, self.momento, 100, 4, 9, 10, 13, 39, 52)
        )
        self.assertEqual(
            AmostraValidacao(7, 1, True, self.momento, 100, (4, 9, 10, 13, 39, 52)),
            amostra,
        )
        with self.assertRaises(FrozenInstanceError):
            amostra.ordem = 2  # type: ignore[misc]

    def test_mapeia_avaliacao_com_nomes_resolvidos(self):
        linha = (
            7, 100, 4, 9, 10, 13, 39, 52, 3, "PAD_SEQ", "Sequenciais",
            "PADRAO", "msen.padroes.classificar", "PADRAO", "a" * 64,
            "APROVADO", "PG_001", "Sequenciais", True, None, None,
            "PADRAO_IDENTIFICADO", "PD_002", "Duas sequenciais",
            "PADRAO_IDENTIFICADO", "PD_002", "Duas sequenciais", True, "S",
        )
        avaliacao = _linha_para_avaliacao(linha)
        self.assertIsInstance(avaliacao, AvaliacaoValidacaoDetalhada)
        self.assertEqual((4, 9, 10, 13, 39, 52), avaliacao.dezenas)
        self.assertEqual("Sequenciais", avaliacao.grupo_nome)
        self.assertEqual("Duas sequenciais", avaliacao.subgrupo_esperado_nome)
        self.assertEqual("S", avaliacao.aprovado)

    def test_mapeia_avaliacao_numerica(self):
        linha = (
            8, 101, 1, 2, 3, 4, 5, 6, 4, "EST_SOMA", "Soma", "ESTATISTICA",
            "msen.calculos.soma", "INTEIRO", "b" * 64, "PENDENTE", None, None,
            True, Decimal("21"), Decimal("21"), None, None, None, None, None,
            None, True, "S",
        )
        avaliacao = _linha_para_avaliacao(linha)
        self.assertEqual(Decimal("21"), avaliacao.valor_esperado)
        self.assertIsNone(avaliacao.grupo_codigo)

    def test_rejeita_quantidade_incorreta_de_colunas(self):
        with self.assertRaises(ValueError):
            _linha_para_amostra((1, 2))
        with self.assertRaises(ValueError):
            _linha_para_avaliacao((1, 2))

    def test_valida_identificadores(self):
        self.assertEqual(1, _id_positivo("id_resultado", 1))
        for valor in (0, -1):
            with self.assertRaises(ValueError):
                _id_positivo("id_resultado", valor)
        for valor in (True, "1"):
            with self.assertRaises(TypeError):
                _id_positivo("id_resultado", valor)  # type: ignore[arg-type]

    def test_repositorio_exige_conexao_psycopg(self):
        with self.assertRaises(TypeError):
            RepositorioValidacao(object())  # type: ignore[arg-type]


if __name__ == "__main__":
    unittest.main()
