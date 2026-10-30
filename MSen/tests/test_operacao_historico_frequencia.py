"""Testes do coordenador de execução única e cancelamento."""

from threading import Event, Thread
import unittest

from msen.services import (
    CoordenadorOperacaoFrequencia,
    ExecucaoFrequenciaEmAndamento,
)


class OperacaoHistoricoFrequenciaTestCase(unittest.TestCase):
    def test_impede_duas_execucoes_e_solicita_cancelamento(self) -> None:
        coordenador = CoordenadorOperacaoFrequencia()
        iniciou = Event()
        terminou = Event()
        observado = []

        def operacao(cancelado):
            iniciou.set()
            if not terminou.wait(2):
                raise TimeoutError("Teste não liberou a operação.")
            observado.append(cancelado())

        thread = Thread(target=lambda: coordenador.executar(operacao))
        thread.start()
        self.assertTrue(iniciou.wait(1))
        self.assertTrue(coordenador.esta_executando())
        with self.assertRaises(ExecucaoFrequenciaEmAndamento):
            coordenador.executar(lambda _: None)
        self.assertTrue(coordenador.solicitar_cancelamento())
        terminou.set()
        thread.join(2)
        self.assertEqual([True], observado)
        self.assertFalse(coordenador.esta_executando())
        self.assertFalse(coordenador.solicitar_cancelamento())

    def test_libera_coordenador_depois_de_falha(self) -> None:
        coordenador = CoordenadorOperacaoFrequencia()
        with self.assertRaisesRegex(RuntimeError, "falha"):
            coordenador.executar(lambda _: (_ for _ in ()).throw(RuntimeError("falha")))
        self.assertEqual("ok", coordenador.executar(lambda _: "ok"))


if __name__ == "__main__":
    unittest.main()
