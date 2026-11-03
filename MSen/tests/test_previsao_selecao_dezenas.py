from decimal import Decimal
import unittest

from msen.services import ConfiguracaoSelecaoDezenas


class ConfiguracaoHorizontePrevisaoTest(unittest.TestCase):
    def test_horizonte_faz_parte_da_assinatura(self) -> None:
        comum = dict(
            nome="Previsão", fator_k=Decimal("1"), fator_j=Decimal("0"),
            modo_quantidade="MAX", quantidade_dezenas=None, versao_calculo=1,
        )
        primeira = ConfiguracaoSelecaoDezenas(horizonte_concursos=1, **comum)
        terceira = ConfiguracaoSelecaoDezenas(horizonte_concursos=3, **comum)
        self.assertNotEqual(primeira.assinatura_sha256, terceira.assinatura_sha256)


if __name__ == "__main__":
    unittest.main()
