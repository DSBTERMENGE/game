"""Testes das frequências e dos intervalos entre ocorrências."""

from datetime import date, timedelta
from decimal import Decimal
import unittest

from msen.calculos import ErroAnaliseHistorica, calcular_frequencias
from msen.modelos import ResultadoEntrada


def criar_resultado(numero_ap: int, valores, *, dia: int | None = None):
    data_base = date(2026, 1, 1)
    return ResultadoEntrada.criar(
        data_resultado=data_base + timedelta(days=dia if dia is not None else numero_ap),
        numero_ap=numero_ap,
        resultados=valores,
    )


class FrequenciasTestCase(unittest.TestCase):
    def assert_codigo_erro(self, codigo, funcao) -> ErroAnaliseHistorica:
        with self.assertRaises(ErroAnaliseHistorica) as contexto:
            funcao()
        self.assertEqual(contexto.exception.codigo, codigo)
        return contexto.exception

    def test_historico_vazio_retorna_sessenta_dezenas_zeradas(self) -> None:
        frequencias = calcular_frequencias([])

        self.assertEqual(len(frequencias), 60)
        self.assertEqual(tuple(item.dezena for item in frequencias), tuple(range(1, 61)))
        for item in frequencias:
            self.assertEqual(item.ocorrencias, ())
            self.assertEqual(item.intervalos, ())
            self.assertIsNone(item.prim_oco)
            self.assertIsNone(item.ult_oco)
            self.assertEqual(item.num_oco, 0)
            self.assertIsNone(item.media_oco)
            self.assertIsNone(item.mediana_oco)
            self.assertIsNone(item.desv_padrao_oco)

    def test_exemplo_confirmado_intervalo_entre_35_e_50(self) -> None:
        resultados = [
            criar_resultado(35, [2, 3, 4, 5, 6, 7]),
            criar_resultado(50, [1, 2, 8, 9, 10, 11]),
        ]

        dezena_02 = calcular_frequencias(resultados)[1]

        self.assertEqual(dezena_02.ocorrencias, (35, 50))
        self.assertEqual(dezena_02.intervalos, (15,))
        self.assertEqual(dezena_02.prim_oco, 35)
        self.assertEqual(dezena_02.ult_oco, 50)
        self.assertEqual(dezena_02.num_oco, 2)
        self.assertEqual(dezena_02.media_oco, Decimal("15.000000"))
        self.assertEqual(dezena_02.mediana_oco, Decimal("15.000000"))
        self.assertEqual(dezena_02.desv_padrao_oco, Decimal("0.000000"))

    def test_calcula_media_mediana_e_desvio_dos_intervalos(self) -> None:
        resultados = [
            criar_resultado(10, [2, 3, 4, 5, 6, 7]),
            criar_resultado(20, [1, 2, 8, 9, 10, 11]),
            criar_resultado(35, [2, 12, 13, 14, 15, 16]),
            criar_resultado(50, [2, 17, 18, 19, 20, 21]),
        ]

        dezena_02 = calcular_frequencias(resultados)[1]

        self.assertEqual(dezena_02.ocorrencias, (10, 20, 35, 50))
        self.assertEqual(dezena_02.intervalos, (10, 15, 15))
        self.assertEqual(dezena_02.media_oco, Decimal("13.333333"))
        self.assertEqual(dezena_02.mediana_oco, Decimal("15.000000"))
        self.assertEqual(dezena_02.desv_padrao_oco, Decimal("2.357023"))

    def test_mediana_de_quantidade_par_de_intervalos(self) -> None:
        resultados = [
            criar_resultado(10, [2, 3, 4, 5, 6, 7]),
            criar_resultado(20, [1, 2, 8, 9, 10, 11]),
            criar_resultado(40, [2, 12, 13, 14, 15, 16]),
        ]

        dezena_02 = calcular_frequencias(resultados)[1]

        self.assertEqual(dezena_02.intervalos, (10, 20))
        self.assertEqual(dezena_02.media_oco, Decimal("15.000000"))
        self.assertEqual(dezena_02.mediana_oco, Decimal("15.000000"))
        self.assertEqual(dezena_02.desv_padrao_oco, Decimal("5.000000"))

    def test_uma_ocorrencia_nao_inventa_intervalo(self) -> None:
        dezena_60 = calcular_frequencias(
            [criar_resultado(1, [1, 2, 3, 4, 5, 60])]
        )[59]

        self.assertEqual(dezena_60.prim_oco, 1)
        self.assertEqual(dezena_60.ult_oco, 1)
        self.assertEqual(dezena_60.num_oco, 1)
        self.assertEqual(dezena_60.intervalos, ())
        self.assertIsNone(dezena_60.media_oco)
        self.assertIsNone(dezena_60.mediana_oco)
        self.assertIsNone(dezena_60.desv_padrao_oco)

    def test_ordena_entrada_por_numero_ap(self) -> None:
        resultados = [
            criar_resultado(50, [1, 2, 8, 9, 10, 11]),
            criar_resultado(35, [2, 3, 4, 5, 6, 7]),
        ]

        dezena_02 = calcular_frequencias(resultados)[1]

        self.assertEqual(dezena_02.ocorrencias, (35, 50))
        self.assertEqual(dezena_02.intervalos, (15,))

    def test_total_de_ocorrencias_e_seis_por_resultado(self) -> None:
        resultados = [
            criar_resultado(1, [1, 2, 3, 4, 5, 6]),
            criar_resultado(2, [7, 8, 9, 10, 11, 12]),
            criar_resultado(3, [1, 13, 14, 15, 16, 17]),
        ]

        frequencias = calcular_frequencias(resultados)

        self.assertEqual(sum(item.num_oco for item in frequencias), 18)
        self.assertEqual(frequencias[0].num_oco, 2)

    def test_periodo_e_inclusivo(self) -> None:
        resultados = [
            criar_resultado(10, [2, 3, 4, 5, 6, 7]),
            criar_resultado(20, [2, 8, 9, 10, 11, 12]),
            criar_resultado(30, [2, 13, 14, 15, 16, 17]),
        ]

        dezena_02 = calcular_frequencias(
            resultados,
            numero_ap_inicial=20,
            numero_ap_final=30,
        )[1]

        self.assertEqual(dezena_02.ocorrencias, (20, 30))
        self.assertEqual(dezena_02.intervalos, (10,))

    def test_rejeita_periodo_invalido(self) -> None:
        for inicio, fim in ((30, 20), (0, 20), (True, 20), (1.5, 20)):
            with self.subTest(inicio=inicio, fim=fim):
                self.assert_codigo_erro(
                    "PERIODO_INVALIDO",
                    lambda inicio=inicio, fim=fim: calcular_frequencias(
                        [], numero_ap_inicial=inicio, numero_ap_final=fim
                    ),
                )

    def test_rejeita_numero_ap_duplicado_no_historico(self) -> None:
        resultados = [
            criar_resultado(10, [1, 2, 3, 4, 5, 6]),
            criar_resultado(10, [7, 8, 9, 10, 11, 12]),
        ]

        self.assert_codigo_erro(
            "NUMERO_AP_DUPLICADO",
            lambda: calcular_frequencias(resultados),
        )

    def test_rejeita_data_incompativel_com_ordem_das_apresentacoes(self) -> None:
        resultados = [
            criar_resultado(10, [1, 2, 3, 4, 5, 6], dia=20),
            criar_resultado(20, [7, 8, 9, 10, 11, 12], dia=10),
        ]

        self.assert_codigo_erro(
            "ORDEM_HISTORICA_DIVERGENTE",
            lambda: calcular_frequencias(resultados),
        )

    def test_rejeita_objeto_que_nao_seja_resultado_validado(self) -> None:
        with self.assertRaisesRegex(TypeError, "ResultadoEntrada"):
            calcular_frequencias([object()])

    def test_resultados_de_entrada_nao_sao_alterados(self) -> None:
        resultados = [
            criar_resultado(35, [2, 3, 4, 5, 6, 7]),
            criar_resultado(50, [1, 2, 8, 9, 10, 11]),
        ]
        estado_antes = tuple((item.numero_ap, item.resultados) for item in resultados)

        calcular_frequencias(resultados)

        self.assertEqual(
            tuple((item.numero_ap, item.resultados) for item in resultados),
            estado_antes,
        )


if __name__ == "__main__":
    unittest.main()
