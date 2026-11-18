"""Adapta as três origens atuais ao contrato comum do motor do Screener."""

from __future__ import annotations

from collections.abc import Iterable

from msen.screener.configuracao import ConfiguracaoScreener
from msen.screener.entrada_combinacoes import (
    ORIGEM_APLICACAO_INTEGRAL,
    ORIGEM_SELECAO_DEZENAS,
    ORIGEM_TESTE_5000,
    EntradaCombinacoesScreener,
    criar_entrada_combinacoes,
)
from msen.screener.gerador import (
    TOTAL_COMBINACOES,
    criar_iterador_combinacoes,
    gerar_amostra,
)

from .combinacoes_selecao_dezenas import (
    ErroCombinacoesSelecao,
    calcular_previa_combinacoes,
    gerar_combinacoes_seis_dezenas,
)


def adaptar_teste_5000(
    configuracao: ConfiguracaoScreener,
) -> EntradaCombinacoesScreener:
    """Empacota a amostra reproduzível já usada pelo Teste do Screener."""

    amostra = gerar_amostra(configuracao)
    return criar_entrada_combinacoes(
        origem=ORIGEM_TESTE_5000,
        total_combinacoes=len(amostra),
        itens=amostra,
        contexto={"semente": configuracao.semente},
    )


def adaptar_aplicacao_integral(
    configuracao: ConfiguracaoScreener,
    *,
    confirmacao_integral: str | None = None,
) -> EntradaCombinacoesScreener:
    """Empacota o iterador integral mantendo todas as travas existentes."""

    itens = criar_iterador_combinacoes(
        configuracao, confirmacao_integral=confirmacao_integral
    )
    return criar_entrada_combinacoes(
        origem=ORIGEM_APLICACAO_INTEGRAL,
        total_combinacoes=TOTAL_COMBINACOES,
        itens=itens,
        contexto={"universo_dezenas": 60},
    )


def adaptar_selecao_dezenas(
    dezenas_selecionadas: Iterable[int],
) -> EntradaCombinacoesScreener:
    """Empacota as combinações formadas por uma seleção variável de dezenas."""

    selecionadas = tuple(dezenas_selecionadas)
    previa = calcular_previa_combinacoes(selecionadas)
    if previa.quantidade_combinacoes == 0:
        raise ErroCombinacoesSelecao(
            "DEZENAS_INSUFICIENTES",
            "São necessárias ao menos seis dezenas para formar uma combinação.",
        )
    return criar_entrada_combinacoes(
        origem=ORIGEM_SELECAO_DEZENAS,
        total_combinacoes=previa.quantidade_combinacoes,
        itens=gerar_combinacoes_seis_dezenas(selecionadas),
        contexto={
            "dezenas_selecionadas": tuple(sorted(selecionadas)),
            "quantidade_dezenas": previa.quantidade_dezenas,
            "volume_elevado": previa.volume_elevado,
        },
    )
