from pathlib import Path
import unittest


MIGRACAO = (
    Path(__file__).parents[2]
    / "database"
    / "migrations"
    / "026_criar_formacao_final_jogos.sql"
)
AJUSTE_VALORES = (
    Path(__file__).parents[2]
    / "database"
    / "migrations"
    / "027_alargar_valores_formacao_jogos.sql"
)


class MigracaoFormacaoFinalJogosDDLTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.sql = MIGRACAO.read_text(encoding="utf-8")

    def test_cria_formacao_e_somente_jogos_finais(self) -> None:
        self.assertIn("CREATE TABLE formacoes_jogos_selecao", self.sql)
        self.assertIn("CREATE TABLE jogos_finais_selecao", self.sql)
        self.assertNotIn("combinações reprovadas", self.sql.lower())

    def test_guarda_configuracao_fotografia_totais_e_valores(self) -> None:
        for trecho in (
            "quantidade_jogos_solicitada", "valor_unitario",
            "valor_maximo_previsto", "fotografia_screener_json",
            "assinatura_screener", "versao_classificador",
            "assinatura_classificador", "quantidade_examinada",
            "quantidade_reprovada", "quantidade_aprovada",
            "quantidade_disponibilizada", "valor_efetivo",
        ):
            self.assertIn(trecho, self.sql)

    def test_protege_idempotencia_e_imutabilidade(self) -> None:
        self.assertIn("uk_formacao_jogos_idempotencia", self.sql)
        self.assertIn("proteger_configuracao_formacao_jogos", self.sql)
        self.assertIn("proteger_jogo_final_selecao", self.sql)

    def test_reconcilia_totais_e_limita_disponibilizados(self) -> None:
        self.assertIn(
            "quantidade_examinada = quantidade_reprovada + quantidade_aprovada",
            self.sql,
        )
        self.assertIn("LEAST(", self.sql)
        self.assertIn("quantidade_disponibilizada <= quantidade_jogos_solicitada", self.sql)

    def test_valores_calculados_comportam_os_limites_da_configuracao(self) -> None:
        ajuste = AJUSTE_VALORES.read_text(encoding="utf-8")
        self.assertIn("valor_maximo_previsto TYPE NUMERIC(24,2)", ajuste)
        self.assertIn("valor_efetivo TYPE NUMERIC(24,2)", ajuste)


if __name__ == "__main__":
    unittest.main()
