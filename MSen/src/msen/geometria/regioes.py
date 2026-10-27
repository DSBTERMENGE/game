"""Divisão exata de segmentos e identificação de regiões fechadas."""

from collections import defaultdict
from collections.abc import Sequence
from dataclasses import dataclass
from fractions import Fraction
from functools import cmp_to_key

from .caminho import PontoGeometrico, SegmentoGeometrico


@dataclass(frozen=True, slots=True)
class RegiaoFechada:
    """Representa o contorno orientado de uma região limitada da rede planar."""

    vertices: tuple[PontoGeometrico, ...]


def _produto_vetorial(
    origem: PontoGeometrico, primeiro: PontoGeometrico, segundo: PontoGeometrico
) -> Fraction:
    return ((primeiro.x - origem.x) * (segundo.y - origem.y)) - (
        (primeiro.y - origem.y) * (segundo.x - origem.x)
    )


def _ponto_no_segmento(ponto: PontoGeometrico, segmento: SegmentoGeometrico) -> bool:
    if _produto_vetorial(segmento.inicio, segmento.fim, ponto) != 0:
        return False
    return (
        min(segmento.inicio.x, segmento.fim.x) <= ponto.x <= max(segmento.inicio.x, segmento.fim.x)
        and min(segmento.inicio.y, segmento.fim.y) <= ponto.y <= max(segmento.inicio.y, segmento.fim.y)
    )


def _intersecoes_do_par(
    primeiro: SegmentoGeometrico, segundo: SegmentoGeometrico
) -> set[PontoGeometrico]:
    p, q = primeiro.inicio, segundo.inicio
    rx, ry = primeiro.fim.x - p.x, primeiro.fim.y - p.y
    sx, sy = segundo.fim.x - q.x, segundo.fim.y - q.y
    denominador = rx * sy - ry * sx
    qpx, qpy = q.x - p.x, q.y - p.y

    if denominador != 0:
        parametro_primeiro = (qpx * sy - qpy * sx) / denominador
        parametro_segundo = (qpx * ry - qpy * rx) / denominador
        if 0 <= parametro_primeiro <= 1 and 0 <= parametro_segundo <= 1:
            return {
                PontoGeometrico(
                    p.x + parametro_primeiro * rx,
                    p.y + parametro_primeiro * ry,
                )
            }
        return set()

    if qpx * ry - qpy * rx != 0:
        return set()

    candidatos = {primeiro.inicio, primeiro.fim, segundo.inicio, segundo.fim}
    return {
        ponto
        for ponto in candidatos
        if _ponto_no_segmento(ponto, primeiro) and _ponto_no_segmento(ponto, segundo)
    }


def _validar_segmentos(
    segmentos: Sequence[SegmentoGeometrico],
) -> tuple[SegmentoGeometrico, ...]:
    if isinstance(segmentos, (str, bytes)) or not isinstance(segmentos, Sequence):
        raise TypeError("A operação geométrica exige uma sequência de segmentos.")
    if any(not isinstance(segmento, SegmentoGeometrico) for segmento in segmentos):
        raise TypeError("Todos os itens devem ser segmentos geométricos.")
    if any(segmento.inicio == segmento.fim for segmento in segmentos):
        raise ValueError("Um segmento geométrico não pode ter comprimento zero.")
    return tuple(segmentos)


def encontrar_intersecoes(
    segmentos: Sequence[SegmentoGeometrico],
) -> tuple[PontoGeometrico, ...]:
    """Localiza nós compartilhados que não sejam apenas junções consecutivas.

    Args:
        segmentos: Segmentos do percurso fechado ou de outra rede planar.

    Returns:
        Pontos exatos de cruzamento, contato ou limite de sobreposição. Uma
        extremidade comum a apenas dois segmentos é omitida por ser uma junção
        normal do percurso.
    """

    validados = _validar_segmentos(segmentos)
    incidencias: dict[PontoGeometrico, set[int]] = defaultdict(set)
    for indice, primeiro in enumerate(validados):
        for outro_indice in range(indice + 1, len(validados)):
            segundo = validados[outro_indice]
            for ponto in _intersecoes_do_par(primeiro, segundo):
                incidencias[ponto].update((indice, outro_indice))

    resultado = []
    for ponto, indices in incidencias.items():
        apenas_extremidades = all(
            ponto in (validados[indice].inicio, validados[indice].fim)
            for indice in indices
        )
        if len(indices) > 2 or not apenas_extremidades:
            resultado.append(ponto)
    return tuple(sorted(resultado, key=lambda ponto: (ponto.y, ponto.x)))


def _parametro_no_segmento(
    ponto: PontoGeometrico, segmento: SegmentoGeometrico
) -> Fraction:
    delta_x = segmento.fim.x - segmento.inicio.x
    if delta_x != 0:
        return (ponto.x - segmento.inicio.x) / delta_x
    return (ponto.y - segmento.inicio.y) / (segmento.fim.y - segmento.inicio.y)


def dividir_segmentos(
    segmentos: Sequence[SegmentoGeometrico],
) -> tuple[SegmentoGeometrico, ...]:
    """Divide segmentos em todos os nós e remove trechos sobrepostos repetidos.

    Args:
        segmentos: Segmentos válidos que podem se cruzar ou se sobrepor.

    Returns:
        Trechos atômicos únicos, orientados por ordem crescente de coordenadas.
    """

    validados = _validar_segmentos(segmentos)
    pontos_por_segmento = [set((segmento.inicio, segmento.fim)) for segmento in validados]
    for indice, primeiro in enumerate(validados):
        for outro_indice in range(indice + 1, len(validados)):
            comuns = _intersecoes_do_par(primeiro, validados[outro_indice])
            pontos_por_segmento[indice].update(comuns)
            pontos_por_segmento[outro_indice].update(comuns)

    arestas: dict[frozenset[PontoGeometrico], SegmentoGeometrico] = {}
    for segmento, pontos in zip(validados, pontos_por_segmento):
        ordenados = sorted(pontos, key=lambda ponto: _parametro_no_segmento(ponto, segmento))
        for inicio, fim in zip(ordenados, ordenados[1:]):
            if inicio == fim:
                continue
            primeiro, segundo = sorted((inicio, fim), key=lambda ponto: (ponto.x, ponto.y))
            arestas[frozenset((primeiro, segundo))] = SegmentoGeometrico(primeiro, segundo)
    return tuple(
        sorted(
            arestas.values(),
            key=lambda aresta: (
                aresta.inicio.x, aresta.inicio.y, aresta.fim.x, aresta.fim.y
            ),
        )
    )


def _comparar_direcoes(
    origem: PontoGeometrico, primeiro: PontoGeometrico, segundo: PontoGeometrico
) -> int:
    ax, ay = primeiro.x - origem.x, primeiro.y - origem.y
    bx, by = segundo.x - origem.x, segundo.y - origem.y
    metade_a = 0 if ay > 0 or (ay == 0 and ax >= 0) else 1
    metade_b = 0 if by > 0 or (by == 0 and bx >= 0) else 1
    if metade_a != metade_b:
        return -1 if metade_a < metade_b else 1
    cruzado = ax * by - ay * bx
    if cruzado != 0:
        return -1 if cruzado > 0 else 1
    return 0


def _dobro_area_assinada(vertices: Sequence[PontoGeometrico]) -> Fraction:
    return sum(
        atual.x * seguinte.y - seguinte.x * atual.y
        for atual, seguinte in zip(vertices, vertices[1:] + vertices[:1])
    )


def _simplificar_contorno(
    vertices: Sequence[PontoGeometrico],
) -> tuple[PontoGeometrico, ...]:
    simplificados = list(vertices)
    mudou = True
    while mudou and len(simplificados) >= 3:
        mudou = False
        resultado: list[PontoGeometrico] = []
        quantidade = len(simplificados)
        for indice, atual in enumerate(simplificados):
            anterior = simplificados[(indice - 1) % quantidade]
            seguinte = simplificados[(indice + 1) % quantidade]
            if _produto_vetorial(anterior, atual, seguinte) == 0:
                mudou = True
                continue
            resultado.append(atual)
        simplificados = resultado
    return tuple(simplificados)


def identificar_regioes_fechadas(
    segmentos: Sequence[SegmentoGeometrico],
) -> tuple[RegiaoFechada, ...]:
    """Identifica as faces limitadas formadas por uma rede de segmentos.

    Args:
        segmentos: Segmentos que serão divididos exatamente nos seus encontros.

    Returns:
        Regiões limitadas com vértices em sentido anti-horário. A face externa e
        percursos de área nula não são retornados.
    """

    atomicos = dividir_segmentos(segmentos)
    vizinhos: dict[PontoGeometrico, set[PontoGeometrico]] = defaultdict(set)
    for aresta in atomicos:
        vizinhos[aresta.inicio].add(aresta.fim)
        vizinhos[aresta.fim].add(aresta.inicio)

    ordenados = {
        ponto: sorted(
            destinos,
            key=cmp_to_key(lambda a, b, origem=ponto: _comparar_direcoes(origem, a, b)),
        )
        for ponto, destinos in vizinhos.items()
    }
    visitadas: set[tuple[PontoGeometrico, PontoGeometrico]] = set()
    regioes: list[RegiaoFechada] = []

    for inicio, destinos in ordenados.items():
        for destino in destinos:
            primeira = (inicio, destino)
            if primeira in visitadas:
                continue
            vertices: list[PontoGeometrico] = []
            atual, seguinte = primeira
            while (atual, seguinte) not in visitadas:
                visitadas.add((atual, seguinte))
                vertices.append(atual)
                opcoes = ordenados[seguinte]
                indice_retorno = opcoes.index(atual)
                atual, seguinte = seguinte, opcoes[(indice_retorno - 1) % len(opcoes)]
            contorno = _simplificar_contorno(vertices)
            if (atual, seguinte) == primeira and _dobro_area_assinada(contorno) > 0:
                regioes.append(RegiaoFechada(contorno))

    return tuple(regioes)
