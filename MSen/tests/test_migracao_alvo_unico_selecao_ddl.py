from pathlib import Path
import unittest


RAIZ = Path(__file__).resolve().parents[2]
MIGRACAO = RAIZ / "database/migrations/023_remover_horizonte_selecao_dezenas.sql"
ESQUEMA = RAIZ / "database/schema_postgresql.sql"


class MigracaoAlvoUnicoSelecaoDDLTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.migracao = MIGRACAO.read_text(encoding="utf-8")
        cls.esquema = ESQUEMA.read_text(encoding="utf-8")

    def test_remove_horizonte_e_versiona_assinatura(self) -> None:
        self.assertIn("DROP COLUMN horizonte_concursos", self.migracao)
        self.assertIn("versao_assinatura", self.migracao)
        self.assertNotIn("horizonte_concursos SMALLINT", self.esquema)
        self.assertIn("versao_assinatura SMALLINT NOT NULL DEFAULT 2", self.esquema)

    def test_preserva_legadas_como_arquivadas(self) -> None:
        self.assertIn("SET versao_assinatura = 1", self.migracao)
        self.assertIn("estado = 'ARQUIVADA'", self.migracao)
        self.assertIn("arquivada_em = COALESCE", self.migracao)

    def test_atualiza_protecao_de_imutabilidade(self) -> None:
        self.assertIn("CREATE OR REPLACE FUNCTION proteger_configuracao", self.migracao)
        self.assertIn("NEW.versao_assinatura", self.migracao)
        self.assertNotIn("NEW.horizonte_concursos", self.migracao)


if __name__ == "__main__":
    unittest.main()
