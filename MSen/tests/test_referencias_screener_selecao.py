import unittest

from msen.services.homologacao_screener import (
    PERFIS_OBRIGATORIOS,
    CriterioHomologado,
    EstadoHomologacaoScreener,
)
from msen.services.referencias_screener_selecao import (
    ReferenciasScreenerDesatualizadas,
    verificar_referencias_atualizadas,
)


def criar_estado(**alteracoes):
    criterio = CriterioHomologado(
        "EST_SOMA", "APROVADO", "a" * 64, "b" * 64, 200, 200, 0, 0
    )
    dados = {
        "atualizado": True,
        "motivo": "TODAS_AS_CONDICOES_CONFIRMADAS",
        "quantidade_resultados": 3069,
        "total_resultados": 3069,
        "criterios": (criterio,),
        "perfis": tuple((codigo, 3069) for codigo in sorted(PERFIS_OBRIGATORIOS)),
    }
    dados.update(alteracoes)
    return EstadoHomologacaoScreener(**dados)


class ReferenciasScreenerSelecaoTestCase(unittest.TestCase):
    def test_libera_estado_integralmente_atualizado(self):
        resultado = verificar_referencias_atualizadas(lambda: criar_estado())

        self.assertEqual(True, resultado["atualizado"])
        self.assertEqual(3069, resultado["quantidade_resultados"])
        self.assertEqual(1, resultado["quantidade_filtros"])
        self.assertEqual(len(PERFIS_OBRIGATORIOS), resultado["quantidade_perfis"])

    def test_bloqueia_estado_global_desatualizado(self):
        with self.assertRaises(ReferenciasScreenerDesatualizadas) as contexto:
            verificar_referencias_atualizadas(
                lambda: criar_estado(
                    atualizado=False, motivo="REFERENCIAS_OU_CALCULOS_PENDENTES"
                )
            )
        self.assertEqual("REFERENCIAS_DESATUALIZADAS", contexto.exception.codigo)

    def test_bloqueia_quantidade_de_resultados_divergente(self):
        with self.assertRaises(ReferenciasScreenerDesatualizadas) as contexto:
            verificar_referencias_atualizadas(
                lambda: criar_estado(quantidade_resultados=3068)
            )
        self.assertEqual(
            "QUANTIDADE_RESULTADOS_DIVERGENTE", contexto.exception.codigo
        )

    def test_bloqueia_filtro_com_pendencia(self):
        pendente = CriterioHomologado(
            "PAD_PD_011", "PENDENTE", "a" * 64, "b" * 64, 200, 199, 1, 0
        )
        with self.assertRaises(ReferenciasScreenerDesatualizadas) as contexto:
            verificar_referencias_atualizadas(
                lambda: criar_estado(criterios=(pendente,))
            )
        self.assertEqual("FILTRO_NAO_HOMOLOGADO", contexto.exception.codigo)

    def test_bloqueia_perfil_historico_incompleto(self):
        with self.assertRaises(ReferenciasScreenerDesatualizadas) as contexto:
            verificar_referencias_atualizadas(
                lambda: criar_estado(perfis=(("EST_SOMA", 3069),))
            )
        self.assertEqual(
            "PERFIS_HISTORICOS_DESATUALIZADOS", contexto.exception.codigo
        )


if __name__ == "__main__":
    unittest.main()
