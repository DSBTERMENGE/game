from dataclasses import dataclass
import unittest

from msen.screener import DecisaoCriterio, simular_modo_sombra


@dataclass
class CriterioSombraArtificial:
    codigo: str = "SOMBRA"

    def avaliar(self, combinacao):
        marca = combinacao[0] % 2 == 0
        return DecisaoCriterio(True, self.codigo, {"marcaria_exclusao": marca})


class RelogioArtificial:
    def __init__(self, *valores):
        self.valores = iter(valores)

    def __call__(self):
        return next(self.valores)


class SimulacaoSombraTestCase(unittest.TestCase):
    def test_conta_marcas_saldo_e_preserva_todas(self):
        combinacoes = tuple((n, 10, 20, 30, 40, 50) for n in range(1, 7))
        resultado = simular_modo_sombra(
            combinacoes,
            CriterioSombraArtificial(),
            semente=42,
            limite_exemplos=2,
            relogio=RelogioArtificial(1.0, 1.25),
        )
        self.assertEqual(6, resultado.total_avaliado)
        self.assertEqual(3, resultado.total_marcado)
        self.assertEqual(50.0, resultado.percentual_marcado)
        self.assertEqual(3, resultado.saldo_hipotetico)
        self.assertEqual(6, resultado.total_aprovado_real)
        self.assertEqual(0, resultado.total_excluido_real)
        self.assertEqual((combinacoes[1], combinacoes[3]), resultado.exemplos_marcados)
        self.assertEqual(0.25, resultado.duracao_segundos)

    def test_amostra_vazia_tem_percentual_zero(self):
        resultado = simular_modo_sombra(
            (), CriterioSombraArtificial(), semente=1
        )
        self.assertEqual(0.0, resultado.percentual_marcado)

    def test_rejeita_criterio_que_reprova_realmente(self):
        class CriterioInvalido:
            codigo = "INVALIDO"

            def avaliar(self, combinacao):
                return DecisaoCriterio(False, self.codigo, {"marcaria_exclusao": True})

        with self.assertRaises(ValueError):
            simular_modo_sombra(((1, 2, 3, 4, 5, 6),), CriterioInvalido(), semente=1)


if __name__ == "__main__":
    unittest.main()
