"""Prepara as entradas do Screener originadas pela Seleção de dezenas."""

from collections.abc import Iterable, Iterator

from .combinacoes_selecao_dezenas import (
    ErroCombinacoesSelecao,
    calcular_previa_combinacoes,
    gerar_combinacoes_seis_dezenas,
)


Combinacao = tuple[int, int, int, int, int, int]


def criar_dicionario_combinacoes(
    dezenas_selecionadas: Iterable[int],
) -> dict[str, object]:
    """Cria o segundo argumento do orquestrador sem acumular todos os jogos."""

    selecionadas = tuple(dezenas_selecionadas)
    previa = calcular_previa_combinacoes(selecionadas)
    if previa.quantidade_combinacoes == 0:
        raise ErroCombinacoesSelecao(
            "DEZENAS_INSUFICIENTES",
            "São necessárias ao menos seis dezenas para formar uma combinação.",
        )
    itens: Iterator[Combinacao] = gerar_combinacoes_seis_dezenas(selecionadas)
    return {
        "origem": "SELECAO_DE_DEZENAS",
        "dezenas_selecionadas": tuple(sorted(selecionadas)),
        "quantidade_dezenas": previa.quantidade_dezenas,
        "quantidade_combinacoes": previa.quantidade_combinacoes,
        "volume_elevado": previa.volume_elevado,
        "itens": itens,
    }
