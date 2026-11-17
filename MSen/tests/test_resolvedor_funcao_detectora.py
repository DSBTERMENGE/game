"""Testes do resolvedor isolado das funções detectoras cadastradas."""

import unittest
from unittest.mock import patch

from msen.padroes import (
    ErroResolucaoDetector,
    executar_funcao_detectora,
    resolver_funcao_detectora,
)
from msen.padroes.sequenciais import detectar_duas_dezenas_sequenciais


FUNCAO_VALIDA = (
    "msen.padroes.sequenciais.detectar_duas_dezenas_sequenciais"
)


class ResolvedorFuncaoDetectoraTest(unittest.TestCase):
    def assertErro(self, codigo, chamada):
        with self.assertRaises(ErroResolucaoDetector) as contexto:
            chamada()
        self.assertEqual(codigo, contexto.exception.codigo)

    def test_resolve_funcao_qualificada_autorizada(self):
        self.assertIs(
            detectar_duas_dezenas_sequenciais,
            resolver_funcao_detectora(FUNCAO_VALIDA),
        )

    def test_rejeita_funcao_ausente(self):
        for valor in (None, "", "   "):
            with self.subTest(valor=valor):
                self.assertErro(
                    "FUNCAO_NAO_INFORMADA",
                    lambda valor=valor: resolver_funcao_detectora(valor),
                )

    def test_rejeita_modulo_fora_do_namespace(self):
        self.assertErro(
            "MODULO_NAO_AUTORIZADO",
            lambda: resolver_funcao_detectora("os.path.exists"),
        )

    def test_informa_modulo_inexistente(self):
        self.assertErro(
            "MODULO_NAO_ENCONTRADO",
            lambda: resolver_funcao_detectora("msen.padroes.inexistente.detectar"),
        )

    def test_informa_funcao_inexistente(self):
        self.assertErro(
            "FUNCAO_NAO_ENCONTRADA",
            lambda: resolver_funcao_detectora(
                "msen.padroes.sequenciais.funcao_inexistente"
            ),
        )

    def test_rejeita_objeto_nao_chamavel(self):
        self.assertErro(
            "FUNCAO_NAO_CHAMAVEL",
            lambda: resolver_funcao_detectora("msen.padroes.sequenciais.__doc__"),
        )

    def test_executa_detector_e_devolve_booleano(self):
        self.assertTrue(executar_funcao_detectora(FUNCAO_VALIDA, (1, 2, 10, 20, 30, 40)))
        self.assertFalse(executar_funcao_detectora(FUNCAO_VALIDA, (1, 3, 10, 20, 30, 40)))

    def test_rejeita_resposta_nao_booleana(self):
        with patch(
            "msen.padroes.resolvedor.resolver_funcao_detectora",
            return_value=lambda dezenas: 1,
        ):
            self.assertErro(
                "RESPOSTA_DETECTOR_INVALIDA",
                lambda: executar_funcao_detectora(FUNCAO_VALIDA, (1, 2, 3, 4, 5, 6)),
            )


if __name__ == "__main__":
    unittest.main()
