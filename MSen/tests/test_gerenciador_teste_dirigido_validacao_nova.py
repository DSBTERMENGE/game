import unittest

from msen.api.validacao_nova import GerenciadorTestesDirigidosValidacaoNova


class GerenciadorTesteDirigidoValidacaoNovaTestCase(unittest.TestCase):
    def test_guarda_na_memoria_e_testa_em_operacao_separada(self):
        combinacoes = tuple((i, i + 10, i + 20, i + 30, i + 40, i + 50)
                            for i in range(1, 11))

        def preparar(id_grupo, id_filtro):
            return {
                "id_grupo": id_grupo,
                "nome_grupo": "Grupo",
                "id_filtro": id_filtro,
                "nome_filtro": "Filtro",
                "tentativas_geracao": 25,
                "combinacoes": combinacoes,
            }

        chamadas = []

        def testar(id_filtro, recebidas):
            chamadas.append((id_filtro, recebidas))
            return {"avaliacoes": tuple({
                "numero": indice,
                "combinacao": list(item),
                "detectada": True,
                "desenho": {"dezenas_marcadas": list(item), "segmentos": []},
            } for indice, item in enumerate(recebidas, start=1))}

        gerenciador = GerenciadorTestesDirigidosValidacaoNova(preparar, testar)
        criado = gerenciador.criar(2, 12)

        self.assertEqual("GERADO", criado["estado"])
        self.assertEqual(10, criado["total_combinacoes"])
        self.assertIsNone(criado["resultado"])
        pausado = gerenciador.testar(criado["id"])
        self.assertEqual("AGUARDANDO_CONFIRMACAO", pausado["estado"])
        self.assertEqual(1, pausado["ocorrencia_atual"]["numero"])
        for numero in range(2, 11):
            pausado = gerenciador.continuar(criado["id"])
            self.assertEqual(numero, pausado["ocorrencia_atual"]["numero"])
        concluido = gerenciador.continuar(criado["id"])
        self.assertEqual("TESTADO", concluido["estado"])
        self.assertEqual(10, concluido["resultado"]["ocorrencias_detectadas"])
        self.assertIsNone(concluido["ocorrencia_atual"])
        self.assertEqual((12, combinacoes), chamadas[0])

    def test_registro_desconhecido_nao_e_inventado(self):
        gerenciador = GerenciadorTestesDirigidosValidacaoNova(
            lambda _grupo, _filtro: {}, lambda _filtro, _itens: {}
        )
        with self.assertRaises(KeyError):
            gerenciador.obter("ausente")
        with self.assertRaises(KeyError):
            gerenciador.testar("ausente")
        with self.assertRaises(KeyError):
            gerenciador.continuar("ausente")
        with self.assertRaises(KeyError):
            gerenciador.cancelar("ausente")

    def test_cancela_inspecao_pausada(self):
        combinacoes = tuple((1, 2, 3, 4, 5, 6) for _ in range(10))
        gerenciador = GerenciadorTestesDirigidosValidacaoNova(
            lambda grupo, filtro: {
                "id_grupo": grupo, "nome_grupo": "Grupo",
                "id_filtro": filtro, "nome_filtro": "Filtro",
                "tentativas_geracao": 10, "combinacoes": combinacoes,
            },
            lambda _filtro, _itens: {"avaliacoes": tuple({
                "numero": indice, "combinacao": list(item), "detectada": True,
                "desenho": {"dezenas_marcadas": list(item), "segmentos": []},
            } for indice, item in enumerate(combinacoes, start=1))},
        )
        criado = gerenciador.criar(2, 12)
        gerenciador.testar(criado["id"])

        cancelado = gerenciador.cancelar(criado["id"])

        self.assertEqual("CANCELADO", cancelado["estado"])
        self.assertIsNone(cancelado["ocorrencia_atual"])

    def test_concluir_vai_diretamente_ao_resultado(self):
        combinacoes = tuple((1, 2, 3, 4, 5, 6) for _ in range(10))
        gerenciador = GerenciadorTestesDirigidosValidacaoNova(
            lambda grupo, filtro: {
                "id_grupo": grupo, "nome_grupo": "Grupo",
                "id_filtro": filtro, "nome_filtro": "Filtro",
                "tentativas_geracao": 10, "combinacoes": combinacoes,
            },
            lambda _filtro, _itens: {"avaliacoes": tuple({
                "numero": indice, "combinacao": list(item), "detectada": True,
                "desenho": {"dezenas_marcadas": list(item), "segmentos": []},
            } for indice, item in enumerate(combinacoes, start=1))},
        )
        criado = gerenciador.criar(2, 12)
        gerenciador.testar(criado["id"])

        concluido = gerenciador.concluir(criado["id"])

        self.assertEqual("TESTADO", concluido["estado"])
        self.assertEqual(10, concluido["resultado"]["ocorrencias_detectadas"])
        self.assertIsNone(concluido["ocorrencia_atual"])


if __name__ == "__main__":
    unittest.main()
