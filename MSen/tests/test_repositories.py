import unittest
from datetime import date, datetime, timezone
from decimal import Decimal

from msen.calculos import calcular_resultado
from msen.database import ErroRepositorioResultado, RepositorioResultados
from msen.database.repositories import _linha_para_resultado, _parametros
from msen.modelos import ResultadoEntrada


class MapeamentoRepositorioTestCase(unittest.TestCase):
    def setUp(self):
        self.entrada = ResultadoEntrada.criar(
            data_resultado="11/10/2026",
            numero_ap=3069,
            resultados=[47, 5, 22, 44, 57, 19],
        )
        self.calculado = calcular_resultado(self.entrada)

    def test_parametros_preservam_campos_originais_e_derivados(self):
        parametros = _parametros(self.calculado)
        self.assertEqual(15, len(parametros))
        self.assertEqual(date(2026, 10, 11), parametros[0])
        self.assertEqual(3069, parametros[1])
        self.assertEqual((47, 5, 22, 44, 57, 19), parametros[2:8])
        self.assertEqual(194, parametros[8])

    def test_mapeia_as_dezoito_colunas_retornadas(self):
        instante = datetime(2026, 10, 26, tzinfo=timezone.utc)
        linha = (
            7, self.calculado.data_resultado, self.calculado.numero_ap,
            *self.calculado.resultados, self.calculado.soma_res,
            self.calculado.media_aritmetica_res, self.calculado.mediana_res,
            self.calculado.desvio_padrao_media, self.calculado.media_coordenada_x,
            self.calculado.media_coordenada_y, self.calculado.versao_calculo,
            instante, instante,
        )
        persistido = _linha_para_resultado(linha)
        self.assertEqual(7, persistido.id_resultado)
        self.assertEqual(self.calculado, persistido.resultado)
        self.assertEqual(3069, persistido.numero_ap)
        self.assertEqual(instante, persistido.criado_em)

    def test_rejeita_quantidade_incorreta_de_colunas(self):
        with self.assertRaises(ValueError):
            _linha_para_resultado((1, 2, 3))

    def test_repositorio_exige_conexao_psycopg(self):
        with self.assertRaises(TypeError):
            RepositorioResultados(object())

    def test_erro_carrega_codigo_e_concurso(self):
        erro = ErroRepositorioResultado("TESTE", "mensagem", numero_ap=3069)
        self.assertEqual("TESTE", erro.codigo)
        self.assertEqual(3069, erro.numero_ap)

    def test_decimais_nao_sao_convertidos_para_float(self):
        parametros = _parametros(self.calculado)
        self.assertTrue(all(isinstance(valor, Decimal) for valor in parametros[9:14]))


if __name__ == "__main__":
    unittest.main()
