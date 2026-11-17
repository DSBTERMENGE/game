"""Adaptadores escalares que reutilizam exclusivamente os cálculos oficiais."""

from decimal import Decimal, localcontext
from fractions import Fraction

from msen.geometria import calcular_area_e_centro_gravidade
from msen.padroes import (
    CATEGORIA_SEM_REFERENCIA_LONGA,
    analisar_assinaturas_diagonais,
)


def _decimal_exato(valor: Fraction) -> Decimal:
    with localcontext() as contexto:
        contexto.prec = 30
        return Decimal(valor.numerator) / Decimal(valor.denominator)


def calcular_quantidade_regioes(dezenas: tuple[int, ...]) -> int:
    return len(calcular_area_e_centro_gravidade(dezenas).regioes)


def calcular_area_total(dezenas: tuple[int, ...]) -> Decimal:
    return _decimal_exato(calcular_area_e_centro_gravidade(dezenas).area_total)


def calcular_centro_gravidade_x(dezenas: tuple[int, ...]) -> Decimal | None:
    centro = calcular_area_e_centro_gravidade(dezenas).centro_gravidade
    return None if centro is None else _decimal_exato(centro.x)


def calcular_centro_gravidade_y(dezenas: tuple[int, ...]) -> Decimal | None:
    centro = calcular_area_e_centro_gravidade(dezenas).centro_gravidade
    return None if centro is None else _decimal_exato(centro.y)


def calcular_categorias_diagonais(dezenas: tuple[int, ...]) -> str:
    """Serializa o resultado categórico diagonal para validação independente."""

    analise = analisar_assinaturas_diagonais(dezenas)
    if analise.sem_referencia_longa:
        return CATEGORIA_SEM_REFERENCIA_LONGA
    return "|".join(item.codigo for item in analise.assinaturas)
