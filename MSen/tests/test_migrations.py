import hashlib
import tempfile
import unittest
from pathlib import Path

from msen.database import ErroMigracao, descobrir_migracoes
from msen.database.migrations import _remover_transacao_explicita


class DescobertaMigracoesTestCase(unittest.TestCase):
    def setUp(self):
        self._temporario = tempfile.TemporaryDirectory()
        self.pasta = Path(self._temporario.name)

    def tearDown(self):
        self._temporario.cleanup()

    def _criar(self, nome: str, conteudo: str) -> Path:
        caminho = self.pasta / nome
        caminho.write_text(conteudo, encoding="utf-8")
        return caminho

    def test_ordena_por_versao_numerica(self):
        self._criar("010_decima.sql", "SELECT 10;")
        self._criar("002_segunda.sql", "SELECT 2;")
        self._criar("001_primeira.sql", "SELECT 1;")
        migracoes = descobrir_migracoes(self.pasta)
        self.assertEqual(("001", "002", "010"), tuple(m.versao for m in migracoes))

    def test_calcula_checksum_dos_bytes_originais(self):
        conteudo = "-- acentuação\nSELECT 1;\n"
        caminho = self._criar("001_inicio.sql", conteudo)
        migracao = descobrir_migracoes(self.pasta)[0]
        self.assertEqual(hashlib.sha256(caminho.read_bytes()).hexdigest(), migracao.checksum_sha256)

    def test_ignora_arquivos_fora_do_padrao(self):
        self._criar("README.md", "texto")
        self._criar("rascunho.sql", "SELECT 1;")
        self.assertEqual((), descobrir_migracoes(self.pasta))

    def test_rejeita_duas_migracoes_com_mesma_versao(self):
        self._criar("001_inicio.sql", "SELECT 1;")
        self._criar("001_repetida.sql", "SELECT 2;")
        with self.assertRaises(ErroMigracao) as contexto:
            descobrir_migracoes(self.pasta)
        self.assertEqual("VERSAO_DUPLICADA", contexto.exception.codigo)

    def test_rejeita_pasta_ausente(self):
        with self.assertRaises(ErroMigracao) as contexto:
            descobrir_migracoes(self.pasta / "ausente")
        self.assertEqual("PASTA_NAO_ENCONTRADA", contexto.exception.codigo)

    def test_remove_begin_commit_para_controle_transacional_python(self):
        sql = "-- comentário\nBEGIN;\nCREATE TABLE teste (id integer);\nCOMMIT;\n"
        tratado = _remover_transacao_explicita(sql, "001")
        self.assertNotIn("BEGIN;", tratado)
        self.assertNotIn("COMMIT;", tratado)
        self.assertIn("CREATE TABLE teste", tratado)

    def test_rejeita_transacao_explicita_incompleta(self):
        with self.assertRaises(ErroMigracao) as contexto:
            _remover_transacao_explicita("BEGIN;\nSELECT 1;", "001")
        self.assertEqual("TRANSACAO_EXPLICITA_INCOMPLETA", contexto.exception.codigo)

    def test_rejeita_migracao_vazia(self):
        with self.assertRaises(ErroMigracao) as contexto:
            _remover_transacao_explicita("-- somente comentário\n", "001")
        self.assertEqual("MIGRACAO_VAZIA", contexto.exception.codigo)


if __name__ == "__main__":
    unittest.main()
