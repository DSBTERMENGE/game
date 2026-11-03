from pathlib import Path
import unittest


RAIZ = Path(__file__).resolve().parents[2]
MIGRACAO = RAIZ / "database/migrations/021_criar_pesquisas_selecao_dezenas.sql"
ESQUEMA = RAIZ / "database/schema_postgresql.sql"


class MigracaoPesquisaSelecaoDDLTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.migracao = MIGRACAO.read_text(encoding="utf-8")
        cls.esquema = ESQUEMA.read_text(encoding="utf-8")

    def test_cria_os_quatro_niveis_do_modelo(self) -> None:
        tabelas = (
            "configuracoes_pesquisa_selecao",
            "execucoes_pesquisa_selecao",
            "alvos_pesquisa_selecao",
            "avaliacoes_dezenas_pesquisa",
        )
        for tabela in tabelas:
            with self.subTest(tabela=tabela):
                trecho = f"CREATE TABLE {tabela}"
                self.assertIn(trecho, self.migracao)
                self.assertIn(trecho, self.esquema)

    def test_preserva_resultados_e_configuracoes_e_limita_cascata(self) -> None:
        self.assertIn("ON UPDATE RESTRICT ON DELETE RESTRICT", self.migracao)
        self.assertEqual(self.migracao.count("ON UPDATE RESTRICT ON DELETE CASCADE"), 2)
        self.assertIn("REFERENCES resultados (id_resultado)", self.migracao)
        for coluna in ("res_01", "res_02", "res_03", "res_04", "res_05", "res_06"):
            self.assertNotIn(coluna, self.migracao)

    def test_impede_alteracao_retroativa_da_configuracao(self) -> None:
        self.assertIn("proteger_configuracao_pesquisa_selecao", self.migracao)
        self.assertIn("CREATE TRIGGER tg_proteger_configuracao_pesquisa_selecao", self.migracao)
        self.assertIn("IS DISTINCT FROM", self.migracao)

    def test_contem_regras_de_quantidade_periodo_e_sessenta_dezenas(self) -> None:
        self.assertIn("modo_quantidade = 'MAX'", self.migracao)
        self.assertIn("modo_quantidade = 'FIXA'", self.migracao)
        self.assertIn("fator_j >= -fator_k AND fator_j <= fator_k", self.migracao)
        self.assertIn("concurso_alvo_inicial >= 500", self.migracao)
        self.assertIn("CHECK (dezena BETWEEN 1 AND 60)", self.migracao)
        self.assertIn("PRIMARY KEY (id_alvo_selecao, dezena)", self.migracao)

    def test_migracoes_possuem_versoes_unicas_e_022_e_a_ultima(self) -> None:
        versoes = sorted(
            int(arquivo.name.split("_", 1)[0])
            for arquivo in MIGRACAO.parent.glob("[0-9][0-9][0-9]_*.sql")
        )
        self.assertEqual(versoes[-1], 22)
        self.assertEqual(len(versoes), len(set(versoes)))


if __name__ == "__main__":
    unittest.main()
