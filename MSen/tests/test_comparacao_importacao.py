import hashlib
import unittest
from dataclasses import replace
from pathlib import Path

from msen.importacao import (
    StatusImportacao,
    comparar_importacao_excel,
    ler_resultados_calculados_excel,
)


class ComparacaoImportacaoTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fixtures = Path(__file__).parent / "fixtures"
        cls.base = cls.fixtures / "base_existente.xlsx"
        cls.atualizada = cls.fixtures / "linha_existente_alterada.xlsx"
        cls.existentes = ler_resultados_calculados_excel(cls.base)

    def test_reimportar_mesmo_arquivo_nao_cria_novidades(self):
        comparacao = comparar_importacao_excel(self.base, self.existentes)
        self.assertEqual(2, len(comparacao.com_status(StatusImportacao.IGUAL)))
        self.assertEqual((), comparacao.com_status(StatusImportacao.NOVA))
        self.assertEqual((), comparacao.com_status(StatusImportacao.ALTERADA))
        self.assertEqual((), comparacao.com_status(StatusImportacao.INVALIDA))

    def test_arquivo_atualizado_retorna_somente_acrescimo_como_novo(self):
        comparacao = comparar_importacao_excel(self.atualizada, self.existentes)
        novas = comparacao.com_status(StatusImportacao.NOVA)
        self.assertEqual(1, len(novas))
        self.assertEqual(102, novas[0].numero_ap)

    def test_classifica_igual_alterado_e_novo_separadamente(self):
        comparacao = comparar_importacao_excel(self.atualizada, self.existentes)
        self.assertEqual([100], [item.numero_ap for item in comparacao.com_status(StatusImportacao.IGUAL)])
        self.assertEqual([101], [item.numero_ap for item in comparacao.com_status(StatusImportacao.ALTERADA)])
        self.assertEqual([102], [item.numero_ap for item in comparacao.com_status(StatusImportacao.NOVA)])

    def test_divergencia_antiga_preserva_as_duas_versoes(self):
        original = self.existentes[1]
        comparacao = comparar_importacao_excel(self.atualizada, self.existentes)
        alterada = comparacao.com_status(StatusImportacao.ALTERADA)[0]
        self.assertIs(original, alterada.existente)
        self.assertNotEqual(alterada.existente.resultados, alterada.importado.resultados)
        self.assertEqual((2, 11, 21, 31, 41, 59), original.resultados)

    def test_versao_de_calculo_diferente_nao_altera_dados_originais(self):
        existentes = tuple(replace(item, versao_calculo=2) for item in self.existentes)
        comparacao = comparar_importacao_excel(self.base, existentes)
        self.assertEqual(2, len(comparacao.com_status(StatusImportacao.IGUAL)))
        self.assertEqual((), comparacao.com_status(StatusImportacao.ALTERADA))

    def test_linha_com_conteudo_invalido_e_classificada_sem_impedir_as_validas(self):
        caminho = self.fixtures / "linha_invalida.xlsx"
        comparacao = comparar_importacao_excel(caminho, ())
        self.assertEqual([100], [item.numero_ap for item in comparacao.com_status(StatusImportacao.NOVA)])
        invalidas = comparacao.com_status(StatusImportacao.INVALIDA)
        self.assertEqual(1, len(invalidas))
        self.assertEqual(101, invalidas[0].numero_ap)
        self.assertEqual("LINHA_INVALIDA", invalidas[0].erro.codigo)

    def test_concurso_repetido_na_planilha_torna_as_duas_linhas_invalidas(self):
        caminho = self.fixtures / "linhas_repetidas.xlsx"
        comparacao = comparar_importacao_excel(caminho, ())
        invalidas = comparacao.com_status(StatusImportacao.INVALIDA)
        self.assertEqual(2, len(invalidas))
        self.assertTrue(all(
            item.erro.codigo == "NUMERO_AP_DUPLICADO_NA_PLANILHA" for item in invalidas
        ))

    def test_comparacao_nao_modifica_planilha_nem_existentes(self):
        hash_antes = hashlib.sha256(self.atualizada.read_bytes()).hexdigest()
        existentes_antes = tuple(self.existentes)
        comparar_importacao_excel(self.atualizada, self.existentes)
        hash_depois = hashlib.sha256(self.atualizada.read_bytes()).hexdigest()
        self.assertEqual(hash_antes, hash_depois)
        self.assertEqual(existentes_antes, self.existentes)


if __name__ == "__main__":
    unittest.main()
