from pathlib import Path
import unittest


class MigracaoRemoverBacktestPersistenteDDLTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.sql = (
            Path(__file__).parents[2]
            / "database"
            / "migrations"
            / "024_remover_backtest_persistente.sql"
        ).read_text(encoding="utf-8")

    def test_remove_somente_execucoes_backtest_e_protege_lotes(self) -> None:
        self.assertIn("WHERE e.tipo_execucao = 'BACKTEST'", self.sql)
        self.assertIn("WHERE tipo_execucao = 'BACKTEST'", self.sql)
        self.assertIn("lotes_jogos_selecao", self.sql)
        self.assertNotIn("DROP TABLE", self.sql.upper())

    def test_modelo_passa_a_aceitar_apenas_previsao(self) -> None:
        self.assertIn("CHECK (tipo_execucao = 'PREVISAO_FUTURA')", self.sql)
        self.assertIn("DROP INDEX IF EXISTS ix_execucao_pesquisa_comparacao", self.sql)


if __name__ == "__main__":
    unittest.main()
