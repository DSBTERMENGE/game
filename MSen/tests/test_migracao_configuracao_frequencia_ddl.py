"""Contrato estrutural da migração 018."""

from pathlib import Path
import unittest

from msen.database import descobrir_migracoes
from msen.services import configuracao_frequencia_inicial


RAIZ = Path(__file__).resolve().parents[2]
MIGRACOES = RAIZ / "database" / "migrations"
MIGRACAO = MIGRACOES / "018_criar_configuracao_frequencia_dezenas.sql"
ESQUEMA = RAIZ / "database" / "schema_postgresql.sql"


class MigracaoConfiguracaoFrequenciaDDLTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.sql = MIGRACAO.read_text(encoding="utf-8")
        cls.esquema = ESQUEMA.read_text(encoding="utf-8")

    def test_018_permanece_na_sequencia(self) -> None:
        versoes = tuple(item.versao for item in descobrir_migracoes(MIGRACOES))
        self.assertIn("018", versoes)
        self.assertEqual("020", versoes[-1])

    def test_campos_e_unidades_sao_explicitos(self) -> None:
        for campo in (
            "concurso_inicial", "tamanho_inicial", "regra_janela",
            "tipo_evento", "metodo_faixa", "parametro_faixa",
            "unidade_parametro", "regra_arredondamento", "versao_calculo",
            "assinatura_sha256",
        ):
            with self.subTest(campo=campo):
                self.assertIn(campo, self.sql)
                self.assertIn(campo, self.esquema)

    def test_semente_corresponde_a_assinatura_python(self) -> None:
        assinatura = configuracao_frequencia_inicial().assinatura_sha256
        self.assertIn(assinatura, self.sql)
        self.assertIn(assinatura, self.esquema)

    def test_linha_unica_e_protegida(self) -> None:
        self.assertIn("CHECK (id_configuracao = 1)", self.sql)
        self.assertIn("BEFORE UPDATE OR DELETE", self.sql)
        self.assertIn("não pode ser excluída", self.sql)


if __name__ == "__main__":
    unittest.main()
