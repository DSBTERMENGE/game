"""Testes estáticos da migração 029."""

from pathlib import Path
import unittest


SQL = (Path(__file__).parents[2] / "database" / "migrations" /
       "029_data_registro_remover_prioridade_origem.sql").read_text(encoding="utf-8")


class MigracaoGestaoDesenvolvimento029Test(unittest.TestCase):
    def test_cria_data_e_remove_campos(self):
        self.assertIn("ADD COLUMN data_registro DATE", SQL)
        self.assertIn("DROP COLUMN prioridade", SQL)
        self.assertIn("DROP COLUMN origem_registro", SQL)
        self.assertIn("DROP COLUMN origem_evento", SQL)

    def test_preserva_estados_e_converte_existentes(self):
        self.assertIn("status_trabalho", SQL)
        self.assertIn("status_publicacao", SQL)
        self.assertIn("criado_em::date", SQL)


if __name__ == "__main__":
    unittest.main()
