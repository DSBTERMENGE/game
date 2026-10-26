"""Estatísticas calculadas exclusivamente a partir de uma linha validada."""

from collections.abc import Sequence
from decimal import Decimal, ROUND_HALF_UP, localcontext

from msen.modelos import ResultadoEntrada


SEIS_CASAS_DECIMAIS = Decimal("0.000001")
UMA_CASA_DECIMAL = Decimal("0.1")


def calcular_soma(resultado: ResultadoEntrada) -> int:
    """Soma os seis resultados preservados no modelo validado."""

    return sum(resultado.resultados)


def _calcular_media_exata(resultado: ResultadoEntrada) -> Decimal:
    """Calcula a média sem aplicar arredondamento intermediário."""

    return Decimal(calcular_soma(resultado)) / Decimal(6)


def calcular_media_aritmetica(resultado: ResultadoEntrada) -> Decimal:
    """Retorna a média aritmética com seis casas para armazenamento."""

    return _calcular_media_exata(resultado).quantize(
        SEIS_CASAS_DECIMAIS,
        rounding=ROUND_HALF_UP,
    )


def calcular_mediana(resultado: ResultadoEntrada) -> Decimal:
    """Retorna a mediana dos seis valores com uma casa decimal."""

    ordenados = sorted(resultado.resultados)
    mediana_exata = (Decimal(ordenados[2]) + Decimal(ordenados[3])) / Decimal(2)
    return mediana_exata.quantize(UMA_CASA_DECIMAL, rounding=ROUND_HALF_UP)


def calcular_desvio_padrao_populacional(
    valores: Sequence[int | Decimal],
) -> Decimal:
    """Calcula o desvio-padrão populacional de uma sequência não vazia."""

    if not valores:
        raise ValueError("O desvio-padrão exige ao menos um valor.")

    decimais: list[Decimal] = []
    for valor in valores:
        if isinstance(valor, bool) or not isinstance(valor, (int, Decimal)):
            raise TypeError("O desvio-padrão aceita somente int ou Decimal.")
        decimais.append(valor if isinstance(valor, Decimal) else Decimal(valor))

    with localcontext() as contexto:
        contexto.prec = 50
        quantidade = Decimal(len(decimais))
        media_exata = sum(decimais, start=Decimal(0)) / quantidade
        variancia = (
            sum(
                ((valor - media_exata) ** 2 for valor in decimais),
                start=Decimal(0),
            )
            / quantidade
        )
        desvio_exato = variancia.sqrt()
        return desvio_exato.quantize(
            SEIS_CASAS_DECIMAIS,
            rounding=ROUND_HALF_UP,
        )


def calcular_desvio_padrao_media(resultado: ResultadoEntrada) -> Decimal:
    """Calcula o desvio-padrão populacional dos seis resultados da linha."""

    return calcular_desvio_padrao_populacional(resultado.resultados)
