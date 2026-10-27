from dataclasses import replace
from pathlib import Path
import unittest

from msen.screener import (
    AdaptadorMedidasEstatisticas,
    AdaptadorMedidasGeometricas,
    AdaptadorPadroesHistoricos,
    ErroAdaptadorCriterio,
    ResultadoAvaliador,
    carregar_configuracao_screener,
    executar_funil,
)


PADRAO = Path(__file__).resolve().parents[1] / "config" / "screener.toml"
COMBINACAO = (1, 2, 3, 10, 20, 30)


class AdaptadoresScreenerTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.configuracao = carregar_configuracao_screener(PADRAO)

    def test_tres_adaptadores_desabilitados_aprovam_sem_chamar_avaliador(self):
        def nao_deve_ser_chamado(*_):
            raise AssertionError("avaliador desabilitado foi chamado")

        classes = (
            (AdaptadorPadroesHistoricos, "padroes_historicos"),
            (AdaptadorMedidasEstatisticas, "medidas_estatisticas"),
            (AdaptadorMedidasGeometricas, "medidas_geometricas"),
        )
        for classe, categoria in classes:
            with self.subTest(categoria=categoria):
                adaptador = classe(
                    f"TESTE_{categoria}",
                    self.configuracao.criterios[categoria],
                    nao_deve_ser_chamado,
                )
                decisao = adaptador.avaliar(COMBINACAO)
                self.assertTrue(decisao.aprovada)
                self.assertEqual(categoria, decisao.valores["categoria"])
                self.assertFalse(decisao.valores["habilitado"])

    def test_adaptador_habilitado_repassa_tolerancias_codigo_e_valores(self):
        base = self.configuracao.criterios["padroes_historicos"]
        habilitada = replace(base, habilitado=True)

        def avaliar(combinacao, tolerancias):
            return ResultadoAvaliador(
                aprovada=False,
                valores={
                    "combinacao": combinacao,
                    "tolerancia": tolerancias["tolerancia_ocorrencia_percentual"],
                    "ocorrencia_percentual": 0.0,
                },
            )

        adaptador = AdaptadorPadroesHistoricos("PD_TESTE", habilitada, avaliar)
        decisao = adaptador.avaliar(COMBINACAO)
        self.assertFalse(decisao.aprovada)
        self.assertEqual("PD_TESTE", decisao.codigo_criterio)
        self.assertEqual(3.0, decisao.valores["tolerancia"])
        self.assertEqual(0.0, decisao.valores["ocorrencia_percentual"])

    def test_adaptadores_se_integram_ao_funil_na_ordem_recebida(self):
        chamadas = []

        def reprovar(_combinacao, _tolerancias):
            chamadas.append("primeiro")
            return ResultadoAvaliador(False, {"motivo": "teste"})

        def nao_alcancado(_combinacao, _tolerancias):
            chamadas.append("segundo")
            return ResultadoAvaliador(True, {})

        padrao = replace(
            self.configuracao.criterios["padroes_historicos"], habilitado=True
        )
        estatistica = replace(
            self.configuracao.criterios["medidas_estatisticas"], habilitado=True
        )
        relatorio = executar_funil(
            (COMBINACAO,),
            (
                AdaptadorPadroesHistoricos("PD_TESTE", padrao, reprovar),
                AdaptadorMedidasEstatisticas("EST_TESTE", estatistica, nao_alcancado),
            ),
        )
        self.assertEqual(["primeiro"], chamadas)
        self.assertEqual({"PD_TESTE": 1, "EST_TESTE": 0}, dict(relatorio.exclusoes_por_criterio))

    def test_criterio_habilitado_exige_avaliador(self):
        habilitada = replace(
            self.configuracao.criterios["medidas_geometricas"], habilitado=True
        )
        with self.assertRaises(ErroAdaptadorCriterio) as contexto:
            AdaptadorMedidasGeometricas("GEO_TESTE", habilitada)
        self.assertEqual("AVALIADOR_AUSENTE", contexto.exception.codigo)

    def test_rejeita_resposta_fora_do_contrato(self):
        habilitada = replace(
            self.configuracao.criterios["medidas_estatisticas"], habilitado=True
        )
        adaptador = AdaptadorMedidasEstatisticas(
            "EST_TESTE", habilitada, lambda *_: True
        )
        with self.assertRaises(ErroAdaptadorCriterio) as contexto:
            adaptador.avaliar(COMBINACAO)
        self.assertEqual("RESULTADO_INVALIDO", contexto.exception.codigo)


if __name__ == "__main__":
    unittest.main()
