"""Testes puros da identidade da origem histórica."""

from datetime import date, timedelta
import unittest

from msen.modelos import ResultadoEntrada
from msen.services import assinatura_resultados


def criar(numero: int, primeira: int = 1) -> ResultadoEntrada:
    return ResultadoEntrada.criar(
        data_resultado=date(2020, 1, 1) + timedelta(days=numero),
        numero_ap=numero,
        resultados=(primeira, 10, 20, 30, 40, 50),
    )


class CargaHistoricoFrequenciaTestCase(unittest.TestCase):
    def test_assinatura_e_deterministica(self) -> None:
        serie = (criar(1), criar(2), criar(3))
        self.assertEqual(assinatura_resultados(serie), assinatura_resultados(serie))
        self.assertEqual(64, len(assinatura_resultados(serie)))

    def test_alteracao_antiga_muda_assinatura(self) -> None:
        original = (criar(1), criar(2), criar(3))
        alterada = (criar(1), criar(2, primeira=2), criar(3))
        self.assertNotEqual(
            assinatura_resultados(original), assinatura_resultados(alterada)
        )

    def test_concurso_novo_muda_somente_assinatura_completa(self) -> None:
        prefixo = (criar(1), criar(2), criar(3))
        ampliada = prefixo + (criar(4),)
        self.assertEqual(
            assinatura_resultados(prefixo), assinatura_resultados(ampliada[:3])
        )
        self.assertNotEqual(
            assinatura_resultados(prefixo), assinatura_resultados(ampliada)
        )


if __name__ == "__main__":
    unittest.main()
