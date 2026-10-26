"""Conversão das dezenas em coordenadas e cálculo da média espacial."""

from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP

from msen.modelos import ResultadoEntrada


SEIS_CASAS_DECIMAIS = Decimal("0.000001")


@dataclass(frozen=True, slots=True)
class MediaEspacial:
    """Ponto médio decimal dos seis resultados na matriz de 10 por 6."""

    x: Decimal
    y: Decimal


def calcular_coordenada(numero: int) -> tuple[int, int]:
    """Retorna a coordenada lógica inteira de uma dezena entre 1 e 60."""

    if isinstance(numero, bool) or not isinstance(numero, int):
        raise TypeError("A dezena da coordenada deve ser um número inteiro.")
    if not 1 <= numero <= 60:
        raise ValueError("A dezena da coordenada deve estar entre 1 e 60.")

    return ((numero - 1) % 10, (numero - 1) // 10)


def calcular_media_espacial(resultado: ResultadoEntrada) -> MediaEspacial:
    """Calcula a média independente dos eixos X e Y dos seis resultados."""

    coordenadas = tuple(calcular_coordenada(numero) for numero in resultado.resultados)
    quantidade = Decimal(len(coordenadas))
    media_x_exata = Decimal(sum(x for x, _ in coordenadas)) / quantidade
    media_y_exata = Decimal(sum(y for _, y in coordenadas)) / quantidade

    return MediaEspacial(
        x=media_x_exata.quantize(SEIS_CASAS_DECIMAIS, rounding=ROUND_HALF_UP),
        y=media_y_exata.quantize(SEIS_CASAS_DECIMAIS, rounding=ROUND_HALF_UP),
    )
