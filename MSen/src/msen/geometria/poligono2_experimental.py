"""Primeira poda experimental das ligações candidatas do Polígono 2."""

from dataclasses import dataclass
from math import atan2, tau
from collections import deque
from collections.abc import Sequence

from .caminho import PontoGeometrico, construir_vertices


@dataclass(frozen=True, slots=True, order=True)
class ArestaExperimental:
    dezena_a: int
    dezena_b: int


@dataclass(frozen=True, slots=True)
class DiagnosticoPoligono2Experimental:
    arestas: tuple[ArestaExperimental, ...]
    graus: tuple[tuple[int, int], ...]
    escolhas_por_dezena: tuple[tuple[int, tuple[int, int]], ...]
    quantidade_arestas: int
    conectado: bool
    possui_cruzamento: bool
    circuito_pronto: bool


def _aresta(a: int, b: int) -> ArestaExperimental:
    return ArestaExperimental(*sorted((a, b)))


def _orientacao(a: PontoGeometrico, b: PontoGeometrico, c: PontoGeometrico):
    return (b.x - a.x) * (c.y - a.y) - (b.y - a.y) * (c.x - a.x)


def _entre(a, b, valor) -> bool:
    return min(a, b) <= valor <= max(a, b)


def _segmentos_cruzam(a, b, c, d) -> bool:
    o1, o2 = _orientacao(a, b, c), _orientacao(a, b, d)
    o3, o4 = _orientacao(c, d, a), _orientacao(c, d, b)
    if o1 == 0 and _entre(a.x, b.x, c.x) and _entre(a.y, b.y, c.y):
        return True
    if o2 == 0 and _entre(a.x, b.x, d.x) and _entre(a.y, b.y, d.y):
        return True
    if o3 == 0 and _entre(c.x, d.x, a.x) and _entre(c.y, d.y, a.y):
        return True
    if o4 == 0 and _entre(c.x, d.x, b.x) and _entre(c.y, d.y, b.y):
        return True
    return (o1 > 0) != (o2 > 0) and (o3 > 0) != (o4 > 0)


def _duas_extremidades(
    origem: int, ponto_origem: PontoGeometrico,
    dezenas: tuple[int, ...], pontos: dict[int, PontoGeometrico],
) -> tuple[int, int]:
    raios = sorted(
        (
            (atan2(float(pontos[dezena].y - ponto_origem.y),
                   float(pontos[dezena].x - ponto_origem.x)) % tau, dezena)
            for dezena in dezenas if dezena != origem
        ),
        key=lambda item: (item[0], item[1]),
    )
    setores = []
    for indice, (angulo, dezena) in enumerate(raios):
        proximo_angulo, proxima_dezena = raios[(indice + 1) % len(raios)]
        abertura = (proximo_angulo - angulo) % tau
        setores.append((abertura, tuple(sorted((dezena, proxima_dezena)))))
    maior = max(abertura for abertura, _ in setores)
    # Empates geométricos recebem sempre a mesma solução.
    return min(par for abertura, par in setores if abs(abertura - maior) < 1e-12)


def analisar_poligono2_experimental(
    dezenas_entrada: Sequence[int],
) -> DiagnosticoPoligono2Experimental:
    """Mantém, em cada ponto, os raios que limitam seu maior setor vazio.

    A união pode conter mais de seis arestas. Este estágio diagnostica esses
    excedentes; ele ainda não escolhe automaticamente quais devem ser retirados.
    """

    vertices = construir_vertices(dezenas_entrada)
    dezenas = tuple(sorted(dezenas_entrada))
    pontos = dict(zip(dezenas, vertices))
    escolhas = tuple(
        (dezena, _duas_extremidades(dezena, pontos[dezena], dezenas, pontos))
        for dezena in dezenas
    )
    arestas = tuple(sorted({
        _aresta(origem, destino)
        for origem, destinos in escolhas for destino in destinos
    }))
    graus = {dezena: 0 for dezena in dezenas}
    vizinhos = {dezena: set() for dezena in dezenas}
    for aresta in arestas:
        graus[aresta.dezena_a] += 1
        graus[aresta.dezena_b] += 1
        vizinhos[aresta.dezena_a].add(aresta.dezena_b)
        vizinhos[aresta.dezena_b].add(aresta.dezena_a)

    visitados = set()
    fila = deque((dezenas[0],))
    while fila:
        atual = fila.popleft()
        if atual in visitados:
            continue
        visitados.add(atual)
        fila.extend(vizinhos[atual] - visitados)

    cruzamento = False
    for indice, primeira in enumerate(arestas):
        for segunda in arestas[indice + 1:]:
            extremos_primeira = {primeira.dezena_a, primeira.dezena_b}
            extremos_segunda = {segunda.dezena_a, segunda.dezena_b}
            if extremos_primeira & extremos_segunda:
                continue
            if _segmentos_cruzam(
                pontos[primeira.dezena_a], pontos[primeira.dezena_b],
                pontos[segunda.dezena_a], pontos[segunda.dezena_b],
            ):
                cruzamento = True
                break
        if cruzamento:
            break

    conectado = len(visitados) == 6
    graus_ordenados = tuple(sorted(graus.items()))
    pronto = (
        len(arestas) == 6 and conectado and not cruzamento
        and all(grau == 2 for _, grau in graus_ordenados)
    )
    return DiagnosticoPoligono2Experimental(
        arestas=arestas,
        graus=graus_ordenados,
        escolhas_por_dezena=escolhas,
        quantidade_arestas=len(arestas),
        conectado=conectado,
        possui_cruzamento=cruzamento,
        circuito_pronto=pronto,
    )
