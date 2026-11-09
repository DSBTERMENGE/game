from decimal import Decimal
import unittest

from msen.services import (
    ConfiguracaoSelecaoDezenas,
    ErroSelecaoDezenas,
    EstatisticaDezenaCorte,
    selecionar_dezenas_para_alvo,
)


def configuracao(*, k="0.5", j="0", modo="MAX", quantidade=None):
    return ConfiguracaoSelecaoDezenas(
        nome="Teste", fator_k=Decimal(k), fator_j=Decimal(j),
        modo_quantidade=modo, quantidade_dezenas=quantidade,
        versao_calculo=1,
    )


def estatisticas_com(*itens: EstatisticaDezenaCorte):
    por_dezena = {item.dezena: item for item in itens}
    return tuple(
        por_dezena.get(dezena, EstatisticaDezenaCorte(dezena, None, 0, None, None))
        for dezena in range(1, 61)
    )


class SelecaoDezenasTest(unittest.TestCase):
    def test_caso_manual_sem_deslocamento_e_limites_inclusivos(self) -> None:
        base = EstatisticaDezenaCorte(10, 480, 20, Decimal("25"), Decimal("6"))
        for alvo, aprovada in ((501, False), (502, True), (508, True), (509, False)):
            with self.subTest(alvo=alvo):
                resultado = selecionar_dezenas_para_alvo(
                    estatisticas_com(base), configuracao(),
                    numero_concurso_alvo=alvo, numero_concurso_corte=499,
                )
                avaliacao = resultado.avaliacoes[9]
                self.assertEqual(avaliacao.aprovada, aprovada)
                self.assertEqual((avaliacao.limite_inferior, avaliacao.limite_superior), (502, 508))
                self.assertIn(
                    "Aprovada" if aprovada else "fora da faixa",
                    avaliacao.motivo_decisao,
                )

    def test_deslocamento_j_move_a_faixa_sem_alterar_a_largura(self) -> None:
        base = EstatisticaDezenaCorte(10, 480, 20, Decimal("25"), Decimal("6"))
        resultado = selecionar_dezenas_para_alvo(
            estatisticas_com(base), configuracao(j="0.25"),
            numero_concurso_alvo=510, numero_concurso_corte=499,
        )
        avaliacao = resultado.avaliacoes[9]
        self.assertEqual(avaliacao.centro_ajustado, Decimal("506.500000"))
        self.assertEqual((avaliacao.limite_inferior, avaliacao.limite_superior), (503, 510))
        self.assertTrue(avaliacao.retornada)

    def test_modo_fixo_reduz_por_ranking_sem_completar_fora_da_faixa(self) -> None:
        bases = tuple(
            EstatisticaDezenaCorte(
                dezena, 90, 10, Decimal("10"), Decimal(str(desvio))
            )
            for dezena, desvio in ((1, 10), (2, 8), (3, 6), (4, 4), (5, 2))
        )
        resultado = selecionar_dezenas_para_alvo(
            estatisticas_com(*bases),
            configuracao(k="1", modo="FIXA", quantidade=6),
            numero_concurso_alvo=100, numero_concurso_corte=99,
        )
        self.assertEqual(resultado.dezenas_aprovadas, (1, 2, 3, 4, 5))
        self.assertEqual(resultado.dezenas_retornadas, (1, 2, 3, 4, 5))
        self.assertTrue(resultado.limite_nao_atingido)

    def test_modo_fixo_conserva_as_melhores_aprovadas(self) -> None:
        bases = tuple(
            EstatisticaDezenaCorte(
                dezena, 90, 10, Decimal(str(media)), Decimal("10")
            )
            for dezena, media in ((1, 10), (2, 11), (3, 12), (4, 13), (5, 14), (6, 15), (7, 16))
        )
        resultado = selecionar_dezenas_para_alvo(
            estatisticas_com(*bases),
            configuracao(k="1", modo="FIXA", quantidade=6),
            numero_concurso_alvo=100, numero_concurso_corte=99,
        )
        self.assertEqual(resultado.dezenas_retornadas, (1, 2, 3, 4, 5, 6))
        self.assertFalse(resultado.avaliacoes[6].retornada)

    def test_desvio_zero_aprova_somente_o_centro(self) -> None:
        base = EstatisticaDezenaCorte(7, 90, 4, Decimal("10"), Decimal("0"))
        no_centro = selecionar_dezenas_para_alvo(
            estatisticas_com(base), configuracao(),
            numero_concurso_alvo=100, numero_concurso_corte=99,
        )
        fora = selecionar_dezenas_para_alvo(
            estatisticas_com(base), configuracao(),
            numero_concurso_alvo=101, numero_concurso_corte=99,
        )
        self.assertTrue(no_centro.avaliacoes[6].aprovada)
        self.assertFalse(fora.avaliacoes[6].aprovada)
        self.assertIsNone(fora.avaliacoes[6].distancia_normalizada)

    def test_sem_base_completa_torna_alvo_nao_avaliavel(self) -> None:
        resultado = selecionar_dezenas_para_alvo(
            estatisticas_com(), configuracao(),
            numero_concurso_alvo=500, numero_concurso_corte=499,
        )
        self.assertFalse(resultado.avaliavel)
        self.assertEqual(len(resultado.avaliacoes), 60)
        self.assertEqual({item.estado_avaliacao for item in resultado.avaliacoes}, {"SEM_BASE"})

    def test_rejeita_cobertura_incompleta_e_alvo_no_corte(self) -> None:
        with self.assertRaisesRegex(ErroSelecaoDezenas, "exatamente"):
            selecionar_dezenas_para_alvo(
                estatisticas_com()[:-1], configuracao(),
                numero_concurso_alvo=500, numero_concurso_corte=499,
            )
        with self.assertRaisesRegex(ErroSelecaoDezenas, "posterior"):
            selecionar_dezenas_para_alvo(
                estatisticas_com(), configuracao(),
                numero_concurso_alvo=499, numero_concurso_corte=499,
            )


if __name__ == "__main__":
    unittest.main()
