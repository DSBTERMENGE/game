from pathlib import Path
import unittest


RAIZ = Path(__file__).resolve().parents[2]
SQL = (RAIZ / "database/migrations/036_associar_funcao_diagonal.sql").read_text(
    encoding="utf-8"
)


class TestMigracaoFuncaoDiagonalDDL(unittest.TestCase):
    def test_associa_por_ids_sem_criar_estrutura(self):
        self.assertIn("WHERE id_padrao = 19", SQL)
        self.assertIn("grupo <> 5", SQL)
        self.assertIn(
            "msen.padroes.diagonais.calcular_categorias_diagonais", SQL
        )
        self.assertNotIn("ALTER TABLE", SQL)
        self.assertNotIn("CREATE TABLE", SQL)

    def test_recusa_sobrescrever_outra_funcao(self):
        self.assertIn("funcao IS NOT NULL", SQL)
        self.assertIn("já possui outra função cadastrada", SQL)


if __name__ == "__main__":
    unittest.main()
