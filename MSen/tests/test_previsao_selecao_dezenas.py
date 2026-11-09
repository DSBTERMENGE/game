from decimal import Decimal
import unittest

from msen.services import ConfiguracaoSelecaoDezenas


class ConfiguracaoAlvoUnicoPrevisaoTest(unittest.TestCase):
    def test_assinatura_nao_possui_horizonte(self) -> None:
        configuracao = ConfiguracaoSelecaoDezenas(
            nome="Previsão", fator_k=Decimal("1"), fator_j=Decimal("0"),
            modo_quantidade="MAX", quantidade_dezenas=None, versao_calculo=1,
        )
        self.assertNotIn("horizonte_concursos", configuracao.conteudo_assinavel())
        self.assertRegex(configuracao.assinatura_sha256, r"^[0-9a-f]{64}$")


if __name__ == "__main__":
    unittest.main()
