import unittest
from pathlib import Path

from msen.database import descobrir_migracoes


RAIZ_PROJETO = Path(__file__).resolve().parents[2]
PASTA_MIGRACOES = RAIZ_PROJETO / "database" / "migrations"
ESQUEMA_CONSOLIDADO = RAIZ_PROJETO / "database" / "schema_postgresql.sql"


class MigracaoClassificacaoPadraoDDLTestCase(unittest.TestCase):
    """Valida estaticamente o contrato estrutural da migração 008."""

    @classmethod
    def setUpClass(cls):
        cls.migracao = PASTA_MIGRACOES / "008_criar_classificacao_resultado_padrao.sql"
        cls.sql = cls.migracao.read_text(encoding="utf-8")
        cls.esquema = ESQUEMA_CONSOLIDADO.read_text(encoding="utf-8")

    def test_migracao_008_e_descoberta_antes_da_009(self):
        migracoes = descobrir_migracoes(PASTA_MIGRACOES)
        migracao_008 = next(item for item in migracoes if item.versao == "008")
        self.assertEqual(self.migracao, migracao_008.caminho)
        self.assertLess(
            migracoes.index(migracao_008),
            next(i for i, item in enumerate(migracoes) if item.versao == "009"),
        )

    def test_tabela_tem_unicidade_versao_e_data(self):
        self.assertIn("CREATE TABLE resultado_classificacao_padrao", self.sql)
        self.assertIn("UNIQUE (id_resultado, id_grupo)", self.sql)
        self.assertIn("versao_calculo SMALLINT NOT NULL DEFAULT 1", self.sql)
        self.assertIn("calculado_em TIMESTAMPTZ NOT NULL", self.sql)

    def test_chaves_cobrem_resultado_grupo_e_padrao_do_grupo(self):
        self.assertIn("REFERENCES resultados (id_resultado)", self.sql)
        self.assertIn("REFERENCES padroes_grupo (id_grupo)", self.sql)
        self.assertIn("REFERENCES padroes_subgrupo (id_grupo, id_padrao)", self.sql)

    def test_estado_exige_padrao_ou_sem_correspondencia(self):
        self.assertIn("estado_classificacao = 'PADRAO_IDENTIFICADO'", self.sql)
        self.assertIn("estado_classificacao = 'SEM_CORRESPONDENCIA'", self.sql)
        self.assertIn("AND id_padrao IS NOT NULL", self.sql)
        self.assertIn("AND id_padrao IS NULL", self.sql)

    def test_esquema_consolidado_contem_contrato_essencial(self):
        for elemento in (
            "CREATE TABLE IF NOT EXISTS resultado_classificacao_padrao",
            "UNIQUE (id_resultado, id_grupo)",
            "REFERENCES padroes_subgrupo (id_grupo, id_padrao)",
            "ix_resultado_classificacao_grupo_padrao",
        ):
            with self.subTest(elemento=elemento):
                self.assertIn(elemento, self.esquema)


if __name__ == "__main__":
    unittest.main()
