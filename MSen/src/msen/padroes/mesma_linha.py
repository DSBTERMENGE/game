"""Detectores puros dos padrões de dezenas na mesma linha da matriz."""

from collections import Counter
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


def _maior_ocupacao_de_linha(dezenas: Sequence[int]) -> int:
    validadas = _validar_dezenas(dezenas)
    ocupacoes = Counter(((numero - 1) // 10) + 1 for numero in validadas)
    return max(ocupacoes.values())


def detectar_duas_dezenas_na_mesma_linha(dezenas: tuple[int, ...]) -> bool:
    """Detecta quando a linha mais ocupada contém exatamente duas dezenas.

    Parâmetros:
        dezenas: As seis dezenas diferentes, cada uma entre 1 e 60.

    Retorno:
        `True` somente quando a maior ocupação de uma linha é dois.

    Regra:
        As dezenas não precisam ser sequenciais. Dois pares em linhas
        diferentes representam uma única ocorrência; uma linha com três ou
        mais dezenas não pertence a este padrão.
    """

    return _maior_ocupacao_de_linha(dezenas) == 2


def detectar_tres_dezenas_na_mesma_linha(dezenas: tuple[int, ...]) -> bool:
    """Detecta quando a linha mais ocupada contém exatamente três dezenas.

    Parâmetros:
        dezenas: As seis dezenas diferentes, cada uma entre 1 e 60.

    Retorno:
        `True` somente quando a maior ocupação de uma linha é três.

    Regra:
        O resultado pertence exclusivamente a este padrão mesmo que outra
        linha contenha duas dezenas. Sequencialidade não é exigida.
    """

    return _maior_ocupacao_de_linha(dezenas) == 3


def detectar_mais_de_tres_dezenas_na_mesma_linha(
    dezenas: tuple[int, ...],
) -> bool:
    """Detecta quando uma linha contém quatro, cinco ou seis dezenas.

    Parâmetros:
        dezenas: As seis dezenas diferentes, cada uma entre 1 e 60.

    Retorno:
        `True` quando a maior ocupação de uma linha é superior a três.

    Regra:
        Os tamanhos quatro, cinco e seis formam um único padrão e não são
        registrados novamente nos padrões de duas ou três dezenas.
    """

    return _maior_ocupacao_de_linha(dezenas) > 3
