"""Detecção geométrica de cinco ou seis dezenas em arranjo circular."""

from dataclasses import dataclass
from itertools import combinations
from math import hypot

from .entrada import validar_dezenas


EPSILON = 1e-9


@dataclass(frozen=True, slots=True)
class ArranjoCircular:
    centro_x: float
    centro_y: float
    raio: float
    dezenas_circulares: tuple[int, ...]
    desvio_relativo_maximo: float


def _ponto(dezena: int) -> tuple[float, float]:
    return ((dezena - 1) % 10 + 0.5, (dezena - 1) // 10 + 0.5)


def _circuncirculo(
    a: tuple[float, float],
    b: tuple[float, float],
    c: tuple[float, float],
) -> tuple[float, float, float] | None:
    ax, ay = a
    bx, by = b
    cx, cy = c
    divisor = 2 * (ax * (by - cy) + bx * (cy - ay) + cx * (ay - by))
    if abs(divisor) <= EPSILON:
        return None
    centro_x = (
        (ax * ax + ay * ay) * (by - cy)
        + (bx * bx + by * by) * (cy - ay)
        + (cx * cx + cy * cy) * (ay - by)
    ) / divisor
    centro_y = (
        (ax * ax + ay * ay) * (cx - bx)
        + (bx * bx + by * by) * (ax - cx)
        + (cx * cx + cy * cy) * (bx - ax)
    ) / divisor
    raio = hypot(ax - centro_x, ay - centro_y)
    return centro_x, centro_y, raio


def analisar_arranjo_circular(dezenas) -> ArranjoCircular | None:
    """Encontra o melhor círculo que contenha ao menos cinco das seis dezenas."""

    ordenadas = validar_dezenas(dezenas)
    pontos = {dezena: _ponto(dezena) for dezena in ordenadas}
    candidatos: list[ArranjoCircular] = []
    for trio in combinations(ordenadas, 3):
        circulo = _circuncirculo(*(pontos[dezena] for dezena in trio))
        if circulo is None:
            continue
        centro_x, centro_y, raio = circulo
        if raio <= EPSILON:
            continue
        desvios = {
            dezena: abs(hypot(
                pontos[dezena][0] - centro_x,
                pontos[dezena][1] - centro_y,
            ) - raio)
            for dezena in ordenadas
        }
        circulares = tuple(
            dezena for dezena in ordenadas
            if desvios[dezena] <= EPSILON * max(1.0, raio)
        )
        if len(circulares) >= 5:
            candidatos.append(ArranjoCircular(
                centro_x=centro_x,
                centro_y=centro_y,
                raio=raio,
                dezenas_circulares=circulares,
                desvio_relativo_maximo=(
                    max(desvios[item] for item in circulares) / raio
                ),
            ))
    if not candidatos:
        return None
    return min(candidatos, key=lambda item: (
        -len(item.dezenas_circulares),
        item.desvio_relativo_maximo,
        item.raio,
        item.centro_x,
        item.centro_y,
    ))


def detectar_quatro_a_seis_dezenas_em_arranjo_circular(dezenas) -> bool:
    """Retorna True quando cinco ou seis dezenas compartilham um círculo.

    O nome da função foi preservado para manter a compatibilidade com o
    cadastro existente do filtro.
    """

    return analisar_arranjo_circular(dezenas) is not None
