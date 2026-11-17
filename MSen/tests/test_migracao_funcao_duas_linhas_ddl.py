from pathlib import Path
import unittest


RAIZ = Path(__file__).resolve().parents[2]
SQL = (RAIZ / "database/migrations/037_associar_funcao_duas_linhas.sql").read_text(
    encoding="utf-8"
)


class TestMigracaoFuncaoDuasLinhasDDL(unittest.TestCase):
    def test_associa_por_ids_sem_criar_estrutura(self):
        self.assertIn("WHERE id_padrao = 17", SQL)
        self.assertIn("grupo <> 8", SQL)
        self.assertIn(
            "msen.padroes.duas_linhas.detectar_dezenas_em_duas_linhas", SQL
        )
        self.assertNotIn("ALTER TABLE", SQL)
        self.assertNotIn("CREATE TABLE", SQL)

    def test_recusa_sobrescrever_outra_funcao(self):
        self.assertIn("funcao IS NOT NULL", SQL)
        self.assertIn("já possui outra função cadastrada", SQL)


if __name__ == "__main__":
    unittest.main()
