from decimal import Decimal
import unittest

from msen.services import ConfiguracaoFormacaoJogos, ErroConfiguracaoFormacaoJogos


ASSINATURA_SCREENER = "a" * 64
ASSINATURA_CLASSIFICADOR = "b" * 64


def criar(**alteracoes) -> ConfiguracaoFormacaoJogos:
    dados = {
        "id_alvo_selecao": 2571,
        "quantidade_dezenas": 16,
        "quantidade_combinacoes_brutas": 8008,
        "quantidade_jogos_solicitada": 100,
        "valor_unitario": "5.00",
        "assinatura_screener": ASSINATURA_SCREENER,
        "versao_classificador": 1,
        "assinatura_classificador": ASSINATURA_CLASSIFICADOR,
    }
    dados.update(alteracoes)
    return ConfiguracaoFormacaoJogos.criar(**dados)


class ConfiguracaoFormacaoJogosTest(unittest.TestCase):
    def test_calcula_valor_maximo_com_decimal_exato(self) -> None:
        configuracao = criar()
        self.assertEqual(Decimal("5.00"), configuracao.valor_unitario)
        self.assertEqual(Decimal("500.00"), configuracao.valor_maximo_previsto)

    def test_chave_e_reproduzivel_e_muda_com_a_configuracao(self) -> None:
        primeira = criar()
        self.assertEqual(primeira.chave_idempotencia, criar().chave_idempotencia)
        self.assertNotEqual(
            primeira.chave_idempotencia,
            criar(quantidade_jogos_solicitada=101).chave_idempotencia,
        )
        self.assertNotEqual(
            primeira.chave_idempotencia,
            criar(assinatura_screener="c" * 64).chave_idempotencia,
        )

    def test_rejeita_arredondamento_implicito_e_valores_invalidos(self) -> None:
        for valor in ("0", "5.001", "NaN", "infinito"):
            with self.subTest(valor=valor), self.assertRaises(ErroConfiguracaoFormacaoJogos):
                criar(valor_unitario=valor)

    def test_rejeita_identidades_e_assinaturas_invalidas(self) -> None:
        casos = (
            {"id_alvo_selecao": 0},
            {"quantidade_dezenas": 5},
            {"quantidade_jogos_solicitada": 50_063_861},
            {"assinatura_screener": "A" * 64},
            {"versao_classificador": 0},
        )
        for alteracoes in casos:
            with self.subTest(alteracoes=alteracoes), self.assertRaises(ErroConfiguracaoFormacaoJogos):
                criar(**alteracoes)


if __name__ == "__main__":
    unittest.main()
