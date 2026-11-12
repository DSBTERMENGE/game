"""Testes estáticos da migração 030."""

from pathlib import Path
import unittest


SQL = (Path(__file__).parents[2] / "database" / "migrations" /
       "030_remover_criterios_referencia_manutencao.sql").read_text(encoding="utf-8")


class MigracaoGestaoDesenvolvimento030Test(unittest.TestCase):
    def test_remove_os_dois_campos(self):
        self.assertIn("DROP COLUMN criterios_conclusao", SQL)
        self.assertIn("DROP COLUMN referencia", SQL)

    def test_preserva_coerencia_da_conclusao(self):
        self.assertIn("status_trabalho <> 'CONCLUIDO' OR concluido_em IS NOT NULL", SQL)


if __name__ == "__main__":
    unittest.main()
