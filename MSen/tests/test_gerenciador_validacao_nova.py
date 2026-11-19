from threading import Event
from time import monotonic, sleep
import unittest

from msen.api.validacao_nova import (
    ExecucaoValidacaoNovaEmAndamento,
    GerenciadorExecucoesValidacaoNova,
)
from msen.services import OperacaoValidacaoNovaCancelada


def aguardar(gerenciador, identificador, estados, limite=2):
    inicio = monotonic()
    while monotonic() - inicio < limite:
        estado = gerenciador.obter(identificador)
        if estado["estado"] in estados:
            return estado
        sleep(0.005)
    raise AssertionError("A execução não atingiu o estado esperado.")


class GerenciadorValidacaoNovaTestCase(unittest.TestCase):
    def test_mantem_progresso_e_resultado_final_em_memoria(self):
        def operacao(ids, progresso, _cancelado, _ocorrencia):
            self.assertEqual((10, 20), ids)
            progresso(0, 2, "Grupo A", "Filtro A")
            progresso(1, 2, "Grupo A", "Filtro A")
            progresso(2, 2, "Grupo B", "Filtro B")
            return {"total_filtros": 2}

        gerenciador = GerenciadorExecucoesValidacaoNova(operacao)
        inicio = gerenciador.iniciar((10, 20))
        fim = aguardar(gerenciador, inicio["id"], {"CONCLUIDA"})

        self.assertEqual(100, fim["percentual"])
        self.assertEqual("Grupo B", fim["grupo_atual"])
        self.assertEqual("Filtro B", fim["filtro_atual"])
        self.assertEqual({"total_filtros": 2}, fim["resultado"])
        self.assertNotIn("_cancelar", fim)

    def test_cancela_em_ponto_seguro(self):
        iniciou = Event()

        def operacao(_ids, progresso, cancelado, _ocorrencia):
            progresso(0, 100, "Grupo", "Filtro")
            iniciou.set()
            while not cancelado():
                sleep(0.002)
            raise OperacaoValidacaoNovaCancelada()

        gerenciador = GerenciadorExecucoesValidacaoNova(operacao)
        execucao = gerenciador.iniciar()
        self.assertTrue(iniciou.wait(1))
        solicitacao = gerenciador.cancelar(execucao["id"])
        self.assertEqual("CANCELANDO", solicitacao["estado"])
        fim = aguardar(gerenciador, execucao["id"], {"CANCELADA"})
        self.assertIsNone(fim["resultado"])

    def test_impede_duas_execucoes_simultaneas(self):
        liberar = Event()

        def operacao(_ids, _progresso, _cancelado, _ocorrencia):
            liberar.wait(1)
            return {}

        gerenciador = GerenciadorExecucoesValidacaoNova(operacao)
        primeira = gerenciador.iniciar()
        with self.assertRaises(ExecucaoValidacaoNovaEmAndamento):
            gerenciador.iniciar()
        liberar.set()
        aguardar(gerenciador, primeira["id"], {"CONCLUIDA"})

    def test_falha_fica_consultavel_sem_detalhe_oculto(self):
        def operacao(_ids, _progresso, _cancelado, _ocorrencia):
            raise ValueError("entrada inválida")

        gerenciador = GerenciadorExecucoesValidacaoNova(operacao)
        execucao = gerenciador.iniciar()
        fim = aguardar(gerenciador, execucao["id"], {"FALHOU"})
        self.assertEqual("ValueError", fim["erro"]["tipo"])
        self.assertEqual("entrada inválida", fim["erro"]["mensagem"])

    def test_pausa_em_ocorrencia_e_retorna_somente_apos_continuar(self):
        ocorrencia = type("Ocorrencia", (), {
            "id_grupo": 2,
            "nome_grupo": "Grupo",
            "id_filtro": 12,
            "nome_filtro": "Filtro",
            "indice_combinacao": 7,
            "combinacao": (1, 2, 3, 4, 5, 6),
        })()

        def operacao(_ids, progresso, _cancelado, informar_ocorrencia):
            progresso(7, 1000, "Grupo", "Filtro")
            informar_ocorrencia(ocorrencia)
            return {"total_filtros": 1}

        gerenciador = GerenciadorExecucoesValidacaoNova(operacao)
        inicio = gerenciador.iniciar((12,))
        pausa = aguardar(
            gerenciador, inicio["id"], {"AGUARDANDO_CONFIRMACAO"}
        )
        self.assertEqual([1, 2, 3, 4, 5, 6], pausa["ocorrencia_atual"]["combinacao"])
        self.assertEqual(7, pausa["ocorrencia_atual"]["indice_combinacao"])

        retomada = gerenciador.continuar(inicio["id"])
        self.assertEqual("EXECUTANDO", retomada["estado"])
        fim = aguardar(gerenciador, inicio["id"], {"CONCLUIDA"})
        self.assertIsNone(fim["ocorrencia_atual"])


if __name__ == "__main__":
    unittest.main()
