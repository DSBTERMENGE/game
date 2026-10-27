"""Construção do percurso crescente e cálculo de suas medidas básicas."""

from collections.abc import Sequence
from dataclasses import dataclass
from decimal import Decimal, localcontext
from fractions import Fraction

from msen.calculos import calcular_coordenada


@dataclass(frozen=True, slots=True)
class PontoGeometrico:
    """Representa um ponto lógico exato na matriz das dezenas."""

    x: Fraction
    y: Fraction


@dataclass(frozen=True, slots=True)
class SegmentoGeometrico:
    """Representa um segmento orientado entre dois pontos lógicos."""

    inicio: PontoGeometrico
    fim: PontoGeometrico


def _validar_e_ordenar(dezenas: Sequence[int]) -> tuple[int, ...]:
    if isinstance(dezenas, (str, bytes)) or not isinstance(dezenas, Sequence):
        raise TypeError("A geometria exige uma sequência com seis dezenas.")
    if len(dezenas) != 6:
        raise ValueError("A geometria exige exatamente seis dezenas.")
    if any(isinstance(numero, bool) or not isinstance(numero, int) for numero in dezenas):
        raise TypeError("As dezenas da geometria devem ser números inteiros.")
    if any(numero < 1 or numero > 60 for numero in dezenas):
        raise ValueError("As dezenas da geometria devem estar entre 1 e 60.")
    if len(set(dezenas)) != 6:
        raise ValueError("As seis dezenas da geometria devem ser diferentes.")
    return tuple(sorted(dezenas))


def construir_vertices(dezenas: Sequence[int]) -> tuple[PontoGeometrico, ...]:
    """Converte seis dezenas em vértices ordenados crescentemente.

    Args:
        dezenas: Seis inteiros diferentes, cada um entre 1 e 60.

    Returns:
        Os seis centros lógicos exatos na ordem crescente das dezenas.
    """

    vertices: list[PontoGeometrico] = []
    for dezena in _validar_e_ordenar(dezenas):
        x, y = calcular_coordenada(dezena)
        vertices.append(PontoGeometrico(Fraction(x), Fraction(y)))
    return tuple(vertices)


def construir_caminho_aberto(
    dezenas: Sequence[int],
) -> tuple[SegmentoGeometrico, ...]:
    """Constrói os cinco segmentos entre as dezenas crescentes.

    Args:
        dezenas: Seis dezenas válidas em qualquer ordem de entrada.

    Returns:
        Cinco segmentos orientados do menor para o maior número.
    """

    vertices = construir_vertices(dezenas)
    return tuple(
        SegmentoGeometrico(inicio, fim)
        for inicio, fim in zip(vertices, vertices[1:])
    )


def construir_percurso_fechado(
    dezenas: Sequence[int],
) -> tuple[SegmentoGeometrico, ...]:
    """Constrói o caminho crescente e o segmento da última à primeira dezena.

    Args:
        dezenas: Seis dezenas válidas em qualquer ordem de entrada.

    Returns:
        Seis segmentos, incluindo o fechamento do percurso.
    """

    vertices = construir_vertices(dezenas)
    destinos = vertices[1:] + vertices[:1]
    return tuple(
        SegmentoGeometrico(inicio, fim)
        for inicio, fim in zip(vertices, destinos)
    )


def _decimal_exato(valor: Fraction) -> Decimal:
    return Decimal(valor.numerator) / Decimal(valor.denominator)


def _comprimento(segmento: SegmentoGeometrico) -> Decimal:
    delta_x = _decimal_exato(segmento.fim.x - segmento.inicio.x)
    delta_y = _decimal_exato(segmento.fim.y - segmento.inicio.y)
    return (delta_x * delta_x + delta_y * delta_y).sqrt()


def _somar_comprimentos(segmentos: Sequence[SegmentoGeometrico]) -> Decimal:
    with localcontext() as contexto:
        contexto.prec = 28
        return sum((_comprimento(segmento) for segmento in segmentos), Decimal(0))


def calcular_extensao_aberta(dezenas: Sequence[int]) -> Decimal:
    """Calcula a soma euclidiana dos cinco segmentos do caminho aberto.

    Args:
        dezenas: Seis dezenas válidas em qualquer ordem de entrada.

    Returns:
        A extensão em unidades lógicas, com precisão decimal de 28 dígitos.
    """

    return _somar_comprimentos(construir_caminho_aberto(dezenas))


def calcular_perimetro_fechado(dezenas: Sequence[int]) -> Decimal:
    """Calcula a extensão do caminho acrescida do segmento de fechamento.

    Args:
        dezenas: Seis dezenas válidas em qualquer ordem de entrada.

    Returns:
        O perímetro do percurso em unidades lógicas decimais.
    """

    return _somar_comprimentos(construir_percurso_fechado(dezenas))
