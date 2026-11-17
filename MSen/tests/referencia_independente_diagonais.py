"""Oráculo independente para conferir as categorias diagonais do PG_004.

Este módulo de teste não importa o analisador oficial nem os cálculos de
coordenadas da aplicação. A duplicação intencional permite detectar regressões
na implementação aferida.
"""

from collections.abc import Sequence


SEM_REFERENCIA = "SEM_REFERENCIA_LONGA"


def _validar(dezenas: Sequence[int]) -> tuple[int, ...]:
    if isinstance(dezenas, (str, bytes)) or not isinstance(dezenas, Sequence):
        raise TypeError("A referência exige uma sequência de dezenas.")
    if len(dezenas) != 6:
        raise ValueError("A referência exige seis dezenas.")
    if any(isinstance(item, bool) or not isinstance(item, int) for item in dezenas):
        raise TypeError("As dezenas da referência devem ser inteiras.")
    if any(item < 1 or item > 60 for item in dezenas):
        raise ValueError("As dezenas da referência devem estar entre 1 e 60.")
    if len(set(dezenas)) != 6:
        raise ValueError("As dezenas da referência devem ser distintas.")
    return tuple(sorted(dezenas))


def _ponto(dezena: int) -> tuple[int, int]:
    indice = dezena - 1
    linha, coluna = divmod(indice, 10)
    return coluna, linha


def calcular_referencia_categorias_diagonais(dezenas: Sequence[int]) -> str:
    """Calcula a resposta canônica por enumeração independente da grade."""

    ordenadas = _validar(dezenas)
    pontos_grade = {numero: _ponto(numero) for numero in range(1, 61)}
    assinaturas: set[tuple[int, int]] = set()
    for indice_referencia in (1, 2, 3, 4):
        referencia = ordenadas[indice_referencia]
        coluna_ref, linha_ref = pontos_grade[referencia]
        diagonal_d = {
            numero
            for numero, (coluna, linha) in pontos_grade.items()
            if coluna + linha == coluna_ref + linha_ref
        }
        diagonal_e = {
            numero
            for numero, (coluna, linha) in pontos_grade.items()
            if coluna - linha == coluna_ref - linha_ref
        }
        if len(diagonal_d) < 4 or len(diagonal_e) < 4:
            continue
        companheiras = set(ordenadas)
        companheiras.remove(referencia)
        assinaturas.add(
            (
                len(companheiras & diagonal_d),
                len(companheiras & diagonal_e),
            )
        )
    if not assinaturas:
        return SEM_REFERENCIA
    return "|".join(f"{direita}D{esquerda}E" for direita, esquerda in sorted(assinaturas))
