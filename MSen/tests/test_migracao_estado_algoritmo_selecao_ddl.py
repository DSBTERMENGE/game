import unittest
from pathlib import Path

from msen.database import descobrir_migracoes


RAIZ = Path(__file__).resolve().parents[2]
MIGRACOES = RAIZ / "database" / "migrations"
ESQUEMA = RAIZ / "database" / "schema_postgresql.sql"


class MigracaoEstadoAlgoritmoSelecaoDDLTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.caminho = MIGRACOES / "013_criar_estado_algoritmo_selecao.sql"
        cls.sql = cls.caminho.read_text(encoding="utf-8")
        cls.esquema = ESQUEMA.read_text(encoding="utf-8")

    def test_013_antecede_a_014(self):
        migracoes = descobrir_migracoes(MIGRACOES)
        migracao_013 = next(item for item in migracoes if item.versao == "013")
        migracao_014 = next(item for item in migracoes if item.versao == "014")
        self.assertEqual(self.caminho, migracao_013.caminho)
        self.assertLess(migracoes.index(migracao_013), migracoes.index(migracao_014))

    def test_cria_e_inicializa_linha_unica_desatualizada(self):
        self.assertIn("CREATE TABLE estado_algoritmo_selecao", self.sql)
        self.assertIn("CHECK (id_estado = 1)", self.sql)
        self.assertIn("atualizado BOOLEAN NOT NULL DEFAULT FALSE", self.sql)
        self.assertIn("VALUES (1)", self.sql)

    def test_guarda_evidencias_da_liberacao(self):
        for elemento in (
            "assinatura_catalogo_homologado CHAR(64)",
            "assinatura_conjunto_resultados CHAR(64)",
            "quantidade_resultados BIGINT",
            "homologado_em TIMESTAMPTZ",
            "perfis_atualizados_em TIMESTAMPTZ",
            "cobertura_confirmada_em TIMESTAMPTZ",
        ):
            with self.subTest(elemento=elemento):
                self.assertIn(elemento, self.sql)

    def test_estado_atualizado_exige_todas_as_evidencias(self):
        self.assertIn("ck_estado_algoritmo_atualizado_com_evidencias", self.sql)
        self.assertIn("NOT atualizado", self.sql)
        self.assertIn("assinatura_catalogo_homologado IS NOT NULL", self.sql)
        self.assertIn("assinatura_conjunto_resultados IS NOT NULL", self.sql)

    def test_protege_linha_contra_exclusao_e_troca_de_identidade(self):
        self.assertIn("CREATE FUNCTION proteger_estado_algoritmo_selecao()", self.sql)
        self.assertIn("IF TG_OP = 'DELETE'", self.sql)
        self.assertIn("IF NEW.id_estado <> OLD.id_estado", self.sql)
        self.assertIn("BEFORE UPDATE OR DELETE", self.sql)

    def test_esquema_consolidado_contem_o_estado(self):
        for elemento in (
            "CREATE TABLE IF NOT EXISTS estado_algoritmo_selecao",
            "CREATE OR REPLACE FUNCTION proteger_estado_algoritmo_selecao()",
            "ON CONFLICT (id_estado) DO NOTHING",
        ):
            with self.subTest(elemento=elemento):
                self.assertIn(elemento, self.esquema)


if __name__ == "__main__":
    unittest.main()
