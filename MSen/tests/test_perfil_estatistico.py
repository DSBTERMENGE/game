"""Testes manuais do perfil estatístico genérico da Etapa 17.3."""

from decimal import Decimal
import unittest

from msen.services import (
    ErroPerfilEstatistico,
    calcular_faixa_desvio_padrao,
    calcular_faixa_percentual_media,
    calcular_perfil_estatistico,
)


class PerfilEstatisticoTestCase(unittest.TestCase):
    def setUp(self) -> None:
        # Série clássica: média 5, variância populacional 4 e desvio 2.
        self.perfil = calcular_perfil_estatistico((2, 4, 4, 4, 5, 5, 7, 9))

    def test_calcula_resumo_controlado_manualmente(self) -> None:
        self.assertEqual(self.perfil.quantidade, 8)
        self.assertEqual(self.perfil.media, Decimal("5"))
        self.assertEqual(self.perfil.desvio_padrao_populacional, Decimal("2"))
        self.assertEqual(self.perfil.minimo, Decimal("2"))
        self.assertEqual(self.perfil.maximo, Decimal("9"))

    def test_distribuicao_real_fecha_quantidade_e_cem_por_cento(self) -> None:
        observada = tuple(
            (ponto.valor, ponto.frequencia, ponto.percentual)
            for ponto in self.perfil.distribuicao
        )
        self.assertEqual(
            observada,
            (
                (Decimal("2"), 1, Decimal("12.500000")),
                (Decimal("4"), 3, Decimal("37.500000")),
                (Decimal("5"), 2, Decimal("25.000000")),
                (Decimal("7"), 1, Decimal("12.500000")),
                (Decimal("9"), 1, Decimal("12.500000")),
            ),
        )
        self.assertEqual(sum(p.frequencia for p in self.perfil.distribuicao), 8)
        self.assertEqual(
            sum((p.percentual for p in self.perfil.distribuicao), Decimal(0)),
            Decimal("100.000000"),
        )

    def test_faixa_percentual_aceita_margens_assimetricas(self) -> None:
        faixa = calcular_faixa_percentual_media(
            self.perfil,
            percentual_inferior=Decimal("10"),
            percentual_superior=Decimal("20"),
        )

        self.assertEqual(faixa.metodo, "percentual_media")
        self.assertEqual(faixa.limite_inferior, Decimal("4.5"))
        self.assertEqual(faixa.limite_superior, Decimal("6"))
        self.assertTrue(faixa.contem(Decimal("4.5")))
        self.assertTrue(faixa.contem(6))
        self.assertFalse(faixa.contem(Decimal("6.01")))

    def test_faixa_por_desvio_aceita_multiplicadores_assimetricos(self) -> None:
        faixa = calcular_faixa_desvio_padrao(
            self.perfil,
            multiplicador_inferior=1,
            multiplicador_superior=2,
        )

        self.assertEqual(faixa.metodo, "desvio_padrao")
        self.assertEqual(faixa.limite_inferior, Decimal("3"))
        self.assertEqual(faixa.limite_superior, Decimal("9"))

    def test_serie_constante_tem_desvio_zero_e_distribuicao_unica(self) -> None:
        perfil = calcular_perfil_estatistico((Decimal("3.5"),) * 4)
        faixa = calcular_faixa_desvio_padrao(
            perfil, multiplicador_inferior=1, multiplicador_superior=1
        )

        self.assertEqual(perfil.desvio_padrao_populacional, 0)
        self.assertEqual(len(perfil.distribuicao), 1)
        self.assertEqual(faixa.limite_inferior, Decimal("3.5"))
        self.assertEqual(faixa.limite_superior, Decimal("3.5"))

    def test_percentual_preserva_ordem_em_serie_com_media_negativa(self) -> None:
        perfil = calcular_perfil_estatistico((-6, -4))
        faixa = calcular_faixa_percentual_media(
            perfil, percentual_inferior=10, percentual_superior=20
        )

        self.assertEqual(faixa.limite_inferior, Decimal("-5.5"))
        self.assertEqual(faixa.limite_superior, Decimal("-4"))

    def test_rejeita_serie_vazia_tipo_invalido_e_valor_nao_finito(self) -> None:
        with self.assertRaises(ErroPerfilEstatistico) as vazia:
            calcular_perfil_estatistico(())
        self.assertEqual(vazia.exception.codigo, "SERIE_VAZIA")

        for valores in ((True,), (1.5,)):
            with self.subTest(valores=valores):
                with self.assertRaises(TypeError):
                    calcular_perfil_estatistico(valores)  # type: ignore[arg-type]

        with self.assertRaises(ErroPerfilEstatistico) as nao_finito:
            calcular_perfil_estatistico((Decimal("NaN"),))
        self.assertEqual(nao_finito.exception.codigo, "VALOR_NAO_FINITO")

    def test_rejeita_margens_negativas_e_perfil_invalido(self) -> None:
        with self.assertRaises(ErroPerfilEstatistico) as contexto:
            calcular_faixa_percentual_media(
                self.perfil, percentual_inferior=-1, percentual_superior=10
            )
        self.assertEqual(contexto.exception.codigo, "PARAMETRO_NEGATIVO")

        with self.assertRaises(TypeError):
            calcular_faixa_desvio_padrao(  # type: ignore[arg-type]
                object(), multiplicador_inferior=1, multiplicador_superior=1
            )


if __name__ == "__main__":
    unittest.main()
