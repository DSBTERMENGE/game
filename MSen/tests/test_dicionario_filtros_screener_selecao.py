import unittest

from msen.services.dicionario_filtros_screener_selecao import (
    ErroDicionarioFiltrosScreener,
    montar_dicionario_filtros,
)


def filtro(**alteracao):
    dados = {
        "grupo": "estatisticos", "chave": "soma", "id_filtro": 1,
        "id_grupo": None, "nome_filtro": "Soma", "tipo_resultado": "NUMERICO",
        "metodo_comparacao": "FAIXA",
        "referencia": {"limite_inferior": 21, "limite_superior": 300},
    }
    dados.update(alteracao)
    return dados


class DicionarioFiltrosScreenerSelecaoTestCase(unittest.TestCase):
    def test_monta_tres_grupos_sem_funcoes(self):
        dicionario = montar_dicionario_filtros(
            estado_referencias={"atualizado": True, "quantidade_resultados": 3069},
            limite_raridade="10.000000",
            filtros=(
                filtro(),
                filtro(
                    grupo="padroes", chave="duas_linhas", id_filtro=21,
                    id_grupo=7, nome_filtro="Dezenas em duas linhas",
                    tipo_resultado="BOOLEANO", metodo_comparacao="RARIDADE",
                    referencia={True: "1.042685", False: "98.957315"},
                ),
            ),
        )
        self.assertEqual(3069, dicionario["controle"]["quantidade_resultados"])
        self.assertEqual({"soma"}, set(dicionario["estatisticos"]))
        self.assertEqual({}, dicionario["geometricos"])
        self.assertEqual({"duas_linhas"}, set(dicionario["padroes"]))
        self.assertNotIn("funcao", dicionario["padroes"]["duas_linhas"])

    def test_recusa_referencias_desatualizadas(self):
        with self.assertRaises(ErroDicionarioFiltrosScreener):
            montar_dicionario_filtros(
                estado_referencias={"atualizado": False, "quantidade_resultados": 3069},
                limite_raridade=10, filtros=(),
            )

    def test_recusa_qualquer_campo_de_funcao(self):
        for campo in ("funcao", "funcao_python", "funcao_detectora"):
            with self.subTest(campo=campo), self.assertRaises(ErroDicionarioFiltrosScreener):
                montar_dicionario_filtros(
                    estado_referencias={"atualizado": True, "quantidade_resultados": 3069},
                    limite_raridade=10, filtros=(filtro(**{campo: "qualquer"}),),
                )

    def test_recusa_chave_desconhecida_ou_duplicada(self):
        estado = {"atualizado": True, "quantidade_resultados": 3069}
        with self.assertRaises(ErroDicionarioFiltrosScreener):
            montar_dicionario_filtros(
                estado_referencias=estado, limite_raridade=10,
                filtros=(filtro(chave="inventada"),),
            )
        with self.assertRaises(ErroDicionarioFiltrosScreener):
            montar_dicionario_filtros(
                estado_referencias=estado, limite_raridade=10,
                filtros=(filtro(), filtro(id_filtro=2)),
            )


if __name__ == "__main__":
    unittest.main()
