"""Validação compartilhada da entrada das funções detectoras de padrões."""

from collections.abc import Sequence


def validar_dezenas(dezenas: Sequence[int]) -> tuple[int, ...]:
    """Valida e ordena as seis dezenas recebidas por um detector.

    Args:
        dezenas: Sequência com seis inteiros diferentes entre 1 e 60.

    Returns:
        As seis dezenas em ordem crescente, numa tupla imutável.

    Raises:
        TypeError: Para coleção ou elementos de tipo inválido.
        ValueError: Para quantidade, faixa ou repetição inválida.
    """

    if isinstance(dezenas, (str, bytes)) or not isinstance(dezenas, Sequence):
        raise TypeError("O detector exige uma sequência com seis dezenas.")
    if len(dezenas) != 6:
        raise ValueError("O detector exige exatamente seis dezenas.")
    if any(
        isinstance(numero, bool) or not isinstance(numero, int)
        for numero in dezenas
    ):
        raise TypeError("As dezenas devem ser números inteiros.")
    if any(numero < 1 or numero > 60 for numero in dezenas):
        raise ValueError("As dezenas devem estar entre 1 e 60.")
    if len(set(dezenas)) != 6:
        raise ValueError("As seis dezenas devem ser diferentes.")
    return tuple(sorted(dezenas))
