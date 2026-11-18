import inspect
import unittest

from msen.screener.orquestrador import orquestrar_aplicacao_screener


def filtro_faixa(identificador, nome, inferior=0, superior=1000):
    return {
        "id_filtro": identificador,
        "id_grupo": None,
        "nome_filtro": nome,
        "tipo_resultado": "NUMERICO",
        "metodo_comparacao": "FAIXA",
        "referencia": {
            "limite_inferior": inferior,
            "limite_superior": superior,
        },
    }


def entradas(filtros, combinacoes=((1, 2, 3, 4, 5, 6),)):
    return (
        {
            "origem": "TESTE",
            "quantidade_combinacoes": len(combinacoes),
            "itens": iter(combinacoes),
        },
        {
            "controle": {
                "atualizado": True,
                "quantidade_resultados": 3069,
                "limite_raridade": 10,
            },
            **filtros,
        },
    )


class OrquestradorScreenerTestCase(unittest.TestCase):
    def test_documenta_nome_e_tres_membros_no_codigo(self):
        fonte = inspect.getsource(orquestrar_aplicacao_screener)
        self.assertIn("função orquestradora central", orquestrar_aplicacao_screener.__doc__)
        self.assertIn("MEMBRO 1 — FILTROS ESTATÍSTICOS", fonte)
        self.assertIn("MEMBRO 2 — FILTROS GEOMÉTRICOS", fonte)
        self.assertIn("MEMBRO 3 — FILTROS DE PADRÕES", fonte)

    def test_executa_os_tres_membros_na_ordem(self):
        filtros = {
            "estatisticos": {"soma": filtro_faixa(1, "Estatístico")},
            "geometricos": {"extensao": filtro_faixa(2, "Geométrico")},
            "padroes": {"duas_linhas": {
                "id_filtro": 3, "id_grupo": 1, "nome_filtro": "Padrão",
                "tipo_resultado": "BOOLEANO", "metodo_comparacao": "RARIDADE",
                "referencia": {True: 100, False: 100},
            }},
        }
        resultado = orquestrar_aplicacao_screener(*entradas(filtros))

        self.assertEqual(1, resultado["total_aprovado"])
        self.assertEqual(((1, 2, 3, 4, 5, 6),), resultado["combinacoes_aprovadas"])

    def test_reprovacao_estatistica_interrompe_demais_membros(self):
        filtros = {
            "estatisticos": {"soma": filtro_faixa(1, "Estatístico", 0, 10)},
            "geometricos": {"extensao": filtro_faixa(2, "Geométrico")},
            "padroes": {},
        }
        resultado = orquestrar_aplicacao_screener(*entradas(filtros))

        self.assertEqual("ESTATISTICO", resultado["exclusoes"][0]["membro"])

    def test_reprovacao_geometrica_impede_membro_de_padroes(self):
        filtros = {
            "estatisticos": {"soma": filtro_faixa(1, "Estatístico")},
            "geometricos": {"extensao": filtro_faixa(2, "Geométrico", 0, 1)},
            "padroes": {},
        }
        resultado = orquestrar_aplicacao_screener(*entradas(filtros))

        self.assertEqual("GEOMETRICO", resultado["exclusoes"][0]["membro"])

    def test_padrao_raro_exclui_pelo_percentual_da_resposta(self):
        filtro = {
            "id_filtro": 21,
            "id_grupo": 8,
            "nome_filtro": "Duas linhas",
            "tipo_resultado": "BOOLEANO",
            "metodo_comparacao": "RARIDADE",
            "referencia": {True: 1.042685, False: 1.042685},
        }
        resultado = orquestrar_aplicacao_screener(*entradas({
            "estatisticos": {}, "geometricos": {}, "padroes": {"duas_linhas": filtro},
        }))

        self.assertEqual(0, resultado["total_aprovado"])
        self.assertEqual(1, resultado["total_excluido"])
        self.assertEqual("PADRAO", resultado["exclusoes"][0]["membro"])
        self.assertEqual("1.042685", str(resultado["exclusoes"][0]["percentual"]))

    def test_fecha_varias_combinacoes_aprovadas_e_excluidas(self):
        filtro = filtro_faixa(1, "Soma", 27, 100)
        combinacoes = (
            (1, 2, 3, 4, 5, 6),
            (2, 3, 4, 5, 6, 7),
            (3, 4, 5, 6, 7, 8),
        )
        resultado = orquestrar_aplicacao_screener(*entradas({
            "estatisticos": {"soma": filtro}, "geometricos": {}, "padroes": {},
        }, combinacoes))

        self.assertEqual(3, resultado["total_recebido"])
        self.assertEqual(2, resultado["total_aprovado"])
        self.assertEqual(1, resultado["total_excluido"])
        self.assertEqual(
            combinacoes[1:], resultado["combinacoes_aprovadas"]
        )

    def test_interrompe_ao_atingir_quantidade_maxima_aprovada(self):
        combinacoes = (
            (1, 2, 3, 4, 5, 6),
            (2, 3, 4, 5, 6, 7),
            (3, 4, 5, 6, 7, 8),
        )
        resultado = orquestrar_aplicacao_screener(
            *entradas({"estatisticos": {}, "geometricos": {}, "padroes": {}}, combinacoes),
            limite_aprovadas=2,
        )
        self.assertEqual(2, resultado["total_recebido"])
        self.assertEqual(3, resultado["total_universo"])
        self.assertEqual(2, resultado["total_aprovado"])
        self.assertTrue(resultado["interrompido_por_limite"])


if __name__ == "__main__":
    unittest.main()
