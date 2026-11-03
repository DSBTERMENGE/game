from decimal import Decimal
import unittest

from msen.database.pesquisa_selecao_repository import (
    AvaliacaoDezenaPesquisaEntrada,
    _quantidade_combinacoes,
    _validar_avaliacoes,
)


def avaliacao_sem_base(dezena: int) -> AvaliacaoDezenaPesquisaEntrada:
    return AvaliacaoDezenaPesquisaEntrada(
        dezena=dezena,
        estado_avaliacao="SEM_BASE",
        ultima_ocorrencia=None,
        quantidade_intervalos=0,
        media_intervalos=None,
        desvio_padrao=None,
        centro_original=None,
        centro_ajustado=None,
        limite_inferior_exato=None,
        limite_superior_exato=None,
        limite_inferior=None,
        limite_superior=None,
        distancia_normalizada=None,
        distancia_absoluta=None,
        posicao_ranking=None,
        aprovada=False,
        retornada=False,
    )


class RepositorioPesquisaSelecaoTest(unittest.TestCase):
    def test_exige_exatamente_uma_avaliacao_para_cada_dezena(self) -> None:
        avaliacoes = tuple(avaliacao_sem_base(dezena) for dezena in range(1, 61))
        self.assertEqual(_validar_avaliacoes(avaliacoes), avaliacoes)

        with self.assertRaisesRegex(ValueError, "exatamente"):
            _validar_avaliacoes(avaliacoes[:-1])
        with self.assertRaisesRegex(ValueError, "exatamente"):
            _validar_avaliacoes(avaliacoes[:-1] + (avaliacao_sem_base(59),))

    def test_rejeita_dezena_retornada_sem_aprovacao(self) -> None:
        avaliacoes = [avaliacao_sem_base(dezena) for dezena in range(1, 61)]
        original = avaliacoes[9]
        avaliacoes[9] = AvaliacaoDezenaPesquisaEntrada(
            **{
                campo: getattr(original, campo)
                for campo in original.__dataclass_fields__
            } | {"retornada": True}
        )
        with self.assertRaisesRegex(ValueError, "retornada"):
            _validar_avaliacoes(avaliacoes)

    def test_calcula_quantidade_bruta_de_combinacoes(self) -> None:
        esperados = {5: 0, 6: 1, 7: 7, 8: 28, 15: 5005}
        for quantidade, esperado in esperados.items():
            with self.subTest(quantidade=quantidade):
                self.assertEqual(_quantidade_combinacoes(quantidade), esperado)


if __name__ == "__main__":
    unittest.main()
