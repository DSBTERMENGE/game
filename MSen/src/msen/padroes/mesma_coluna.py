"""Detectores puros dos padrões de dezenas na mesma coluna da matriz."""

from collections import defaultdict
from collections.abc import Sequence


def _validar_dezenas(dezenas: Sequence[int]) -> tuple[int, ...]:
    if isinstance(dezenas, (str, bytes)) or not isinstance(dezenas, Sequence):
        raise TypeError("O detector exige uma sequência com seis dezenas.")
    if len(dezenas) != 6:
        raise ValueError("O detector exige exatamente seis dezenas.")
    if any(isinstance(numero, bool) or not isinstance(numero, int) for numero in dezenas):
        raise TypeError("As dezenas devem ser números inteiros.")
    if any(numero < 1 or numero > 60 for numero in dezenas):
        raise ValueError("As dezenas devem estar entre 1 e 60.")
    if len(set(dezenas)) != 6:
        raise ValueError("As seis dezenas devem ser diferentes.")
    return tuple(dezenas)


def _maior_sequencia_vertical(dezenas: Sequence[int]) -> int:
    validadas = _validar_dezenas(dezenas)
    linhas_por_coluna: dict[int, list[int]] = defaultdict(list)
    for numero in validadas:
        coluna = ((numero - 1) % 10) + 1
        linha = (numero - 1) // 10
        linhas_por_coluna[coluna].append(linha)

    maior = 1
    for linhas in linhas_por_coluna.values():
        linhas_ordenadas = sorted(linhas)
        atual = 1
        for anterior, linha in zip(linhas_ordenadas, linhas_ordenadas[1:]):
            if linha - anterior == 1:
                atual += 1
                maior = max(maior, atual)
            else:
                atual = 1
    return maior


def detectar_duas_dezenas_na_mesma_coluna(dezenas: tuple[int, ...]) -> bool:
    """Detecta uma sequência vertical com exatamente duas dezenas.

    Parâmetros:
        dezenas: As seis dezenas diferentes, cada uma entre 1 e 60.

    Retorno:
        `True` quando a maior sequência em linhas subjacentes tem tamanho dois.

    Regra:
        As dezenas devem estar na mesma coluna e em linhas imediatamente
        consecutivas, portanto sua diferença é dez. Dois pares representam uma
        única ocorrência; uma sequência de três não pertence a este padrão.
    """

    return _maior_sequencia_vertical(dezenas) == 2


def detectar_tres_dezenas_na_mesma_coluna(dezenas: tuple[int, ...]) -> bool:
    """Detecta uma sequência vertical com exatamente três dezenas.

    Parâmetros:
        dezenas: As seis dezenas diferentes, cada uma entre 1 e 60.

    Retorno:
        `True` quando a maior sequência em linhas subjacentes tem tamanho três.

    Regra:
        O resultado pertence exclusivamente a este padrão mesmo que outra
        coluna contenha um par vertical.
    """

    return _maior_sequencia_vertical(dezenas) == 3


def detectar_mais_de_tres_dezenas_na_mesma_coluna(
    dezenas: tuple[int, ...],
) -> bool:
    """Detecta sequência vertical com quatro, cinco ou seis dezenas.

    Parâmetros:
        dezenas: As seis dezenas diferentes, cada uma entre 1 e 60.

    Retorno:
        `True` quando a maior sequência em linhas subjacentes supera três.

    Regra:
        Os tamanhos quatro, cinco e seis formam um único padrão e não são
        registrados novamente nos padrões de duas ou três dezenas.
    """

    return _maior_sequencia_vertical(dezenas) > 3
