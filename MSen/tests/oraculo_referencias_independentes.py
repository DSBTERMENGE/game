"""Oráculo independente: não importa cálculos, geometria ou padrões do MSen."""

from collections import Counter, defaultdict
from decimal import Decimal, ROUND_HALF_UP, localcontext
from math import hypot

from shapely import LineString, polygonize, unary_union


def referencias_estatisticas(dezenas: tuple[int, ...]) -> dict[str, Decimal | int]:
    ordenadas = sorted(dezenas)
    soma = sum(ordenadas)
    media = (Decimal(soma) / Decimal(6)).quantize(
        Decimal("0.000001"), rounding=ROUND_HALF_UP
    )
    mediana = ((Decimal(ordenadas[2]) + Decimal(ordenadas[3])) / 2).quantize(
        Decimal("0.1"), rounding=ROUND_HALF_UP
    )
    with localcontext() as contexto:
        contexto.prec = 50
        media_exata = Decimal(soma) / Decimal(6)
        variancia = sum(
            (Decimal(numero) - media_exata) ** 2 for numero in ordenadas
        ) / Decimal(6)
        desvio = variancia.sqrt().quantize(
            Decimal("0.000001"), rounding=ROUND_HALF_UP
        )
    return {
        "EST_SOMA": soma,
        "EST_MEDIA": media,
        "EST_MEDIANA": mediana,
        "EST_DESVIO_PADRAO": desvio,
    }


def _maior_bloco_horizontal(dezenas: tuple[int, ...]) -> int:
    ordenadas = sorted(dezenas)
    maior = atual = 1
    for anterior, numero in zip(ordenadas, ordenadas[1:]):
        atual = atual + 1 if numero == anterior + 1 else 1
        maior = max(maior, atual)
    return maior


def _maior_bloco_vertical(dezenas: tuple[int, ...]) -> int:
    linhas_por_coluna = defaultdict(list)
    for numero in dezenas:
        linhas_por_coluna[(numero - 1) % 10].append((numero - 1) // 10)
    maior = 1
    for linhas in linhas_por_coluna.values():
        atual = 1
        for anterior, linha in zip(sorted(linhas), sorted(linhas)[1:]):
            atual = atual + 1 if linha == anterior + 1 else 1
            maior = max(maior, atual)
    return maior


def _maior_ocupacao_linha(dezenas: tuple[int, ...]) -> int:
    return max(Counter((numero - 1) // 10 for numero in dezenas).values())


def referencias_padroes(dezenas: tuple[int, ...]) -> dict[str, bool]:
    horizontal = _maior_bloco_horizontal(dezenas)
    vertical = _maior_bloco_vertical(dezenas)
    linha = _maior_ocupacao_linha(dezenas)
    return {
        "PAD_PD_001": horizontal == 2,
        "PAD_PD_002": horizontal == 3,
        "PAD_PD_003": horizontal > 3,
        "PAD_PD_004": vertical == 2,
        "PAD_PD_005": vertical == 3,
        "PAD_PD_006": vertical > 3,
        "PAD_PD_007": linha == 2,
        "PAD_PD_008": linha == 3,
        "PAD_PD_009": linha > 3,
    }


def referencias_geometricas(dezenas: tuple[int, ...]) -> dict[str, Decimal | int | None]:
    """Calcula medidas por GEOS/Shapely, motor externo ao MSen."""

    coordenadas = tuple(
        ((numero - 1) % 10, (numero - 1) // 10)
        for numero in sorted(dezenas)
    )
    extensao = sum(
        hypot(fim[0] - inicio[0], fim[1] - inicio[1])
        for inicio, fim in zip(coordenadas, coordenadas[1:])
    )
    linha_fechada = LineString((*coordenadas, coordenadas[0]))
    linhas_nodadas = unary_union(linha_fechada)
    regioes = tuple(polygonize([linhas_nodadas]).geoms)
    area = sum(poligono.area for poligono in regioes)
    if not regioes:
        centro_x = centro_y = None
    else:
        uniao = unary_union(regioes)
        centro_x = Decimal(str(uniao.centroid.x))
        centro_y = Decimal(str(uniao.centroid.y))
    return {
        "GEO_EXTENSAO": Decimal(str(extensao)),
        "GEO_PERIMETRO": Decimal(str(linha_fechada.length)),
        "GEO_REGIOES": len(regioes),
        "GEO_AREA": Decimal(str(area)),
        "GEO_CENTRO_X": centro_x,
        "GEO_CENTRO_Y": centro_y,
    }
