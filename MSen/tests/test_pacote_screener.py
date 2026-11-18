import unittest

from msen.screener.pacote import ErroPacoteScreener, validar_entradas_screener


def somar(dezenas):
    return sum(dezenas)


def detectar(_dezenas):
    return False


def criar_entradas():
    combinacoes = {
            "origem": "SELECAO_DE_DEZENAS",
            "quantidade_combinacoes": 2,
            "itens": [(6, 5, 4, 3, 2, 1), (7, 8, 9, 10, 11, 12)],
    }
    filtros = {
            "controle": {
                "atualizado": True,
                "quantidade_resultados": 3069,
                "limite_raridade": "10",
            },
            "estatisticos": {"soma": {
                "id_filtro": 1,
                "id_grupo": None,
                "nome_filtro": "Soma",
                "tipo_resultado": "NUMERICO",
                "metodo_comparacao": "FAIXA",
            "referencia": {"limite_inferior": 10, "limite_superior": 200},
            }},
            "geometricos": {},
            "padroes": {"duas_linhas": {
                "id_filtro": 21,
                "id_grupo": 8,
                "id_padrao": 17,
                "nome_filtro": "Dezenas em duas linhas",
                "tipo_resultado": "BOOLEANO",
                "metodo_comparacao": "RARIDADE",
                "referencia": {True: 1, False: 99},
            }},
    }
    return combinacoes, filtros


class PacoteScreenerTestCase(unittest.TestCase):
    def test_normaliza_os_dois_dicionarios(self):
        combinacoes, filtros = validar_entradas_screener(*criar_entradas())

        self.assertEqual((1, 2, 3, 4, 5, 6), next(iter(combinacoes["itens"])))
        self.assertEqual("10", str(filtros["controle"]["limite_raridade"]))
        self.assertEqual((1,), tuple(
            item["id_filtro"] for item in filtros["estatisticos"].values()
        ))
        self.assertEqual({True: 1, False: 99}, filtros["padroes"]["duas_linhas"]["referencia"])

    def test_exige_ao_menos_uma_combinacao(self):
        combinacoes, filtros = criar_entradas()
        combinacoes["quantidade_combinacoes"] = 0
        with self.assertRaises(ErroPacoteScreener):
            validar_entradas_screener(combinacoes, filtros)

    def test_rejeita_combinacao_invalida(self):
        for combinacao in ((1, 2, 3), (1, 2, 3, 4, 5, 5), (1, 2, 3, 4, 5, 61)):
            with self.subTest(combinacao=combinacao):
                combinacoes, filtros = criar_entradas()
                combinacoes["itens"] = [combinacao]
                normalizadas, _ = validar_entradas_screener(combinacoes, filtros)
                with self.assertRaises(ErroPacoteScreener):
                    tuple(normalizadas["itens"])

    def test_exige_os_tres_grupos_de_filtros(self):
        combinacoes, filtros = criar_entradas()
        del filtros["geometricos"]
        with self.assertRaises(ErroPacoteScreener):
            validar_entradas_screener(combinacoes, filtros)

    def test_rejeita_id_de_filtro_repetido(self):
        combinacoes, filtros = criar_entradas()
        filtros["padroes"]["duas_linhas"]["id_filtro"] = 1
        with self.assertRaises(ErroPacoteScreener):
            validar_entradas_screener(combinacoes, filtros)

    def test_nao_exige_nome_nem_objeto_de_funcao(self):
        combinacoes, filtros = criar_entradas()
        _, normalizados = validar_entradas_screener(combinacoes, filtros)
        self.assertNotIn("funcao", normalizados["estatisticos"]["soma"])

    def test_exige_id_grupo_explicito(self):
        combinacoes, filtros = criar_entradas()
        del filtros["estatisticos"]["soma"]["id_grupo"]
        with self.assertRaises(ErroPacoteScreener):
            validar_entradas_screener(combinacoes, filtros)

    def test_exige_referencia_dentro_de_cada_filtro(self):
        combinacoes, filtros = criar_entradas()
        del filtros["padroes"]["duas_linhas"]["referencia"]
        with self.assertRaises(ErroPacoteScreener):
            validar_entradas_screener(combinacoes, filtros)


if __name__ == "__main__":
    unittest.main()
