from pathlib import Path
import unittest


RAIZ = Path(__file__).resolve().parents[2]
SQL = (RAIZ / "database/migrations/038_criar_resultados_teste.sql").read_text(
    encoding="utf-8"
)


class TestMigracaoResultadosTesteDDL(unittest.TestCase):
    def test_cria_somente_identificador_e_seis_dezenas(self):
        self.assertIn("CREATE TABLE resultados_teste", SQL)
        self.assertIn("id_resultado_teste BIGINT GENERATED ALWAYS AS IDENTITY", SQL)
        for posicao in range(1, 7):
            self.assertIn(f"res_{posicao:02d} SMALLINT NOT NULL", SQL)
        for campo_proibido in ("criado_em", "versao", "assinatura"):
            self.assertNotIn(campo_proibido, SQL.lower())

    def test_valida_intervalos_e_dezenas_distintas(self):
        for posicao in range(1, 7):
            self.assertIn(f"res_{posicao:02d} BETWEEN 1 AND 60", SQL)
        comparacoes = [
            f"res_{primeira:02d} <> res_{segunda:02d}"
            for primeira in range(1, 7)
            for segunda in range(primeira + 1, 7)
        ]
        self.assertEqual(15, len(comparacoes))
        for comparacao in comparacoes:
            self.assertIn(comparacao, SQL)

    def test_preserva_ordem_e_nao_cria_unicidade_da_combinacao(self):
        self.assertIn("Primeira dezena na ordem gerada", SQL)
        self.assertNotIn("UNIQUE (", SQL.upper())
        self.assertNotIn("ORDER BY", SQL.upper())


if __name__ == "__main__":
    unittest.main()
