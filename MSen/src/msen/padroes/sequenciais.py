"""Detectores puros dos padrões iniciais de dezenas sequenciais."""

from collections.abc import Sequence
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class AnaliseSequencial:
    """Evidência reproduzível dos maiores blocos consecutivos encontrados."""

    dezenas_ordenadas: tuple[int, ...]
    maior_tamanho: int
    maiores_blocos: tuple[tuple[int, ...], ...]


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
    return tuple(sorted(dezenas))


def _maior_grupo_sequencial(dezenas: Sequence[int]) -> int:
    return analisar_dezenas_sequenciais(dezenas).maior_tamanho


def analisar_dezenas_sequenciais(dezenas: Sequence[int]) -> AnaliseSequencial:
    """Localiza o maior bloco sequencial sem unir as dezenas 60 e 01.

    A entrada é validada e ordenada. A evidência contém todos os blocos que
    empatam no maior tamanho, permitindo conferir a classificação produzida
    pela mesma função central usada pelos detectores.
    """

    ordenadas = _validar_dezenas(dezenas)
    blocos: list[tuple[int, ...]] = []
    atual = [ordenadas[0]]
    for anterior, numero in zip(ordenadas, ordenadas[1:]):
        if numero - anterior == 1:
            atual.append(numero)
        else:
            blocos.append(tuple(atual))
            atual = [numero]
    blocos.append(tuple(atual))
    maior = max(len(bloco) for bloco in blocos)
    return AnaliseSequencial(
        dezenas_ordenadas=ordenadas,
        maior_tamanho=maior,
        maiores_blocos=tuple(bloco for bloco in blocos if len(bloco) == maior),
    )


def detectar_duas_dezenas_sequenciais(dezenas: tuple[int, ...]) -> bool:
    """Detecta quando o maior grupo consecutivo possui exatamente duas dezenas.

    Parâmetros:
        dezenas: As seis dezenas diferentes, cada uma entre 1 e 60.

    Retorno:
        `True` somente quando o maior bloco tem tamanho dois.

    Regra:
        A ordem recebida não interfere. Um resultado com grupo de três ou mais
        não pertence a este padrão, mesmo contendo pares consecutivos.
    """

    return _maior_grupo_sequencial(dezenas) == 2


def detectar_tres_dezenas_sequenciais(dezenas: tuple[int, ...]) -> bool:
    """Detecta quando o maior grupo consecutivo possui exatamente três dezenas.

    Parâmetros:
        dezenas: As seis dezenas diferentes, cada uma entre 1 e 60.

    Retorno:
        `True` somente quando o maior bloco tem tamanho três.

    Regra:
        O exemplo `10, 25, 26, 27, 50, 58` pertence exclusivamente a este
        padrão, representado pelo bloco `25, 26, 27`.
    """

    return _maior_grupo_sequencial(dezenas) == 3


def detectar_mais_de_tres_dezenas_sequenciais(
    dezenas: tuple[int, ...],
) -> bool:
    """Detecta quando o maior grupo consecutivo possui quatro ou mais dezenas.

    Parâmetros:
        dezenas: As seis dezenas diferentes, cada uma entre 1 e 60.

    Retorno:
        `True` para blocos de quatro, cinco ou seis dezenas.

    Regra:
        Todos os tamanhos maiores que três pertencem a um único padrão. Eles não
        são registrados novamente nos padrões de duas ou três dezenas.
    """

    return _maior_grupo_sequencial(dezenas) > 3
