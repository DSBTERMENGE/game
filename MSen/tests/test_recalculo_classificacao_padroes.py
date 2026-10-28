from dataclasses import FrozenInstanceError
from decimal import Decimal
import unittest

from msen.services.classificacao_padroes import _percentual, _validar_limite_raridade
from msen.services import (
    ClassePerfilPadrao,
    ContagemClassificacao,
    RelatorioRecalculoClassificacao,
    recalcular_classificacoes_grupo_sequenciais,
)


class RelatorioRecalculoClassificacaoTestCase(unittest.TestCase):
    def test_relatorio_e_contagens_sao_imutaveis(self):
        contagem = ContagemClassificacao("PD_001", 2)
        relatorio = RelatorioRecalculoClassificacao("PG_001", 1, 2, (contagem,))
        with self.assertRaises(FrozenInstanceError):
            contagem.quantidade = 3  # type: ignore[misc]
        with self.assertRaises(FrozenInstanceError):
            relatorio.resultados_analisados = 3  # type: ignore[misc]

    def test_recalculo_exige_conexao_psycopg(self):
        with self.assertRaises(TypeError):
            recalcular_classificacoes_grupo_sequenciais(object())  # type: ignore[arg-type]

    def test_percentual_usa_seis_casas_e_amostra_vazia_segura(self):
        self.assertEqual(Decimal("33.333333"), _percentual(1, 3))
        self.assertEqual(Decimal("0.000000"), _percentual(0, 0))

    def test_limite_de_raridade_e_normalizado_e_validado(self):
        self.assertEqual(Decimal("10.000000"), _validar_limite_raridade("10"))
        for valor in ("-0.1", "100.1", "NaN", "texto"):
            with self.subTest(valor=valor):
                with self.assertRaises(ValueError):
                    _validar_limite_raridade(valor)
        with self.assertRaises(TypeError):
            _validar_limite_raridade(True)

    def test_classe_do_perfil_e_imutavel(self):
        classe = ClassePerfilPadrao(
            "PD_001",
            1,
            Decimal("25.000000"),
            Decimal("33.333333"),
            None,
            None,
            False,
        )
        with self.assertRaises(FrozenInstanceError):
            classe.raro = True  # type: ignore[misc]


if __name__ == "__main__":
    unittest.main()
