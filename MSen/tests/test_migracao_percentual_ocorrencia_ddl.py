import unittest
from pathlib import Path

from msen.database import descobrir_migracoes


RAIZ_PROJETO = Path(__file__).resolve().parents[2]
PASTA_MIGRACOES = RAIZ_PROJETO / "database" / "migrations"
ESQUEMA_CONSOLIDADO = RAIZ_PROJETO / "database" / "schema_postgresql.sql"


class MigracaoPercentualOcorrenciaDDLTestCase(unittest.TestCase):
    """Valida o contrato estrutural da migracao 009."""

    @classmethod
    def setUpClass(cls):
        cls.migracao = (
            PASTA_MIGRACOES / "009_adicionar_percentual_ocorrencia_padroes.sql"
        )
        cls.sql = cls.migracao.read_text(encoding="utf-8")
        cls.esquema = ESQUEMA_CONSOLIDADO.read_text(encoding="utf-8")

    def test_migracao_009_e_descoberta_antes_da_010(self):
        migracoes = descobrir_migracoes(PASTA_MIGRACOES)
        migracao_009 = next(item for item in migracoes if item.versao == "009")
        self.assertEqual(self.migracao, migracao_009.caminho)
        self.assertLess(
            migracoes.index(migracao_009),
            next(i for i, item in enumerate(migracoes) if item.versao == "010"),
        )

    def test_adiciona_denominador_e_percentual_sem_historico(self):
        self.assertIn("ADD COLUMN total_sorteios INTEGER", self.sql)
        self.assertIn(
            "ADD COLUMN percentual_ocorrencia NUMERIC(9,6)", self.sql
        )
        self.assertNotIn("CREATE TABLE", self.sql)

    def test_percentual_exige_fotografia_consistente(self):
        for trecho in (
            "total_sorteios > 0",
            "percentual_ocorrencia BETWEEN 0 AND 100",
            "num_oco <= total_sorteios",
            "num_oco::NUMERIC * 100 / total_sorteios",
            "ROUND(",
        ):
            with self.subTest(trecho=trecho):
                self.assertIn(trecho, self.sql)

    def test_transicao_aceita_novos_campos_nulos_em_conjunto(self):
        self.assertIn("total_sorteios IS NULL", self.sql)
        self.assertIn("percentual_ocorrencia IS NULL", self.sql)

    def test_esquema_consolidado_repete_o_contrato(self):
        for trecho in (
            "total_sorteios INTEGER",
            "percentual_ocorrencia NUMERIC(9,6)",
            "ck_padroes_fotografia_ocorrencia",
            "num_oco::NUMERIC * 100 / total_sorteios",
        ):
            with self.subTest(trecho=trecho):
                self.assertIn(trecho, self.esquema)


if __name__ == "__main__":
    unittest.main()
