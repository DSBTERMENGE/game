from dataclasses import asdict
import unittest

from msen.services import montar_catalogo_filtros_validacao


class CatalogoFiltrosValidacaoNovaTestCase(unittest.TestCase):
    def setUp(self):
        self.linhas = (
            (9, "1 linha e 1 coluna", 16, "Linha e coluna", "Descrição 16", "funcao.16"),
            (1, "Sequenciais", 3, "Mais de três", "Descrição 3", "funcao.3"),
            (1, "Sequenciais", 2, "Três dezenas", "Descrição 2", "funcao.2"),
            (7, "Sem implementação", 70, "Futuro", "Descrição", None),
            (8, "Função inválida", 80, "Quebrado", "Descrição", "funcao.invalida"),
        )

    def test_lista_somente_executaveis_ordenados_por_nome(self):
        catalogo = montar_catalogo_filtros_validacao(
            self.linhas,
            funcao_disponivel=lambda nome: bool(nome and nome != "funcao.invalida"),
        )

        self.assertEqual((9, 1), tuple(item.id_grupo for item in catalogo))
        self.assertEqual(
            ("Mais de três", "Três dezenas"),
            tuple(item.nome for item in catalogo[1].filtros),
        )
        self.assertEqual((16,), tuple(item.id_filtro for item in catalogo[0].filtros))

    def test_omite_grupos_sem_filtro_executavel(self):
        catalogo = montar_catalogo_filtros_validacao(
            self.linhas,
            funcao_disponivel=lambda nome: nome in {"funcao.16", "funcao.2", "funcao.3"},
        )

        self.assertNotIn(7, {item.id_grupo for item in catalogo})
        self.assertNotIn(8, {item.id_grupo for item in catalogo})

    def test_contrato_nao_expoe_codigo_nem_funcao(self):
        catalogo = montar_catalogo_filtros_validacao(
            self.linhas[:1], funcao_disponivel=lambda _nome: True
        )
        contrato = asdict(catalogo[0])
        texto = repr(contrato).lower()

        self.assertEqual({"id_grupo", "nome", "filtros"}, set(contrato))
        self.assertEqual(
            {"id_filtro", "nome", "descricao"},
            set(contrato["filtros"][0]),
        )
        self.assertNotIn("codigo", texto)
        self.assertNotIn("funcao", texto)

    def test_rejeita_identificadores_e_nomes_invalidos(self):
        for linha in (
            (0, "Grupo", 1, "Filtro", "Descrição", "funcao"),
            (1, "Grupo", 0, "Filtro", "Descrição", "funcao"),
            (1, " ", 1, "Filtro", "Descrição", "funcao"),
            (1, "Grupo", 1, " ", "Descrição", "funcao"),
        ):
            with self.subTest(linha=linha), self.assertRaises(ValueError):
                montar_catalogo_filtros_validacao(
                    (linha,), funcao_disponivel=lambda _nome: True
                )

    def test_rejeita_nomes_divergentes_para_o_mesmo_grupo(self):
        with self.assertRaises(ValueError):
            montar_catalogo_filtros_validacao(
                (
                    (1, "Grupo A", 1, "Filtro 1", "", "funcao.1"),
                    (1, "Grupo B", 2, "Filtro 2", "", "funcao.2"),
                ),
                funcao_disponivel=lambda _nome: True,
            )


if __name__ == "__main__":
    unittest.main()
