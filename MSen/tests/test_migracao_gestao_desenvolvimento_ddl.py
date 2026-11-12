from pathlib import Path
import unittest


class MigracaoGestaoDesenvolvimentoDDLTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sql = (Path(__file__).parents[2] / "database" / "migrations" /
                   "028_criar_gestao_desenvolvimento.sql").read_text(encoding="utf-8")

    def test_cria_registros_e_historico(self):
        self.assertIn("CREATE TABLE manutencao_sistema (", self.sql)
        self.assertIn("CREATE TABLE manutencao_sistema_historico (", self.sql)
        self.assertIn("GENERATED ALWAYS AS IDENTITY", self.sql)

    def test_historico_e_imutavel(self):
        self.assertIn("BEFORE UPDATE OR DELETE ON manutencao_sistema_historico", self.sql)
        self.assertIn("ON DELETE RESTRICT", self.sql)

    def test_possui_idempotencia_versao_e_arquivamento(self):
        self.assertIn("chave_idempotencia", self.sql)
        self.assertIn("uk_manutencao_idempotencia UNIQUE", self.sql)
        self.assertIn("versao_registro", self.sql)
        self.assertIn("arquivado_em", self.sql)

    def test_nome_do_inicio_corresponde_ao_repositorio(self):
        repositorio = (
            Path(__file__).parents[1]
            / "src" / "msen" / "database"
            / "gestao_desenvolvimento_repository.py"
        ).read_text(encoding="utf-8")
        self.assertIn('valores["iniciado_em"]', repositorio)
        self.assertNotIn('valores["iniciada_em"]', repositorio)
        self.assertIn('valores["concluido_em"]', repositorio)
        self.assertNotIn('valores["concluida_em"]', repositorio)


if __name__ == "__main__":
    unittest.main()
