import unittest
from pathlib import Path

from msen.database import descobrir_migracoes


RAIZ = Path(__file__).resolve().parents[2]
MIGRACOES = RAIZ / "database" / "migrations"
ESQUEMA = RAIZ / "database" / "schema_postgresql.sql"


class MigracaoCatalogoAvaliacoesValidacaoDDLTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.caminho = MIGRACOES / "012_criar_catalogo_avaliacoes_validacao.sql"
        cls.sql = cls.caminho.read_text(encoding="utf-8")
        cls.esquema = ESQUEMA.read_text(encoding="utf-8")

    def test_012_antecede_a_013(self):
        migracoes = descobrir_migracoes(MIGRACOES)
        migracao_012 = next(item for item in migracoes if item.versao == "012")
        migracao_013 = next(item for item in migracoes if item.versao == "013")
        self.assertEqual(self.caminho, migracao_012.caminho)
        self.assertLess(migracoes.index(migracao_012), migracoes.index(migracao_013))

    def test_cria_catalogo_e_avaliacoes(self):
        self.assertIn("CREATE TABLE criterios_validacao", self.sql)
        self.assertIn("CREATE TABLE avaliacoes_validacao", self.sql)
        self.assertIn(
            "PRIMARY KEY (id_resultado, id_criterio)", self.sql
        )

    def test_catalogo_restringe_categoria_tipo_assinatura_e_estado(self):
        for elemento in (
            "ESTATISTICA', 'GEOMETRIA', 'PADRAO",
            "INTEIRO', 'DECIMAL', 'PADRAO",
            "assinatura_funcao ~ '^[0-9a-f]{64}$'",
            "PENDENTE', 'APROVADO', 'REPROVADO",
            "REFERENCES padroes_grupo (id_grupo)",
        ):
            with self.subTest(elemento=elemento):
                self.assertIn(elemento, self.sql)

    def test_avaliacao_relaciona_amostra_criterio_grupo_e_subgrupos(self):
        for elemento in (
            "REFERENCES amostras_validacao (id_resultado)",
            "REFERENCES criterios_validacao (id_criterio)",
            "REFERENCES criterios_validacao (id_criterio, id_grupo)",
            "FOREIGN KEY (id_grupo, id_padrao_esperado)",
            "FOREIGN KEY (id_grupo, id_padrao_calculado)",
            "REFERENCES padroes_subgrupo (id_grupo, id_padrao)",
        ):
            with self.subTest(elemento=elemento):
                self.assertIn(elemento, self.sql)

    def test_pendente_aprovado_e_sem_correspondencia_sao_distintos(self):
        self.assertIn("aprovado IS NULL OR aprovado IN ('S', 'N')", self.sql)
        self.assertIn("PADRAO_IDENTIFICADO', 'SEM_CORRESPONDENCIA", self.sql)
        self.assertIn("NOT referencia_conferida", self.sql)
        self.assertIn("NOT executado", self.sql)

    def test_esquema_consolidado_contem_as_duas_tabelas(self):
        for elemento in (
            "CREATE TABLE IF NOT EXISTS criterios_validacao",
            "CREATE TABLE IF NOT EXISTS avaliacoes_validacao",
            "ix_avaliacoes_validacao_criterio_aprovado",
        ):
            with self.subTest(elemento=elemento):
                self.assertIn(elemento, self.esquema)


if __name__ == "__main__":
    unittest.main()
