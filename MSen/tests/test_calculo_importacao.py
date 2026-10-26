import hashlib
import unittest
from datetime import date
from decimal import Decimal
from pathlib import Path

from msen.calculos import ResultadoCalculado, calcular_resultado
from msen.importacao import ler_resultados_calculados_excel
from msen.modelos import ResultadoEntrada


class CalculoImportacaoTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fixture = Path(__file__).parent / "fixtures" / "resultados_validos.xlsx"

    def test_linha_importada_e_igual_a_inclusao_manual_equivalente(self):
        importado = ler_resultados_calculados_excel(self.fixture)[0]
        manual = calcular_resultado(ResultadoEntrada.criar(
            numero_ap=100,
            data_resultado=date(2026, 1, 3),
            resultados=[1, 10, 20, 30, 40, 60],
        ))
        self.assertEqual(manual, importado)

    def test_calcula_todas_as_linhas_da_planilha(self):
        calculados = ler_resultados_calculados_excel(self.fixture)
        self.assertEqual(2, len(calculados))
        self.assertTrue(all(isinstance(item, ResultadoCalculado) for item in calculados))
        self.assertEqual((100, 101), tuple(item.numero_ap for item in calculados))

    def test_campos_derivados_tem_valores_e_precisoes_aprovados(self):
        resultado = ler_resultados_calculados_excel(self.fixture)[0]
        self.assertEqual(161, resultado.soma_res)
        self.assertEqual(Decimal("26.833333"), resultado.media_aritmetica_res)
        self.assertEqual(Decimal("25.0"), resultado.mediana_res)
        self.assertEqual(Decimal("19.497151"), resultado.desvio_padrao_media)
        self.assertEqual(Decimal("7.500000"), resultado.media_coordenada_x)
        self.assertEqual(Decimal("1.833333"), resultado.media_coordenada_y)
        self.assertEqual(1, resultado.versao_calculo)

    def test_preserva_campos_originais_e_ordem_das_dezenas(self):
        resultado = ler_resultados_calculados_excel(self.fixture)[0]
        self.assertEqual(date(2026, 1, 3), resultado.data_resultado)
        self.assertEqual(100, resultado.numero_ap)
        self.assertEqual((1, 10, 20, 30, 40, 60), resultado.resultados)

    def test_calculo_nao_modifica_a_planilha(self):
        hash_antes = hashlib.sha256(self.fixture.read_bytes()).hexdigest()
        ler_resultados_calculados_excel(self.fixture)
        hash_depois = hashlib.sha256(self.fixture.read_bytes()).hexdigest()
        self.assertEqual(hash_antes, hash_depois)

    def test_calculo_isolado_exige_modelo_validado(self):
        with self.assertRaises(TypeError):
            calcular_resultado(object())


if __name__ == "__main__":
    unittest.main()
