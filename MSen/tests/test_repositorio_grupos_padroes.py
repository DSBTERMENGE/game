"""Testes unitários do contrato do repositório de grupos de padrões."""

import unittest

from msen.database import (
    ErroRepositorioGrupoPadrao,
    GrupoPadraoPersistido,
    RepositorioGruposPadroes,
)
from msen.database.grupos_padroes_repository import (
    _linha_para_grupo,
    _validar_codigo_grupo,
    _validar_texto_grupo,
)


class RepositorioGruposPadroesTestCase(unittest.TestCase):
    """Confere mapeamento e validações que não precisam de PostgreSQL."""

    def test_mapeia_as_quatro_colunas(self):
        grupo = _linha_para_grupo((1, "PG_001", "Sequenciais", "Descrição"))
        self.assertEqual(
            GrupoPadraoPersistido(1, "PG_001", "Sequenciais", "Descrição"),
            grupo,
        )

    def test_rejeita_quantidade_incorreta_de_colunas(self):
        with self.assertRaises(ValueError):
            _linha_para_grupo((1, 2, 3))

    def test_valida_codigo_e_textos_antes_do_sql(self):
        self.assertEqual("PG_001", _validar_codigo_grupo("PG_001"))
        self.assertEqual("Nome", _validar_texto_grupo("grupo_nome", " Nome "))
        for codigo in ("G1", "pg_001", "PG_01", ""):
            with self.subTest(codigo=codigo), self.assertRaises(ValueError):
                _validar_codigo_grupo(codigo)
        for texto in ("", "   ", None):
            with self.subTest(texto=texto), self.assertRaises(ValueError):
                _validar_texto_grupo("grupo_nome", texto)  # type: ignore[arg-type]

    def test_repositorio_exige_conexao_psycopg(self):
        with self.assertRaises(TypeError):
            RepositorioGruposPadroes(object())  # type: ignore[arg-type]

    def test_erro_preserva_codigo_funcional(self):
        erro = ErroRepositorioGrupoPadrao(
            "TESTE", "Mensagem segura.", grupo_cod="PG_001"
        )
        self.assertEqual("TESTE", erro.codigo)
        self.assertEqual("PG_001", erro.grupo_cod)
        self.assertEqual("Mensagem segura.", str(erro))


if __name__ == "__main__":
    unittest.main()
