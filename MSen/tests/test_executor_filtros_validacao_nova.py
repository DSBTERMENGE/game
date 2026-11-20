import unittest

from msen.padroes import (
    calcular_categorias_diagonais,
)
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

    def test_diagonal_usa_detector_booleano_em_vez_da_raridade_categorica(self):
        executor = criar_executor_filtro_validacao(calcular_categorias_diagonais)

        self.assertTrue(executor((4, 15, 26, 37, 48, 59)))
        self.assertFalse(executor((2, 6, 15, 17, 28, 38)))

    def test_rejeita_objeto_nao_chamavel(self):
        with self.assertRaises(TypeError):
            criar_executor_filtro_validacao(None)  # type: ignore[arg-type]


if __name__ == "__main__":
    unittest.main()
