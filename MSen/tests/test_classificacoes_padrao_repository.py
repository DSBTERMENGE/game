from dataclasses import FrozenInstanceError
from datetime import datetime, timezone
import unittest

from msen.database import RepositorioClassificacoesPadrao
from msen.database.classificacoes_padrao_repository import (
    _id_positivo,
    _linha_para_classificacao,
)
from msen.modelos import ClassificacaoPadrao


class ModeloClassificacaoPadraoTestCase(unittest.TestCase):
    def setUp(self):
        self.momento = datetime(2026, 10, 28, tzinfo=timezone.utc)

    def test_mapeia_as_seis_colunas_para_modelo_imutavel(self):
        classificacao = _linha_para_classificacao(
            (1, 2, 3, 4, 5, self.momento)
        )
        self.assertEqual(
            ClassificacaoPadrao(
                1,
                2,
                3,
                4,
                5,
                self.momento,
            ),
            classificacao,
        )
        with self.assertRaises(FrozenInstanceError):
            classificacao.id_padrao = 9  # type: ignore[misc]

    def test_rejeita_quantidade_incorreta_de_colunas(self):
        with self.assertRaises(ValueError):
            _linha_para_classificacao((1, 2, 3))

    def test_exige_padrao_real_e_data_com_fuso(self):
        with self.assertRaises(TypeError):
            ClassificacaoPadrao(1, 2, 3, None, 1, self.momento)  # type: ignore[arg-type]
        with self.assertRaisesRegex(ValueError, "fuso horário"):
            ClassificacaoPadrao(1, 2, 3, 4, 1, datetime(2026, 10, 28))

    def test_valida_identificadores_e_versao(self):
        for campo, valor in (("id_classificacao", 0), ("id_resultado", 0), ("id_grupo", -1)):
            argumentos = {
                "id_classificacao": 1,
                "id_resultado": 2,
                "id_grupo": 3,
                "id_padrao": 4,
                "versao_calculo": 1,
                "calculado_em": self.momento,
            }
            argumentos[campo] = valor
            with self.subTest(campo=campo):
                with self.assertRaises(ValueError):
                    ClassificacaoPadrao(**argumentos)
        with self.assertRaises(ValueError):
            ClassificacaoPadrao(1, 2, 3, 4, 0, self.momento)

    def test_consultas_validam_id_isolado(self):
        self.assertEqual(7, _id_positivo("id_grupo", 7))
        for valor in (0, -1):
            with self.assertRaises(ValueError):
                _id_positivo("id_grupo", valor)
        for valor in (True, "1"):
            with self.assertRaises(TypeError):
                _id_positivo("id_grupo", valor)  # type: ignore[arg-type]

    def test_repositorio_exige_conexao_psycopg(self):
        with self.assertRaises(TypeError):
            RepositorioClassificacoesPadrao(object())  # type: ignore[arg-type]


if __name__ == "__main__":
    unittest.main()
