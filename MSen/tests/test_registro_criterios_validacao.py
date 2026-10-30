import re
import unittest

from msen.validacao import (
    DefinicaoCriterio,
    RegistroCriteriosValidacao,
    criar_registro_criterios_producao,
)


def funcao_exemplo(valor):
    return valor


class RegistroCriteriosValidacaoTestCase(unittest.TestCase):
    def test_registro_de_producao_cobre_as_tres_categorias(self):
        definicoes = criar_registro_criterios_producao().listar()
        self.assertEqual(19, len(definicoes))
        self.assertEqual(
            {"ESTATISTICA", "GEOMETRIA", "PADRAO"},
            {item.categoria for item in definicoes},
        )
        self.assertEqual(9, sum(item.categoria == "PADRAO" for item in definicoes))

    def test_nomes_estatisticos_identificam_as_grandezas_calculadas(self):
        definicoes = criar_registro_criterios_producao().listar()
        self.assertEqual(
            {
                "EST_SOMA": "Soma das seis dezenas",
                "EST_MEDIA": "Média aritmética das seis dezenas",
                "EST_MEDIANA": "Mediana das seis dezenas",
                "EST_DESVIO_PADRAO": (
                    "Desvio-padrão das seis dezenas em relação à média "
                    "das dezenas"
                ),
            },
            {
                item.codigo: item.nome
                for item in definicoes
                if item.categoria == "ESTATISTICA"
            },
        )

    def test_assinaturas_sao_sha256_estaveis_e_separadas(self):
        primeira = DefinicaoCriterio(
            "TESTE", "Teste", "ESTATISTICA", funcao_exemplo,
            "INTEIRO", "Regra A",
        )
        mesma = DefinicaoCriterio(
            "TESTE", "Outro nome", "ESTATISTICA", funcao_exemplo,
            "INTEIRO", "Regra A",
        )
        outra_regra = DefinicaoCriterio(
            "TESTE", "Teste", "ESTATISTICA", funcao_exemplo,
            "INTEIRO", "Regra B",
        )
        self.assertRegex(primeira.assinatura_funcao, re.compile("^[0-9a-f]{64}$"))
        self.assertEqual(primeira.assinatura_funcao, mesma.assinatura_funcao)
        self.assertEqual(primeira.assinatura_regra, mesma.assinatura_regra)
        self.assertNotEqual(primeira.assinatura_regra, outra_regra.assinatura_regra)

    def test_rejeita_codigo_duplicado(self):
        definicao = DefinicaoCriterio(
            "TESTE", "Teste", "ESTATISTICA", funcao_exemplo,
            "INTEIRO", "Regra",
        )
        with self.assertRaises(ValueError):
            RegistroCriteriosValidacao((definicao, definicao))


if __name__ == "__main__":
    unittest.main()
