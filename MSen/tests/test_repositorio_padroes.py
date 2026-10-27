from decimal import Decimal
import unittest

from msen.database import ErroRepositorioPadrao, PadraoPersistido, RepositorioPadroes
from msen.database.padroes_repository import (
    _linha_para_padrao,
    _validar_codigo,
    _validar_texto,
)


class MapeamentoRepositorioPadroesTestCase(unittest.TestCase):
    def test_mapeia_as_sete_colunas_sem_converter_decimais_para_float(self):
        padrao = _linha_para_padrao(
            (1, "PD_001", "Duas", "Descrição", 2, Decimal("15.000000"), Decimal("0.000000"))
        )

        self.assertEqual(
            PadraoPersistido(
                1,
                "PD_001",
                "Duas",
                "Descrição",
                2,
                Decimal("15.000000"),
                Decimal("0.000000"),
            ),
            padrao,
        )
        self.assertIsInstance(padrao.intervalo_medio, Decimal)
        self.assertIsInstance(padrao.desv_padrao, Decimal)

    def test_rejeita_quantidade_incorreta_de_colunas(self):
        with self.assertRaises(ValueError):
            _linha_para_padrao((1, 2, 3))

    def test_valida_codigo_e_textos_antes_do_sql(self):
        self.assertEqual("PD_001", _validar_codigo("PD_001"))
        self.assertEqual("Nome", _validar_texto("padrao_nome", "  Nome  "))

        for codigo in ("P1", "pd_001", "PD_01", ""):
            with self.subTest(codigo=codigo):
                with self.assertRaises(ValueError):
                    _validar_codigo(codigo)
        for texto in ("", "   ", None):
            with self.subTest(texto=texto):
                with self.assertRaises(ValueError):
                    _validar_texto("padrao_nome", texto)  # type: ignore[arg-type]

    def test_repositorio_exige_conexao_psycopg(self):
        with self.assertRaises(TypeError):
            RepositorioPadroes(object())  # type: ignore[arg-type]

    def test_erro_preserva_codigo_funcional_sem_dados_de_conexao(self):
        erro = ErroRepositorioPadrao(
            "TESTE", "Mensagem segura.", padrao_cod="PD_001"
        )
        self.assertEqual("TESTE", erro.codigo)
        self.assertEqual("PD_001", erro.padrao_cod)
        self.assertEqual("Mensagem segura.", str(erro))


if __name__ == "__main__":
    unittest.main()
