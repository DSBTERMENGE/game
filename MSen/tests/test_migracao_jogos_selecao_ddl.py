from pathlib import Path
import unittest


RAIZ = Path(__file__).resolve().parents[2]
MIGRACAO = RAIZ / "database/migrations/022_criar_jogos_selecao_dezenas.sql"
ESQUEMA = RAIZ / "database/schema_postgresql.sql"


class MigracaoJogosSelecaoDDLTest(unittest.TestCase):
    def test_cria_lotes_e_jogos_no_script_e_esquema(self) -> None:
        migracao = MIGRACAO.read_text(encoding="utf-8")
        esquema = ESQUEMA.read_text(encoding="utf-8")
        for tabela in ("lotes_jogos_selecao", "jogos_selecao_dezenas"):
            trecho = f"CREATE TABLE {tabela}"
            self.assertIn(trecho, migracao)
            self.assertIn(trecho, esquema)

    def test_vincula_lote_ao_alvo_e_ordena_as_seis_dezenas(self) -> None:
        migracao = MIGRACAO.read_text(encoding="utf-8")
        self.assertIn("REFERENCES alvos_pesquisa_selecao", migracao)
        self.assertIn("ON UPDATE RESTRICT ON DELETE CASCADE", migracao)
        self.assertIn("dezena_1 < dezena_2", migracao)
        self.assertIn("dezena_5 < dezena_6", migracao)
        self.assertIn("UNIQUE (", migracao)


if __name__ == "__main__":
    unittest.main()
