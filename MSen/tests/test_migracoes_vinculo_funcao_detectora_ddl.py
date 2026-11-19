"""Testes estruturais das migrações 031 e 032."""

from pathlib import Path
import re
import unittest

from msen.database import descobrir_migracoes
from msen.padroes import criar_registro_detectores_aprovados


RAIZ = Path(__file__).resolve().parents[2]
MIGRACOES = RAIZ / "database" / "migrations"
ESQUEMA = RAIZ / "database" / "schema_postgresql.sql"
SQL_031 = (MIGRACOES / "031_adicionar_vinculo_funcao_detectora.sql").read_text(
    encoding="utf-8"
)
SQL_032 = (MIGRACOES / "032_vincular_funcoes_detectoras_existentes.sql").read_text(
    encoding="utf-8"
)


class MigracoesVinculoFuncaoDetectoraDDLTest(unittest.TestCase):
    def test_migracoes_estao_na_ordem_esperada(self):
        versoes = tuple(item.versao for item in descobrir_migracoes(MIGRACOES))
        self.assertEqual(("031", "032"), versoes[30:32])
        self.assertEqual("038", versoes[-1])

    def test_031_adiciona_colunas_e_integridade_relacional(self):
        for trecho in (
            "ADD COLUMN funcao_detectora VARCHAR(500)",
            "ADD COLUMN id_padrao BIGINT",
            "id_grupo, id_padrao",
            "UNIQUE (id_padrao)",
            "id_padrao IS NULL OR categoria = 'PADRAO'",
        ):
            with self.subTest(trecho=trecho):
                self.assertIn(trecho, SQL_031)

    def test_032_coincide_com_catalogo_python_aprovado(self):
        gravados = dict(re.findall(r"\('(PD_\d+)', '([^']+)'\)", SQL_032))
        registro = criar_registro_detectores_aprovados()
        catalogo = {
            codigo: (
                f"{registro.obter(codigo).__module__}."
                f"{registro.obter(codigo).__qualname__}"
            )
            for codigo in registro.codigos_registrados()
        }
        self.assertEqual(gravados, {codigo: catalogo[codigo] for codigo in gravados})
        self.assertIn("PD_011", catalogo)

    def test_032_aceita_catalogo_novo_vazio_mas_rejeita_estado_parcial(self):
        self.assertIn("total_criterios NOT IN (0, 9)", SQL_032)
        self.assertIn("quantidade <> total_criterios", SQL_032)

    def test_esquema_novo_contem_colunas_restricoes_e_funcoes(self):
        esquema = ESQUEMA.read_text(encoding="utf-8")
        for trecho in (
            "funcao_detectora VARCHAR(500)",
            "id_padrao BIGINT",
            "fk_criterios_validacao_padrao_grupo",
            "uk_criterios_validacao_id_padrao",
            "msen.padroes.sequenciais.detectar_duas_dezenas_sequenciais",
            "msen.padroes.mesma_linha.detectar_mais_de_tres_dezenas_na_mesma_linha",
        ):
            with self.subTest(trecho=trecho):
                self.assertIn(trecho, esquema)

    def test_esquema_declara_assinatura_regra_uma_unica_vez(self):
        esquema = ESQUEMA.read_text(encoding="utf-8")
        self.assertEqual(1, esquema.count("assinatura_regra CHAR(64) NOT NULL"))
        self.assertEqual(
            1, esquema.count("CONSTRAINT ck_criterios_validacao_assinatura_regra")
        )


if __name__ == "__main__":
    unittest.main()
