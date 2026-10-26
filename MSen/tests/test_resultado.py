"""Testes do modelo e das validações de entrada de um resultado."""

from dataclasses import FrozenInstanceError
from datetime import date, datetime
import unittest

from msen.modelos import ErroValidacaoResultado, ResultadoEntrada


class ResultadoEntradaTestCase(unittest.TestCase):
    def assert_codigo_erro(self, codigo, funcao) -> ErroValidacaoResultado:
        with self.assertRaises(ErroValidacaoResultado) as contexto:
            funcao()
        self.assertEqual(contexto.exception.codigo, codigo)
        return contexto.exception

    def criar_valido(self, **alteracoes) -> ResultadoEntrada:
        dados = {
            "data_resultado": "11/10/2026",
            "numero_ap": 3069,
            "resultados": [47, 5, 22, 44, 57, 19],
        }
        dados.update(alteracoes)
        return ResultadoEntrada.criar(**dados)

    def test_cria_resultado_valido_e_preserva_ordem(self) -> None:
        resultado = self.criar_valido()

        self.assertEqual(resultado.data_resultado, date(2026, 10, 11))
        self.assertEqual(resultado.numero_ap, 3069)
        self.assertEqual(resultado.resultados, (47, 5, 22, 44, 57, 19))

    def test_aceita_data_ja_normalizada(self) -> None:
        resultado = self.criar_valido(data_resultado=date(2026, 10, 11))

        self.assertEqual(resultado.data_resultado, date(2026, 10, 11))

    def test_modelo_e_imutavel(self) -> None:
        resultado = self.criar_valido()

        with self.assertRaises(FrozenInstanceError):
            resultado.numero_ap = 1

    def test_rejeita_data_ausente(self) -> None:
        self.assert_codigo_erro(
            "DATA_AUSENTE", lambda: self.criar_valido(data_resultado=" ")
        )

    def test_rejeita_data_inexistente(self) -> None:
        self.assert_codigo_erro(
            "DATA_INVALIDA", lambda: self.criar_valido(data_resultado="31/02/2026")
        )

    def test_rejeita_data_em_formato_diferente(self) -> None:
        self.assert_codigo_erro(
            "DATA_INVALIDA", lambda: self.criar_valido(data_resultado="2026-10-11")
        )

    def test_rejeita_data_com_horario(self) -> None:
        self.assert_codigo_erro(
            "DATA_INVALIDA",
            lambda: self.criar_valido(
                data_resultado=datetime(2026, 10, 11, 12, 30)
            ),
        )

    def test_rejeita_numero_ap_ausente(self) -> None:
        self.assert_codigo_erro(
            "NUMERO_AP_AUSENTE", lambda: self.criar_valido(numero_ap=None)
        )

    def test_rejeita_numero_ap_nao_inteiro_ou_nao_positivo(self) -> None:
        for valor in (0, -1, 1.5, "3069", True):
            with self.subTest(valor=valor):
                self.assert_codigo_erro(
                    "NUMERO_AP_INVALIDO",
                    lambda valor=valor: self.criar_valido(numero_ap=valor),
                )

    def test_rejeita_quantidade_diferente_de_seis(self) -> None:
        for valores in (
            None,
            123456,
            [1, 2, 3, 4, 5],
            [1, 2, 3, 4, 5, 6, 7],
            "123456",
        ):
            with self.subTest(valores=valores):
                self.assert_codigo_erro(
                    "QUANTIDADE_RESULTADOS_INVALIDA",
                    lambda valores=valores: self.criar_valido(resultados=valores),
                )

    def test_rejeita_resultado_ausente_e_identifica_campo(self) -> None:
        erro = self.assert_codigo_erro(
            "RESULTADO_AUSENTE",
            lambda: self.criar_valido(resultados=[1, 2, None, 4, 5, 6]),
        )

        self.assertEqual(erro.campo, "res_03")

    def test_rejeita_resultado_nao_inteiro(self) -> None:
        for valor in (5.0, "5", True):
            with self.subTest(valor=valor):
                erro = self.assert_codigo_erro(
                    "RESULTADO_NAO_INTEIRO",
                    lambda valor=valor: self.criar_valido(
                        resultados=[1, 2, valor, 4, 5, 6]
                    ),
                )
                self.assertEqual(erro.campo, "res_03")

    def test_rejeita_resultado_fora_do_intervalo(self) -> None:
        for valor in (0, 61):
            with self.subTest(valor=valor):
                self.assert_codigo_erro(
                    "RESULTADO_FORA_INTERVALO",
                    lambda valor=valor: self.criar_valido(
                        resultados=[1, 2, valor, 4, 5, 6]
                    ),
                )

    def test_aceita_os_limites_1_e_60(self) -> None:
        resultado = self.criar_valido(resultados=[1, 2, 3, 4, 5, 60])

        self.assertEqual(resultado.resultados, (1, 2, 3, 4, 5, 60))

    def test_rejeita_resultado_repetido_e_informa_numero(self) -> None:
        erro = self.assert_codigo_erro(
            "RESULTADO_REPETIDO",
            lambda: self.criar_valido(resultados=[1, 2, 3, 2, 5, 6]),
        )

        self.assertEqual(erro.valor, (2,))


if __name__ == "__main__":
    unittest.main()
