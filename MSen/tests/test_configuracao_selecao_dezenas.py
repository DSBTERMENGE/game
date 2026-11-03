from decimal import Decimal
import unittest

from msen.services.configuracao_selecao_dezenas import (
    ConfiguracaoSelecaoDezenas,
    configuracao_selecao_inicial,
)


class ConfiguracaoSelecaoDezenasTest(unittest.TestCase):
    def test_configuracao_inicial_obedece_ao_contrato(self) -> None:
        configuracao = configuracao_selecao_inicial()

        self.assertEqual(configuracao.fator_k, Decimal("1.000000"))
        self.assertEqual(configuracao.fator_j, Decimal("0.000000"))
        self.assertEqual(configuracao.modo_quantidade, "MAX")
        self.assertIsNone(configuracao.quantidade_dezenas)
        self.assertEqual(configuracao.horizonte_concursos, 1)
        self.assertRegex(configuracao.assinatura_sha256, r"^[0-9a-f]{64}$")

    def test_assinatura_e_deterministica_e_sensivel_a_configuracao(self) -> None:
        primeira = configuracao_selecao_inicial()
        repetida = configuracao_selecao_inicial()
        alterada = ConfiguracaoSelecaoDezenas(
            nome=primeira.nome,
            fator_k=Decimal("0.750000"),
            fator_j=Decimal("0.000000"),
            modo_quantidade="FIXA",
            quantidade_dezenas=12,
            horizonte_concursos=1,
            versao_calculo=1,
        )

        self.assertEqual(primeira.assinatura_sha256, repetida.assinatura_sha256)
        self.assertNotEqual(primeira.assinatura_sha256, alterada.assinatura_sha256)

    def test_rejeita_parametros_fora_do_contrato(self) -> None:
        base = dict(
            nome="Teste", fator_k=Decimal("0.5"), fator_j=Decimal("0"),
            modo_quantidade="MAX", quantidade_dezenas=None,
            horizonte_concursos=1, versao_calculo=1,
        )
        casos = (
            {"fator_k": Decimal("0")},
            {"fator_k": Decimal("1.1")},
            {"fator_j": Decimal("0.6")},
            {"modo_quantidade": "OUTRO"},
            {"quantidade_dezenas": 10},
            {"modo_quantidade": "FIXA", "quantidade_dezenas": 5},
            {"horizonte_concursos": 0},
            {"versao_calculo": 0},
        )
        for alteracoes in casos:
            with self.subTest(alteracoes=alteracoes), self.assertRaises(ValueError):
                ConfiguracaoSelecaoDezenas(**(base | alteracoes))


if __name__ == "__main__":
    unittest.main()
