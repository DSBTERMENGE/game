"""Contrato estrutural da migração 019."""

from pathlib import Path
import unittest

from msen.database import descobrir_migracoes


RAIZ = Path(__file__).resolve().parents[2]
MIGRACOES = RAIZ / "database" / "migrations"
MIGRACAO = MIGRACOES / "019_criar_historico_frequencia_dezenas.sql"
ESQUEMA = RAIZ / "database" / "schema_postgresql.sql"


class MigracaoHistoricoFrequenciaDDLTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.sql = MIGRACAO.read_text(encoding="utf-8")
        cls.esquema = ESQUEMA.read_text(encoding="utf-8")

    def test_019_permanece_na_sequencia(self) -> None:
        versoes = tuple(item.versao for item in descobrir_migracoes(MIGRACOES))
        self.assertIn("019", versoes)
        self.assertEqual("020", versoes[-1])

    def test_normaliza_geracao_concurso_dezena_e_evento(self) -> None:
        for trecho in (
            "CREATE TABLE geracoes_frequencia_dezenas",
            "CREATE TABLE historico_frequencia_dezenas",
            "id_geracao, numero_do_concurso, dezena, tipo_evento",
            "tipo_evento IN ('SIMPLES', '2VS', '3VS')",
            "ON DELETE CASCADE",
        ):
            with self.subTest(trecho=trecho):
                self.assertIn(trecho, self.sql)

    def test_nao_repete_as_seis_dezenas_dos_resultados(self) -> None:
        for coluna in ("res_01", "res_02", "res_03", "res_04", "res_05", "res_06"):
            self.assertNotIn(coluna, self.sql)

    def test_preserva_configuracao_e_precisao(self) -> None:
        self.assertIn("configuracao_json JSONB NOT NULL", self.sql)
        self.assertIn("assinatura_configuracao CHAR(64) NOT NULL", self.sql)
        self.assertGreaterEqual(self.sql.count("NUMERIC(18,6)"), 6)

    def test_estado_sem_base_exige_nulos(self) -> None:
        self.assertIn("quantidade_intervalos = 0", self.sql)
        self.assertIn("previsao_central IS NULL", self.sql)
        self.assertIn("concurso_limite_superior IS NULL", self.sql)

    def test_indices_atendem_grafico_e_concurso(self) -> None:
        self.assertIn("ix_historico_frequencia_grafico", self.sql)
        self.assertIn("id_geracao, dezena, tipo_evento, numero_do_concurso", self.sql)
        self.assertIn("ix_historico_frequencia_concurso", self.sql)

    def test_esquema_consolidado_contem_as_duas_tabelas(self) -> None:
        self.assertIn("geracoes_frequencia_dezenas", self.esquema)
        self.assertIn("historico_frequencia_dezenas", self.esquema)


if __name__ == "__main__":
    unittest.main()
