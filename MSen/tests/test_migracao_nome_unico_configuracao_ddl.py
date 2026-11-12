from pathlib import Path
import unittest


class MigracaoNomeUnicoConfiguracaoDDLTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.sql = (
            Path(__file__).parents[2]
            / "database"
            / "migrations"
            / "025_nome_unico_configuracao_selecao.sql"
        ).read_text(encoding="utf-8")

    def test_impede_nomes_repetidos_normalizados(self) -> None:
        self.assertIn("LOWER(BTRIM(nome))", self.sql)
        self.assertIn("uk_config_pesquisa_nome_normalizado", self.sql)
        self.assertIn("CREATE UNIQUE INDEX", self.sql)

    def test_aborta_se_ja_houver_duplicidade(self) -> None:
        self.assertIn("HAVING COUNT(*) > 1", self.sql)
        self.assertIn("nomes equivalentes", self.sql)


if __name__ == "__main__":
    unittest.main()
