from decimal import Decimal

import pytest

from msen.services.backtest_temporario_selecao_dezenas import (
    PontoBacktestTemporario,
    resumir_pontos_temporarios,
)


def test_resumo_temporario_mantem_classes_exclusivas():
    pontos = (
        PontoBacktestTemporario(500, 10, 0),
        PontoBacktestTemporario(501, 14, 2),
        PontoBacktestTemporario(502, 18, 4),
        PontoBacktestTemporario(503, 22, 6),
    )

    resumo = resumir_pontos_temporarios(pontos)

    assert resumo.testes_efetuados == 4
    assert [item.quantidade for item in resumo.classes] == [1, 0, 1, 0, 1, 0, 1]
    assert sum(item.quantidade for item in resumo.classes) == 4
    assert resumo.minimo_dezenas == 10
    assert resumo.maximo_dezenas == 22
    assert resumo.media_dezenas == Decimal("16.000000")
    assert resumo.media_acertos == Decimal("3.000000")
    assert resumo.concursos_premiados == 2
    assert resumo.percentual_premiados == Decimal("50.000000")


def test_resumo_temporario_rejeita_lista_vazia():
    with pytest.raises(ValueError, match="ao menos um"):
        resumir_pontos_temporarios(())


def test_resumo_temporario_rejeita_acerto_fora_de_zero_a_seis():
    with pytest.raises(ValueError, match="entre 0 e 6"):
        resumir_pontos_temporarios((PontoBacktestTemporario(500, 10, 7),))
