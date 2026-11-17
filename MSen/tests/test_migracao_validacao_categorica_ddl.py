"""Testes estruturais da migração categórica ainda não aplicada."""

from pathlib import Path
import unittest

from msen.database import descobrir_migracoes


RAIZ = Path(__file__).resolve().parents[2]
MIGRACOES = RAIZ / "database" / "migrations"
ARQUIVO = MIGRACOES / "035_adicionar_validacao_categorica.sql"
SQL = ARQUIVO.read_text(encoding="utf-8")


class MigracaoValidacaoCategoricaDDLTestCase(unittest.TestCase):
    def test_035_e_a_ultima_migracao_descoberta(self) -> None:
        migracoes = descobrir_migracoes(MIGRACOES)

        self.assertEqual("035", migracoes[-1].versao)
        self.assertEqual(ARQUIVO, migracoes[-1].caminho)

    def test_amplia_tipo_sem_remover_os_tipos_existentes(self) -> None:
        self.assertIn(
            "tipo_resultado IN ('INTEIRO', 'DECIMAL', 'PADRAO', 'CATEGORICO')",
            SQL,
        )
        self.assertIn("tipo_resultado IN ('PADRAO', 'CATEGORICO')", SQL)
        self.assertIn("tipo_resultado <> 'CATEGORICO' OR id_padrao IS NULL", SQL)

    def test_adiciona_respostas_categoricas_separadas(self) -> None:
        self.assertIn("ADD COLUMN categoria_esperada VARCHAR(200)", SQL)
        self.assertIn("ADD COLUMN categoria_calculada VARCHAR(200)", SQL)
        self.assertIn("categoria_esperada IS NOT NULL", SQL)
        self.assertIn("BTRIM(categoria_esperada) <> ''", SQL)
        self.assertIn("categoria_calculada IS NOT NULL", SQL)
        self.assertIn("BTRIM(categoria_calculada) <> ''", SQL)

    def test_preserva_modos_numerico_e_padrao_booleano(self) -> None:
        for trecho in (
            "estado_valor_esperado IS NULL",
            "estado_padrao_esperado IN (",
            "'PADRAO_IDENTIFICADO', 'SEM_CORRESPONDENCIA'",
            "id_padrao_esperado IS NOT NULL",
            "diferenca IS NULL",
        ):
            with self.subTest(trecho=trecho):
                self.assertIn(trecho, SQL)

    def test_migracao_e_estrutural_e_transacional(self) -> None:
        self.assertIn("BEGIN;", SQL)
        self.assertIn("COMMIT;", SQL)
        self.assertNotIn("INSERT INTO", SQL.upper())
        self.assertNotIn("DELETE FROM", SQL.upper())


if __name__ == "__main__":
    unittest.main()
