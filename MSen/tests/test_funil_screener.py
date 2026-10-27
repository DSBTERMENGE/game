from dataclasses import dataclass, field
from pathlib import Path
import unittest

from msen.screener import (
    DecisaoCriterio,
    ErroFunil,
    carregar_configuracao_screener,
    executar_funil,
    gerar_amostra,
)


PADRAO = Path(__file__).resolve().parents[1] / "config" / "screener.toml"


@dataclass
class CriterioArtificial:
    codigo: str
    divisor_reprovado: int
    chamadas: list[int] = field(default_factory=list)

    def avaliar(self, combinacao):
        numero = combinacao[0]
        self.chamadas.append(numero)
        aprovada = numero % self.divisor_reprovado != 0
        return DecisaoCriterio(
            aprovada=aprovada,
            codigo_criterio=self.codigo,
            valores={"primeira_dezena": numero},
        )


class FunilScreenerTestCase(unittest.TestCase):
    def test_sem_criterios_preserva_as_cinco_mil_combinacoes(self):
        configuracao = carregar_configuracao_screener(PADRAO)
        amostra = gerar_amostra(configuracao)
        relatorio = executar_funil(amostra, ())
        self.assertEqual(5_000, relatorio.total_recebido)
        self.assertEqual(5_000, relatorio.total_aprovado)
        self.assertEqual(amostra, relatorio.combinacoes_aprovadas)
        self.assertEqual({}, dict(relatorio.exclusoes_por_criterio))

    def test_contabiliza_funil_e_saldo_na_ordem(self):
        combinacoes = tuple((numero, 10, 20, 30, 40, 50) for numero in range(1, 7))
        pares = CriterioArtificial("F_PAR", 2)
        multiplos_tres = CriterioArtificial("F_TRES", 3)
        relatorio = executar_funil(combinacoes, (pares, multiplos_tres))
        self.assertEqual(6, relatorio.total_recebido)
        self.assertEqual(2, relatorio.total_aprovado)
        self.assertEqual({"F_PAR": 3, "F_TRES": 1}, dict(relatorio.exclusoes_por_criterio))
        self.assertEqual({"F_PAR": 6, "F_TRES": 3}, dict(relatorio.avaliacoes_por_criterio))
        self.assertEqual({"F_PAR": 3, "F_TRES": 2}, dict(relatorio.saldo_apos_criterio))

    def test_reprovacao_salta_os_criterios_restantes(self):
        combinacoes = ((2, 10, 20, 30, 40, 50), (5, 10, 20, 30, 40, 50))
        primeiro = CriterioArtificial("PRIMEIRO", 2)
        segundo = CriterioArtificial("SEGUNDO", 5)
        executar_funil(combinacoes, (primeiro, segundo))
        self.assertEqual([2, 5], primeiro.chamadas)
        self.assertEqual([5], segundo.chamadas)

    def test_rejeita_codigos_duplicados(self):
        criterios = (CriterioArtificial("REPETIDO", 2), CriterioArtificial("REPETIDO", 3))
        with self.assertRaises(ErroFunil) as contexto:
            executar_funil((), criterios)
        self.assertEqual("CODIGO_CRITERIO_DUPLICADO", contexto.exception.codigo)

    def test_rejeita_codigo_divergente_na_decisao(self):
        class CriterioInvalido:
            codigo = "CERTO"

            def avaliar(self, combinacao):
                return DecisaoCriterio(True, "ERRADO", {})

        with self.assertRaises(ErroFunil) as contexto:
            executar_funil(((1, 2, 3, 4, 5, 6),), (CriterioInvalido(),))
        self.assertEqual("CODIGO_DECISAO_DIVERGENTE", contexto.exception.codigo)


if __name__ == "__main__":
    unittest.main()
