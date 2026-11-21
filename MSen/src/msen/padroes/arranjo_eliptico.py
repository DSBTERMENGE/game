"""Detecção de seis dezenas em um arranjo elíptico simétrico."""

from dataclasses import dataclass
from itertools import combinations
from math import atan2, degrees, hypot

from .entrada import validar_dezenas


EPSILON = 1e-9


@dataclass(frozen=True, slots=True)
class ArranjoEliptico:
    centro_x: float
    centro_y: float
    semieixo_maior: float
    semieixo_menor: float
    angulo_graus: float
    extremidades_eixo_maior: tuple[int, int]
    pares_simetricos: tuple[tuple[int, int], tuple[int, int]]


def _ponto(dezena: int) -> tuple[float, float]:
    return ((dezena - 1) % 10 + 0.5, (dezena - 1) // 10 + 0.5)


def _distancia_quadrada(a: tuple[float, float], b: tuple[float, float]) -> float:
    return (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2


def _iguais(a: float, b: float) -> bool:
    return abs(a - b) <= EPSILON * max(1.0, abs(a), abs(b))


def analisar_arranjo_eliptico(dezenas) -> ArranjoEliptico | None:
    """Reconhece a elipse definida pelo maior eixo e dois pares simétricos."""

    ordenadas = validar_dezenas(dezenas)
    pontos = {dezena: _ponto(dezena) for dezena in ordenadas}
    pares = tuple(combinations(ordenadas, 2))
    maior_distancia = max(
        _distancia_quadrada(pontos[a], pontos[b]) for a, b in pares
    )

    # Empates na maior distância são avaliados separadamente.
    for extremo_a, extremo_b in pares:
        a = pontos[extremo_a]
        b = pontos[extremo_b]
        if not _iguais(_distancia_quadrada(a, b), maior_distancia):
            continue
        centro_x = (a[0] + b[0]) / 2
        centro_y = (a[1] + b[1]) / 2
        semieixo_maior = hypot(b[0] - a[0], b[1] - a[1]) / 2
        ux = (b[0] - a[0]) / (2 * semieixo_maior)
        uy = (b[1] - a[1]) / (2 * semieixo_maior)
        restantes = tuple(
            dezena for dezena in ordenadas
            if dezena not in {extremo_a, extremo_b}
        )

        emparelhamentos = (
            ((restantes[0], restantes[1]), (restantes[2], restantes[3])),
            ((restantes[0], restantes[2]), (restantes[1], restantes[3])),
            ((restantes[0], restantes[3]), (restantes[1], restantes[2])),
        )
        for par_1, par_2 in emparelhamentos:
            if any(
                not (
                    _iguais(pontos[p][0] + pontos[q][0], 2 * centro_x)
                    and _iguais(pontos[p][1] + pontos[q][1], 2 * centro_y)
                )
                for p, q in (par_1, par_2)
            ):
                continue

            semieixos_menores = []
            valido = True
            for p, _q in (par_1, par_2):
                dx = pontos[p][0] - centro_x
                dy = pontos[p][1] - centro_y
                x = dx * ux + dy * uy
                y = -dx * uy + dy * ux
                denominador = 1 - (x * x) / (semieixo_maior ** 2)
                if denominador <= EPSILON or abs(y) <= EPSILON:
                    valido = False
                    break
                semieixo_menor = abs(y) / (denominador ** 0.5)
                if semieixo_menor >= semieixo_maior - EPSILON:
                    valido = False
                    break
                semieixos_menores.append(semieixo_menor)
            if valido and _iguais(semieixos_menores[0], semieixos_menores[1]):
                return ArranjoEliptico(
                    centro_x=centro_x,
                    centro_y=centro_y,
                    semieixo_maior=semieixo_maior,
                    semieixo_menor=sum(semieixos_menores) / 2,
                    angulo_graus=degrees(atan2(uy, ux)),
                    extremidades_eixo_maior=(extremo_a, extremo_b),
                    pares_simetricos=(par_1, par_2),
                )
    return None


def detectar_seis_dezenas_em_arranjo_eliptico(dezenas) -> bool:
    """Retorna True quando as seis dezenas formam a mesma elipse."""

    return analisar_arranjo_eliptico(dezenas) is not None
