"""Polígono simples de maior área que usa as seis dezenas como vértices."""

from dataclasses import dataclass
from fractions import Fraction
from itertools import permutations

from .caminho import PontoGeometrico, SegmentoGeometrico, construir_vertices
from .medidas import medir_regiao
from .regioes import RegiaoFechada, encontrar_intersecoes


@dataclass(frozen=True, slots=True)
class ResultadoPoligono2:
    dezenas: tuple[int, ...]
    vertices: tuple[PontoGeometrico, ...]
    area: Fraction
    centro_gravidade: PontoGeometrico
    circuitos_avaliados: int
    circuitos_validos: int


def _segmentos(vertices: tuple[PontoGeometrico, ...]):
    return tuple(
        SegmentoGeometrico(atual, seguinte)
        for atual, seguinte in zip(vertices, vertices[1:] + vertices[:1])
    )


def _area_assinada(vertices: tuple[PontoGeometrico, ...]) -> Fraction:
    return sum(
        atual.x * seguinte.y - seguinte.x * atual.y
        for atual, seguinte in zip(vertices, vertices[1:] + vertices[:1])
    ) / 2


def calcular_poligono2(dezenas) -> ResultadoPoligono2 | None:
    """Seleciona exatamente o circuito simples de maior área.

    A menor dezena fixa o início e apenas uma das duas orientações equivalentes
    é enumerada. Com isso são avaliados no máximo 60 circuitos.
    """

    ordenadas = tuple(sorted(dezenas))
    pontos_ordenados = construir_vertices(ordenadas)
    pontos = dict(zip(ordenadas, pontos_ordenados))
    primeira, restantes = ordenadas[0], ordenadas[1:]
    melhor = None
    validos = 0
    avaliados = 0

    for cauda in permutations(restantes):
        if cauda[0] > cauda[-1]:
            continue
        avaliados += 1
        circuito = (primeira,) + cauda
        vertices = tuple(pontos[dezena] for dezena in circuito)
        if encontrar_intersecoes(_segmentos(vertices)):
            continue
        medida = medir_regiao(RegiaoFechada(vertices))
        if medida.area == 0 or medida.centroide is None:
            continue
        validos += 1
        candidato = (medida.area, tuple(-x for x in circuito), circuito, vertices, medida.centroide)
        if melhor is None or candidato[:2] > melhor[:2]:
            melhor = candidato

    if melhor is None:
        return None
    area, _, circuito, vertices, centroide = melhor
    if _area_assinada(vertices) < 0:
        circuito = (circuito[0],) + tuple(reversed(circuito[1:]))
        vertices = tuple(pontos[dezena] for dezena in circuito)
        centroide = medir_regiao(RegiaoFechada(vertices)).centroide
    return ResultadoPoligono2(
        dezenas=circuito,
        vertices=vertices,
        area=area,
        centro_gravidade=centroide,
        circuitos_avaliados=avaliados,
        circuitos_validos=validos,
    )
