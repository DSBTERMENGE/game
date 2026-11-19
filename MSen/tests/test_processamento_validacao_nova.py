from decimal import Decimal
import unittest

from msen.services import (
    ErroProcessamentoValidacaoNova,
    FiltroExecutavelValidacao,
    GrupoFiltrosValidacao,
    OperacaoValidacaoNovaCancelada,
    processar_colecao_validacao_nova,
)


class ProcessamentoValidacaoNovaTestCase(unittest.TestCase):
    def setUp(self):
        self.catalogo = (
            GrupoFiltrosValidacao(2, "Grupo B", (
                FiltroExecutavelValidacao(20, "Filtro B", ""),
            )),
            GrupoFiltrosValidacao(1, "Grupo A", (
                FiltroExecutavelValidacao(10, "Filtro A", ""),
            )),
        )
        self.colecao = (
            (1, 2, 3, 4, 5, 6),
            (7, 8, 9, 10, 11, 12),
            (13, 14, 15, 16, 17, 18),
        )

    def test_aplica_cada_filtro_a_colecao_inteira_sem_funil(self):
        chamadas = {10: 0, 20: 0}

        def criar(id_filtro):
            def executar(combinacao):
                chamadas[id_filtro] += 1
                return id_filtro == 10 or combinacao[0] == 1
            return executar

        relatorio = processar_colecao_validacao_nova(
            self.colecao, self.catalogo, criar
        )

        self.assertEqual({10: 3, 20: 3}, chamadas)
        self.assertEqual(6, relatorio.total_avaliacoes)
        self.assertEqual([1, 3], [item.ocorrencias for item in relatorio.resultados])
        self.assertEqual(
            [Decimal("33.333333"), Decimal("100.000000")],
            [item.incidencia_percentual for item in relatorio.resultados],
        )

    def test_executa_somente_ids_escolhidos_na_ordem_solicitada(self):
        usados = []
        relatorio = processar_colecao_validacao_nova(
            self.colecao,
            self.catalogo,
            lambda id_filtro: usados.append(id_filtro) or (lambda _item: False),
            ids_filtros=(10,),
        )
        self.assertEqual([10], usados)
        self.assertEqual([10], [item.id_filtro for item in relatorio.resultados])
        self.assertEqual(3, relatorio.total_avaliacoes)

    def test_rejeita_filtro_ausente_repetido_ou_selecao_vazia(self):
        casos = (
            ((), "SELECAO_VAZIA"),
            ((10, 10), "FILTRO_REPETIDO"),
            ((99,), "FILTRO_INDISPONIVEL"),
        )
        for ids, codigo in casos:
            with self.subTest(codigo=codigo):
                with self.assertRaises(ErroProcessamentoValidacaoNova) as contexto:
                    processar_colecao_validacao_nova(
                        self.colecao, self.catalogo, lambda _id: lambda _item: False,
                        ids_filtros=ids,
                    )
                self.assertEqual(codigo, contexto.exception.codigo)

    def test_rejeita_colecao_vazia_e_catalogo_sem_filtros(self):
        with self.assertRaises(ErroProcessamentoValidacaoNova) as contexto:
            processar_colecao_validacao_nova(
                (), self.catalogo, lambda _id: lambda _item: False
            )
        self.assertEqual("COLECAO_VAZIA", contexto.exception.codigo)

        with self.assertRaises(ErroProcessamentoValidacaoNova) as contexto:
            processar_colecao_validacao_nova(
                self.colecao, (), lambda _id: lambda _item: False
            )
        self.assertEqual("SEM_FILTROS", contexto.exception.codigo)

    def test_informa_progresso_total_grupo_filtro_e_aceita_cancelamento(self):
        progressos = []
        verificacoes = 0

        def cancelado():
            nonlocal verificacoes
            verificacoes += 1
            return verificacoes > 2

        with self.assertRaises(OperacaoValidacaoNovaCancelada):
            processar_colecao_validacao_nova(
                self.colecao,
                self.catalogo,
                lambda _id: lambda _item: False,
                informar_progresso=lambda *item: progressos.append(item),
                cancelamento_solicitado=cancelado,
            )
        self.assertEqual((0, 6, "Grupo B", "Filtro B"), progressos[0])
        self.assertEqual((2, 6, "Grupo B", "Filtro B"), progressos[-1])

    def test_um_filtro_informa_cada_ocorrencia_com_combinacao(self):
        ocorrencias = []
        processar_colecao_validacao_nova(
            self.colecao,
            self.catalogo,
            lambda _id: lambda item: item[0] in {1, 13},
            ids_filtros=(20,),
            informar_ocorrencia=ocorrencias.append,
            construir_desenho=lambda id_filtro, item: {
                "id_interno_usado": id_filtro,
                "dezenas_marcadas": list(item),
            },
        )
        self.assertEqual([1, 3], [item.indice_combinacao for item in ocorrencias])
        self.assertEqual(self.colecao[0], ocorrencias[0].combinacao)
        self.assertEqual("Grupo B", ocorrencias[0].nome_grupo)
        self.assertEqual(list(self.colecao[0]), ocorrencias[0].desenho["dezenas_marcadas"])

    def test_varios_filtros_nao_interrompem_para_mostrar_ocorrencias(self):
        ocorrencias = []
        processar_colecao_validacao_nova(
            self.colecao,
            self.catalogo,
            lambda _id: lambda _item: True,
            informar_ocorrencia=ocorrencias.append,
        )
        self.assertEqual([], ocorrencias)


if __name__ == "__main__":
    unittest.main()
