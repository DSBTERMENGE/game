import unittest
from pathlib import Path

from msen.database import descobrir_migracoes


RAIZ = Path(__file__).resolve().parents[2]
MIGRACOES = RAIZ / "database" / "migrations"
ESQUEMA = RAIZ / "database" / "schema_postgresql.sql"


class MigracaoAmostrasValidacaoDDLTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.caminho = MIGRACOES / "011_criar_amostras_validacao.sql"
        cls.sql = cls.caminho.read_text(encoding="utf-8")
        cls.esquema = ESQUEMA.read_text(encoding="utf-8")

    def test_011_antecede_a_012(self):
        migracoes = descobrir_migracoes(MIGRACOES)
        migracao_011 = next(item for item in migracoes if item.versao == "011")
        migracao_012 = next(item for item in migracoes if item.versao == "012")
        self.assertEqual(self.caminho, migracao_011.caminho)
        self.assertLess(migracoes.index(migracao_011), migracoes.index(migracao_012))

    def test_id_resultado_e_pk_fk_com_cascata(self):
        self.assertIn("id_resultado BIGINT PRIMARY KEY", self.sql)
        self.assertIn("REFERENCES resultados (id_resultado)", self.sql)
        self.assertIn("ON UPDATE RESTRICT ON DELETE CASCADE", self.sql)

    def test_ordem_ativa_e_data_possuem_restricoes(self):
        self.assertIn("ordem SMALLINT NOT NULL", self.sql)
        self.assertIn("UNIQUE (ordem)", self.sql)
        self.assertIn("CHECK (ordem > 0)", self.sql)
        self.assertIn("ativo BOOLEAN NOT NULL DEFAULT TRUE", self.sql)
        self.assertIn(
            "incluido_em TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP", self.sql
        )

    def test_nao_duplica_as_seis_dezenas(self):
        for coluna in ("res_01", "res_02", "res_03", "res_04", "res_05", "res_06"):
            with self.subTest(coluna=coluna):
                self.assertNotIn(coluna, self.sql)

    def test_esquema_consolidado_repete_o_contrato(self):
        trecho = self.esquema.split(
            "CREATE TABLE IF NOT EXISTS amostras_validacao", 1
        )[1].split(";", 1)[0]
        for elemento in (
            "id_resultado BIGINT PRIMARY KEY",
            "ordem SMALLINT NOT NULL",
            "ativo BOOLEAN NOT NULL DEFAULT TRUE",
            "REFERENCES resultados (id_resultado)",
            "ON UPDATE RESTRICT ON DELETE CASCADE",
        ):
            with self.subTest(elemento=elemento):
                self.assertIn(elemento, trecho)


if __name__ == "__main__":
    unittest.main()
