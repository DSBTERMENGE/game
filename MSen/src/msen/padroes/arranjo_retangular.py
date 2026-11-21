"""Detecção geométrica de seis dezenas no contorno de um retângulo."""

from dataclasses import dataclass
from itertools import combinations, product
from math import atan2, degrees, hypot

from .entrada import validar_dezenas


EPSILON = 1e-9


@dataclass(frozen=True, slots=True)
class LadoRetangulo:
    x1: float
    y1: float
    x2: float
    y2: float


@dataclass(frozen=True, slots=True)
class ArranjoRetangular:
    lados: tuple[LadoRetangulo, LadoRetangulo, LadoRetangulo, LadoRetangulo]
    distribuicao: tuple[int, int, int, int]
    atribuicao: tuple[tuple[int, int], ...]
    angulo_graus: float
    area: float


def _ponto(dezena: int) -> tuple[float, float]:
    return ((dezena - 1) % 10 + 0.5, (dezena - 1) // 10 + 0.5)


def _proximo(a: float, b: float) -> bool:
    return abs(a - b) <= EPSILON * max(1.0, abs(a), abs(b))


def _atribuir_lados(
    dezenas: tuple[int, ...], possibilidades: tuple[tuple[int, ...], ...]
) -> tuple[tuple[int, int], ...] | None:
    """Atribui cada dezena a somente um lado e ocupa os quatro lados."""

    for escolha in product(*possibilidades):
        contagens = tuple(escolha.count(lado) for lado in range(4))
        if sorted(contagens) in ([1, 1, 1, 3], [1, 1, 2, 2]):
            return tuple(zip(dezenas, escolha))
    return None


def analisar_arranjo_retangular(dezenas) -> ArranjoRetangular | None:
    """Encontra um quadrado ou retângulo, inclusive inclinado."""

    ordenadas = validar_dezenas(dezenas)
    pontos = {dezena: _ponto(dezena) for dezena in ordenadas}
    direcoes: dict[tuple[float, float], tuple[float, float]] = {}
    for a, b in combinations(ordenadas, 2):
        dx = pontos[b][0] - pontos[a][0]
        dy = pontos[b][1] - pontos[a][1]
        comprimento = hypot(dx, dy)
        ux, uy = dx / comprimento, dy / comprimento
        if ux < -EPSILON or (_proximo(ux, 0.0) and uy < 0):
            ux, uy = -ux, -uy
        direcoes[(round(ux, 12), round(uy, 12))] = (ux, uy)

    candidatos: list[ArranjoRetangular] = []
    for ux, uy in direcoes.values():
        vx, vy = -uy, ux
        projecoes = {
            dezena: (
                pontos[dezena][0] * ux + pontos[dezena][1] * uy,
                pontos[dezena][0] * vx + pontos[dezena][1] * vy,
            )
            for dezena in ordenadas
        }
        minimo_u = min(item[0] for item in projecoes.values())
        maximo_u = max(item[0] for item in projecoes.values())
        minimo_v = min(item[1] for item in projecoes.values())
        maximo_v = max(item[1] for item in projecoes.values())
        largura = maximo_u - minimo_u
        altura = maximo_v - minimo_v
        if largura <= EPSILON or altura <= EPSILON:
            continue

        possibilidades = []
        for dezena in ordenadas:
            pu, pv = projecoes[dezena]
            lados = []
            if _proximo(pu, minimo_u):
                lados.append(0)
            if _proximo(pu, maximo_u):
                lados.append(1)
            if _proximo(pv, minimo_v):
                lados.append(2)
            if _proximo(pv, maximo_v):
                lados.append(3)
            if not lados:
                break
            possibilidades.append(tuple(lados))
        if len(possibilidades) != 6:
            continue
        if any(
            sum(lado in lados for lados in possibilidades) >= 4
            for lado in range(4)
        ):
            continue
        atribuicao = _atribuir_lados(ordenadas, tuple(possibilidades))
        if atribuicao is None:
            continue
        distribuicao = tuple(
            sum(lado_escolhido == lado for _dezena, lado_escolhido in atribuicao)
            for lado in range(4)
        )

        def cartesiano(pu: float, pv: float) -> tuple[float, float]:
            return (pu * ux + pv * vx, pu * uy + pv * vy)

        vertices = (
            cartesiano(minimo_u, minimo_v),
            cartesiano(maximo_u, minimo_v),
            cartesiano(maximo_u, maximo_v),
            cartesiano(minimo_u, maximo_v),
        )
        lados = tuple(
            LadoRetangulo(*vertices[indice], *vertices[(indice + 1) % 4])
            for indice in range(4)
        )
        candidatos.append(ArranjoRetangular(
            lados=lados,
            distribuicao=distribuicao,
            atribuicao=atribuicao,
            angulo_graus=degrees(atan2(uy, ux)),
            area=largura * altura,
        ))
    if not candidatos:
        return None
    return min(candidatos, key=lambda item: (item.area, item.angulo_graus))


def detectar_arranjo_quadrado_ou_retangulo(dezenas) -> bool:
    """Retorna True quando as seis dezenas ocupam os quatro lados da figura."""

    return analisar_arranjo_retangular(dezenas) is not None
