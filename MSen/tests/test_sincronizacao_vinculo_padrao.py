"""Testes da resolução direta de padrão durante a sincronização."""

import unittest

from msen.padroes import detectar_duas_dezenas_sequenciais
from msen.services.sincronizacao_validacao import _resolver_id_padrao
from msen.validacao import DefinicaoCriterio


def definicao_padrao():
    return DefinicaoCriterio(
        "PAD_TESTE", "Teste", "PADRAO",
        detectar_duas_dezenas_sequenciais, "PADRAO", "Regra de teste.",
        grupo_codigo="PG_001",
    )


class SincronizacaoVinculoPadraoTest(unittest.TestCase):
    def setUp(self):
        self.definicao = definicao_padrao()
        self.funcao = self.definicao.funcao_python

    def test_preserva_id_direto_quando_grupo_e_funcao_coincidem(self):
        self.assertEqual(
            10,
            _resolver_id_padrao(self.definicao, 1, 10, {10: (1, self.funcao)}),
        )

    def test_encontra_vinculo_unico_para_cadastro_inicial(self):
        self.assertEqual(
            10,
            _resolver_id_padrao(self.definicao, 1, None, {10: (1, self.funcao)}),
        )

    def test_rejeita_vinculo_direto_divergente(self):
        with self.assertRaisesRegex(ValueError, "vínculo direto"):
            _resolver_id_padrao(self.definicao, 1, 10, {10: (2, self.funcao)})

    def test_rejeita_funcao_ambigua_no_mesmo_grupo(self):
        with self.assertRaisesRegex(ValueError, "padrão inequívoco"):
            _resolver_id_padrao(
                self.definicao, 1, None,
                {10: (1, self.funcao), 11: (1, self.funcao)},
            )

    def test_criterio_numerico_nao_recebe_id_padrao(self):
        numerico = DefinicaoCriterio(
            "EST_TESTE", "Teste", "ESTATISTICA", sum, "INTEIRO", "Regra."
        )
        self.assertIsNone(_resolver_id_padrao(numerico, None, None, {}))


if __name__ == "__main__":
    unittest.main()
