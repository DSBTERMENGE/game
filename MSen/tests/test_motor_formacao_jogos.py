import tracemalloc
import unittest

from msen.services import ErroMotorFormacaoJogos, executar_geracao_controlada


class MotorFormacaoJogosTest(unittest.TestCase):
    def test_encaminha_cada_combinacao_uma_vez_em_ordem(self) -> None:
        recebidas = []
        relatorio = executar_geracao_controlada(range(1, 8), recebidas.append)
        self.assertEqual("CONCLUIDA", relatorio.estado)
        self.assertEqual(7, relatorio.quantidade_combinacoes)
        self.assertEqual(7, relatorio.quantidade_encaminhada)
        self.assertEqual(100, relatorio.percentual_concluido)
        self.assertEqual((1, 2, 3, 4, 5, 6), recebidas[0])
        self.assertEqual((2, 3, 4, 5, 6, 7), recebidas[-1])
        self.assertEqual(len(recebidas), len(set(recebidas)))

    def test_informa_inicio_intervalos_e_fim(self) -> None:
        progressos = []
        executar_geracao_controlada(
            range(1, 9), lambda _combinacao: None,
            informar_progresso=lambda atual, total: progressos.append((atual, total)),
            intervalo_progresso=10,
        )
        self.assertEqual((0, 28), progressos[0])
        self.assertIn((10, 28), progressos)
        self.assertIn((20, 28), progressos)
        self.assertEqual((28, 28), progressos[-1])

    def test_cancela_antes_da_proxima_combinacao(self) -> None:
        recebidas = []
        relatorio = executar_geracao_controlada(
            range(1, 10), recebidas.append,
            cancelamento_solicitado=lambda: len(recebidas) == 3,
        )
        self.assertEqual("CANCELADA", relatorio.estado)
        self.assertEqual(3, relatorio.quantidade_encaminhada)
        self.assertEqual(3, len(recebidas))
        self.assertLess(relatorio.percentual_concluido, 100)

    def test_converte_falha_do_adaptador_em_erro_operacional(self) -> None:
        def falhar(_combinacao):
            raise RuntimeError("falha interna")

        with self.assertRaises(ErroMotorFormacaoJogos) as contexto:
            executar_geracao_controlada(range(1, 7), falhar)
        self.assertEqual("FALHA_ADAPTADOR_SCREENER", contexto.exception.codigo)

    def test_rejeita_origem_com_menos_de_seis_dezenas(self) -> None:
        with self.assertRaises(ErroMotorFormacaoJogos) as contexto:
            executar_geracao_controlada(range(1, 6), lambda _combinacao: None)
        self.assertEqual("DEZENAS_INSUFICIENTES", contexto.exception.codigo)

    def test_processa_230230_sem_acumular_as_combinacoes(self) -> None:
        tracemalloc.start()
        relatorio = executar_geracao_controlada(
            range(1, 27), lambda _combinacao: None,
            intervalo_progresso=25_000,
        )
        _, pico = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        self.assertEqual(230_230, relatorio.quantidade_encaminhada)
        self.assertLess(pico, 2 * 1024 * 1024, f"pico de memória: {pico}")


if __name__ == "__main__":
    unittest.main()
