"""Testes da configuração reproduzível do estudo de frequências."""

from dataclasses import replace
from decimal import Decimal
import unittest

from msen.services import (
    ConfiguracaoFrequencia,
    comparar_configuracoes_frequencia,
    configuracao_frequencia_inicial,
)


class ConfiguracaoFrequenciaTestCase(unittest.TestCase):
    def test_configuracao_inicial_aprovada(self) -> None:
        config = configuracao_frequencia_inicial()
        self.assertEqual(1, config.concurso_inicial)
        self.assertEqual(500, config.tamanho_inicial)
        self.assertEqual("INICIO_FIXO_FINAL_EXPANSIVO", config.regra_janela)
        self.assertEqual("TODOS", config.tipo_evento)
        self.assertEqual(Decimal("1.000000"), config.parametro_faixa)
        self.assertEqual(64, len(config.assinatura_sha256))

    def test_assinatura_e_estavel_para_mesmo_conteudo(self) -> None:
        primeira = configuracao_frequencia_inicial()
        segunda = configuracao_frequencia_inicial()
        self.assertEqual(primeira.assinatura_sha256, segunda.assinatura_sha256)

    def test_cada_campo_relevante_altera_assinatura(self) -> None:
        base = configuracao_frequencia_inicial()
        alternativas = (
            replace(base, nome="Experiência B"),
            replace(base, concurso_inicial=2),
            replace(base, tamanho_inicial=600),
            replace(base, tipo_evento="SIMPLES"),
            replace(base, parametro_faixa=Decimal("2.000000")),
            replace(base, versao_calculo=2),
        )
        for alternativa in alternativas:
            with self.subTest(alternativa=alternativa):
                self.assertNotEqual(base.assinatura_sha256,
                                    alternativa.assinatura_sha256)

    def test_comparacao_informa_campos_e_valores_divergentes(self) -> None:
        gravada = configuracao_frequencia_inicial()
        calculada = replace(
            gravada, tamanho_inicial=700, tipo_evento="2VS",
            parametro_faixa=Decimal("1.500000"),
        )
        divergencias = comparar_configuracoes_frequencia(gravada, calculada)
        self.assertEqual(
            ("tamanho_inicial", "tipo_evento", "parametro_faixa"),
            tuple(item.campo for item in divergencias),
        )
        self.assertEqual(500, divergencias[0].valor_gravado)
        self.assertEqual(700, divergencias[0].valor_calculado)

    def test_configuracao_igual_nao_tem_divergencia(self) -> None:
        config = configuracao_frequencia_inicial()
        self.assertEqual((), comparar_configuracoes_frequencia(config, config))

    def test_nao_infere_unidade_nem_converte_float(self) -> None:
        base = configuracao_frequencia_inicial()
        with self.assertRaises(TypeError):
            replace(base, parametro_faixa=1.0)
        with self.assertRaises(ValueError):
            replace(base, unidade_parametro="PERCENTUAL")

    def test_rejeita_configuracao_ambigua_ou_invalida(self) -> None:
        base = configuracao_frequencia_inicial()
        casos = (
            {"nome": " "},
            {"concurso_inicial": 0},
            {"tamanho_inicial": True},
            {"regra_janela": "DESCONHECIDA"},
            {"tipo_evento": ""},
            {"metodo_faixa": "PERCENTUAL"},
            {"parametro_faixa": Decimal("0")},
            {"regra_arredondamento": "IMPLICITO"},
            {"versao_calculo": 0},
        )
        for alteracao in casos:
            with self.subTest(alteracao=alteracao), self.assertRaises((TypeError, ValueError)):
                replace(base, **alteracao)


if __name__ == "__main__":
    unittest.main()
