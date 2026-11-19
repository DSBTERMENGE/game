from datetime import date
import unittest

from msen.modelos import ResultadoEntrada
from msen.padroes import (
    calcular_categorias_diagonais,
    criar_fotografia_historica_diagonal,
)
from msen.screener import avaliar_filtro_diagonal
from msen.services import (
    ErroExecutorFiltroValidacao,
    criar_executor_filtro_validacao,
)


class ExecutorFiltrosValidacaoNovaTestCase(unittest.TestCase):
    def test_repassa_resultado_booleano(self):
        executor_positivo = criar_executor_filtro_validacao(lambda _item: True)
        executor_negativo = criar_executor_filtro_validacao(lambda _item: False)

        self.assertTrue(executor_positivo((1, 2, 3, 4, 5, 6)))
        self.assertFalse(executor_negativo((1, 2, 3, 4, 5, 6)))

    def test_recusa_retorno_nao_booleano(self):
        executor = criar_executor_filtro_validacao(lambda _item: 1)

        with self.assertRaises(ErroExecutorFiltroValidacao) as contexto:
            executor((1, 2, 3, 4, 5, 6))
        self.assertEqual("RETORNO_INVALIDO", contexto.exception.codigo)

    def test_diagonal_devolve_ocorrencia_quando_decisao_excluiria(self):
        historico = (
            ResultadoEntrada(date(2020, 1, 1), 1, 1, 12, 23, 34, 45, 56),
            ResultadoEntrada(date(2020, 1, 2), 2, 5, 14, 27, 38, 49, 60),
        )
        fotografia = criar_fotografia_historica_diagonal(historico)
        combinacao = (4, 15, 26, 37, 48, 59)
        executor = criar_executor_filtro_validacao(
            calcular_categorias_diagonais,
            fotografia_diagonal=fotografia,
            limite_diagonal="10",
        )
        decisao = avaliar_filtro_diagonal(combinacao, fotografia, "10")

        self.assertEqual(not decisao.aprovada, executor(combinacao))

    def test_diagonal_exige_fotografia(self):
        with self.assertRaises(ErroExecutorFiltroValidacao) as contexto:
            criar_executor_filtro_validacao(calcular_categorias_diagonais)
        self.assertEqual("FOTOGRAFIA_DIAGONAL_AUSENTE", contexto.exception.codigo)

    def test_rejeita_objeto_nao_chamavel(self):
        with self.assertRaises(TypeError):
            criar_executor_filtro_validacao(None)  # type: ignore[arg-type]


if __name__ == "__main__":
    unittest.main()
