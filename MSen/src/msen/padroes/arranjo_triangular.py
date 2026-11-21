"""Detecção de seis dezenas nos lados de um triângulo retângulo."""

from dataclasses import dataclass
from itertools import combinations, product

from .entrada import validar_dezenas


EPSILON = 1e-9


@dataclass(frozen=True, slots=True)
class LinhaTriangulo:
    tipo: str
    a: float
    b: float
    c: float


@dataclass(frozen=True, slots=True)
class LadoTriangulo:
    tipo: str
    x1: float
    y1: float
    x2: float
    y2: float


@dataclass(frozen=True, slots=True)
class ArranjoTriangular:
    lados: tuple[LadoTriangulo, LadoTriangulo, LadoTriangulo]
    distribuicao: tuple[int, int, int]
    atribuicao: tuple[tuple[int, int], ...]
    area: float


def _ponto(dezena: int) -> tuple[float, float]:
    return ((dezena - 1) % 10 + 0.5, (dezena - 1) // 10 + 0.5)


def _linhas_do_ponto(x: float, y: float) -> tuple[LinhaTriangulo, ...]:
    return (
        LinhaTriangulo("horizontal", 0.0, 1.0, y),
        LinhaTriangulo("vertical", 1.0, 0.0, x),
        LinhaTriangulo("diagonal_direita", -1.0, 1.0, y - x),
        LinhaTriangulo("diagonal_esquerda", 1.0, 1.0, x + y),
    )


def _intersecao(
    primeira: LinhaTriangulo, segunda: LinhaTriangulo
) -> tuple[float, float] | None:
    divisor = primeira.a * segunda.b - segunda.a * primeira.b
    if abs(divisor) <= EPSILON:
        return None
    return (
        (primeira.c * segunda.b - segunda.c * primeira.b) / divisor,
        (primeira.a * segunda.c - segunda.a * primeira.c) / divisor,
    )


def _na_linha(ponto: tuple[float, float], linha: LinhaTriangulo) -> bool:
    return abs(linha.a * ponto[0] + linha.b * ponto[1] - linha.c) <= EPSILON


def _no_segmento(
    ponto: tuple[float, float], inicio: tuple[float, float], fim: tuple[float, float]
) -> bool:
    return (
        min(inicio[0], fim[0]) - EPSILON <= ponto[0] <= max(inicio[0], fim[0]) + EPSILON
        and min(inicio[1], fim[1]) - EPSILON <= ponto[1] <= max(inicio[1], fim[1]) + EPSILON
    )


def _atribuir(
    dezenas: tuple[int, ...], possibilidades: tuple[tuple[int, ...], ...]
) -> tuple[tuple[int, int], ...] | None:
    for escolha in product(*possibilidades):
        contagens = tuple(escolha.count(lado) for lado in range(3))
        if sorted(contagens) in ([1, 2, 3], [2, 2, 2]):
            return tuple(zip(dezenas, escolha))
    return None


def analisar_arranjo_triangular(dezenas) -> ArranjoTriangular | None:
    """Encontra um triângulo fechado usando as quatro direções do painel."""

    ordenadas = validar_dezenas(dezenas)
    pontos = {dezena: _ponto(dezena) for dezena in ordenadas}
    linhas = {
        (linha.tipo, linha.c): linha
        for ponto in pontos.values()
        for linha in _linhas_do_ponto(*ponto)
    }
    candidatos: list[ArranjoTriangular] = []
    for trio in combinations(linhas.values(), 3):
        if len({linha.tipo for linha in trio}) != 3:
            continue
        # Todo trio de direções distintas contém H×V ou D×E, o ângulo reto.
        vertices = (
            _intersecao(trio[0], trio[1]),
            _intersecao(trio[1], trio[2]),
            _intersecao(trio[2], trio[0]),
        )
        if any(vertice is None for vertice in vertices):
            continue
        if any(
            abs(a[0] - b[0]) <= EPSILON and abs(a[1] - b[1]) <= EPSILON
            for a, b in combinations(vertices, 2)
        ):
            continue

        # O lado i encontra os outros dois nos vértices correspondentes.
        extremos = (
            (vertices[0], vertices[2]),
            (vertices[0], vertices[1]),
            (vertices[1], vertices[2]),
        )
        possibilidades = []
        for dezena in ordenadas:
            ponto = pontos[dezena]
            lados = tuple(
                indice for indice, linha in enumerate(trio)
                if _na_linha(ponto, linha) and _no_segmento(ponto, *extremos[indice])
            )
            if not lados:
                break
            possibilidades.append(lados)
        if len(possibilidades) != 6:
            continue
        atribuicao = _atribuir(ordenadas, tuple(possibilidades))
        if atribuicao is None:
            continue
        distribuicao = tuple(
            sum(escolhido == lado for _dezena, escolhido in atribuicao)
            for lado in range(3)
        )
        area = abs(
            vertices[0][0] * (vertices[1][1] - vertices[2][1])
            + vertices[1][0] * (vertices[2][1] - vertices[0][1])
            + vertices[2][0] * (vertices[0][1] - vertices[1][1])
        ) / 2
        candidatos.append(ArranjoTriangular(
            lados=tuple(
                LadoTriangulo(linha.tipo, *extremos[indice][0], *extremos[indice][1])
                for indice, linha in enumerate(trio)
            ),
            distribuicao=distribuicao,
            atribuicao=atribuicao,
            area=area,
        ))
    if not candidatos:
        return None
    return min(candidatos, key=lambda item: (item.area, item.distribuicao))


def detectar_dezenas_arranjadas_em_formato_triangular(dezenas) -> bool:
    """Retorna True quando as seis dezenas formam o contorno triangular."""

    return analisar_arranjo_triangular(dezenas) is not None
