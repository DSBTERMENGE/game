"""Testes do corte histórico exclusivo da Etapa 17.2."""

from datetime import date, datetime
import unittest

from msen.modelos import ResultadoEntrada
from msen.services import ErroJanelaHistorica, selecionar_janela_historica


def resultado(numero_ap: int, dia: int) -> ResultadoEntrada:
    return ResultadoEntrada.criar(
        data_resultado=date(2026, 1, dia),
        numero_ap=numero_ap,
        resultados=(1, 2, 3, 4, 5, 6),
    )


class JanelaHistoricaTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.historico = tuple(resultado(numero, numero) for numero in range(1, 6))

    def test_sem_corte_retorna_historico_completo_e_ordenado(self) -> None:
        fora_de_ordem = tuple(reversed(self.historico))

        janela = selecionar_janela_historica(fora_de_ordem)

        self.assertEqual(tuple(item.numero_ap for item in janela.resultados), (1, 2, 3, 4, 5))
        self.assertEqual(janela.total_disponivel, 5)
        self.assertEqual(janela.quantidade, 5)
        self.assertEqual(janela.primeiro_numero_ap, 1)
        self.assertEqual(janela.ultimo_numero_ap, 5)
        self.assertEqual(fora_de_ordem, tuple(reversed(self.historico)))

    def test_corte_inicial_exclui_o_proprio_primeiro_resultado(self) -> None:
        janela = selecionar_janela_historica(
            self.historico, numero_ap_antes_de=1
        )

        self.assertEqual(janela.resultados, ())
        self.assertEqual(janela.quantidade, 0)
        self.assertIsNone(janela.primeiro_numero_ap)
        self.assertIsNone(janela.ultimo_numero_ap)

    def test_corte_intermediario_exclui_proprio_resultado_e_futuros(self) -> None:
        janela = selecionar_janela_historica(
            self.historico, numero_ap_antes_de=3
        )

        self.assertEqual(tuple(item.numero_ap for item in janela.resultados), (1, 2))
        self.assertEqual(janela.numero_ap_antes_de, 3)

    def test_corte_final_mantem_somente_antecessores_do_ultimo(self) -> None:
        janela = selecionar_janela_historica(
            self.historico, numero_ap_antes_de=5
        )

        self.assertEqual(tuple(item.numero_ap for item in janela.resultados), (1, 2, 3, 4))

    def test_corte_por_data_tambem_e_exclusivo(self) -> None:
        janela = selecionar_janela_historica(
            self.historico, data_antes_de=date(2026, 1, 3)
        )

        self.assertEqual(tuple(item.numero_ap for item in janela.resultados), (1, 2))
        self.assertEqual(janela.data_antes_de, date(2026, 1, 3))

    def test_rejeita_dois_cortes_e_valores_invalidos(self) -> None:
        casos = (
            ({"numero_ap_antes_de": 3, "data_antes_de": date(2026, 1, 3)}, "CORTES_CONFLITANTES"),
            ({"numero_ap_antes_de": True}, "CONCURSO_INVALIDO"),
            ({"numero_ap_antes_de": 0}, "CONCURSO_INVALIDO"),
            ({"data_antes_de": datetime(2026, 1, 3, 12)}, "DATA_INVALIDA"),
        )
        for argumentos, codigo in casos:
            with self.subTest(codigo=codigo):
                with self.assertRaises(ErroJanelaHistorica) as contexto:
                    selecionar_janela_historica(self.historico, **argumentos)
                self.assertEqual(contexto.exception.codigo, codigo)

    def test_rejeita_concurso_duplicado_e_ordem_de_datas_divergente(self) -> None:
        casos = (
            ((resultado(1, 1), resultado(1, 2)), "CONCURSO_DUPLICADO"),
            ((resultado(1, 2), resultado(2, 1)), "ORDEM_HISTORICA_DIVERGENTE"),
        )
        for historico, codigo in casos:
            with self.subTest(codigo=codigo):
                with self.assertRaises(ErroJanelaHistorica) as contexto:
                    selecionar_janela_historica(historico)
                self.assertEqual(contexto.exception.codigo, codigo)

    def test_rejeita_colecao_e_item_de_tipo_invalido(self) -> None:
        with self.assertRaisesRegex(TypeError, "iteráveis"):
            selecionar_janela_historica(None)  # type: ignore[arg-type]
        with self.assertRaisesRegex(TypeError, "ResultadoEntrada"):
            selecionar_janela_historica((self.historico[0], object()))


if __name__ == "__main__":
    unittest.main()
