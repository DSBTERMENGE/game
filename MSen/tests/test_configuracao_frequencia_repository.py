"""Testes unitários do mapeamento da configuração persistida."""

from datetime import datetime, timezone
from decimal import Decimal
import unittest

from msen.database.configuracao_frequencia_repository import (
    ErroRepositorioConfiguracaoFrequencia,
    _mapear,
)
from msen.services import configuracao_frequencia_inicial


class ConfiguracaoFrequenciaRepositoryTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.config = configuracao_frequencia_inicial()
        self.instante = datetime(2026, 10, 30, tzinfo=timezone.utc)

    def linha(self, assinatura: str | None = None):
        c = self.config
        return (
            c.nome, c.concurso_inicial, c.tamanho_inicial, c.regra_janela,
            c.tipo_evento, c.metodo_faixa, Decimal("1.000000"),
            c.unidade_parametro, c.regra_arredondamento, c.versao_calculo,
            assinatura or c.assinatura_sha256, self.instante,
        )

    def test_mapeia_e_confere_assinatura(self) -> None:
        persistida = _mapear(self.linha())
        self.assertEqual(self.config, persistida.configuracao)
        self.assertEqual(self.config.assinatura_sha256, persistida.assinatura_sha256)

    def test_recusa_assinatura_divergente(self) -> None:
        with self.assertRaises(ErroRepositorioConfiguracaoFrequencia) as contexto:
            _mapear(self.linha("0" * 64))
        self.assertEqual("ASSINATURA_DIVERGENTE", contexto.exception.codigo)

    def test_recusa_quantidade_de_colunas_incorreta(self) -> None:
        with self.assertRaises(ValueError):
            _mapear((1, 2))


if __name__ == "__main__":
    unittest.main()
