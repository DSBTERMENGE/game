import unittest
from datetime import date
from decimal import Decimal

from msen.modelos import ResultadoEntrada
from msen.services import (
    ErroExecucaoValidacao, calcular_valor_criterio, comparar_resultado_numerico,
    comparar_resultado_padrao,
)
from msen.services.motor_validacao import _motivo_global
from msen.validacao import criar_registro_criterios_producao


class TestComparacaoResultadoNumerico(unittest.TestCase):
    def test_valores_iguais_sao_aprovados(self):
        resultado = comparar_resultado_numerico(
            estado_esperado="VALOR_IDENTIFICADO",
            valor_esperado=Decimal("21.500000"),
            valor_calculado=Decimal("21.500000"),
        )
        self.assertEqual(
            ("VALOR_IDENTIFICADO", Decimal("21.500000"), Decimal(0), "S"),
            resultado,
        )

    def test_valores_diferentes_sao_reprovados_com_diferenca(self):
        resultado = comparar_resultado_numerico(
            estado_esperado="VALOR_IDENTIFICADO",
            valor_esperado=Decimal("20"),
            valor_calculado=21,
        )
        self.assertEqual(
            ("VALOR_IDENTIFICADO", Decimal(21), Decimal(1), "N"), resultado
        )

    def test_comparacao_respeita_precisao_contratada_sem_mudar_valor_bruto(self):
        calculado = Decimal("9.720879120879120879")
        resultado = comparar_resultado_numerico(
            estado_esperado="VALOR_IDENTIFICADO",
            valor_esperado=Decimal("9.72087912087912"),
            valor_calculado=calculado,
            precisao_decimal=12,
        )
        self.assertEqual(
            ("VALOR_IDENTIFICADO", calculado, Decimal("0E-12"), "S"), resultado
        )

    def test_duas_ausencias_sao_aprovadas(self):
        self.assertEqual(
            ("SEM_VALOR", None, Decimal(0), "S"),
            comparar_resultado_numerico(
                estado_esperado="SEM_VALOR", valor_esperado=None,
                valor_calculado=None,
            ),
        )

    def test_referencia_pendente_e_retorno_invalido_sao_rejeitados(self):
        with self.assertRaisesRegex(ErroExecucaoValidacao, "referência"):
            comparar_resultado_numerico(
                estado_esperado="PENDENTE", valor_esperado=None, valor_calculado=1
            )
        with self.assertRaises(TypeError):
            comparar_resultado_numerico(
                estado_esperado="VALOR_IDENTIFICADO",
                valor_esperado=Decimal(1), valor_calculado=1.0,
            )

    def test_adaptador_respeita_assinaturas_estatistica_e_geometrica(self):
        definicoes = {
            item.codigo: item for item in criar_registro_criterios_producao().listar()
        }
        entrada = ResultadoEntrada.criar(
            data_resultado=date(2026, 1, 1), numero_ap=1,
            resultados=(1, 2, 3, 4, 5, 6),
        )
        self.assertEqual(21, calcular_valor_criterio(definicoes["EST_SOMA"], entrada))
        self.assertEqual(
            Decimal(5), calcular_valor_criterio(definicoes["GEO_EXTENSAO"], entrada)
        )


class TestComparacaoResultadoPadrao(unittest.TestCase):
    def test_detectado_e_ausente_correspondentes_sao_aprovados(self):
        self.assertEqual(
            ("PADRAO_IDENTIFICADO", 7, "S"),
            comparar_resultado_padrao(
                estado_esperado="PADRAO_IDENTIFICADO", id_padrao_esperado=7,
                detectado=True, id_padrao_criterio=7,
            ),
        )
        self.assertEqual(
            ("SEM_CORRESPONDENCIA", None, "S"),
            comparar_resultado_padrao(
                estado_esperado="SEM_CORRESPONDENCIA", id_padrao_esperado=None,
                detectado=False, id_padrao_criterio=7,
            ),
        )

    def test_divergencia_e_retorno_nao_booleano_sao_identificados(self):
        self.assertEqual(
            ("SEM_CORRESPONDENCIA", None, "N"),
            comparar_resultado_padrao(
                estado_esperado="PADRAO_IDENTIFICADO", id_padrao_esperado=7,
                detectado=False, id_padrao_criterio=7,
            ),
        )
        with self.assertRaises(TypeError):
            comparar_resultado_padrao(
                estado_esperado="SEM_CORRESPONDENCIA", id_padrao_esperado=None,
                detectado=1, id_padrao_criterio=7,
            )


class TestConsolidacaoMotorValidacao(unittest.TestCase):
    def test_motivo_global_prioriza_pendencia_depois_reprovacao(self):
        self.assertEqual(
            "REFERENCIAS_PENDENTES", _motivo_global(reprovadas=1, pendentes=1)
        )
        self.assertEqual(
            "CRITERIOS_REPROVADOS", _motivo_global(reprovadas=1, pendentes=0)
        )
        self.assertEqual(
            "HOMOLOGACAO_CONCLUIDA_AGUARDANDO_COBERTURA",
            _motivo_global(reprovadas=0, pendentes=0),
        )


if __name__ == "__main__":
    unittest.main()
