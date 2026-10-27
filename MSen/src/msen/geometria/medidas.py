"""Áreas e centros de gravidade das regiões formadas pelo percurso."""

from dataclasses import dataclass
from fractions import Fraction

from .caminho import PontoGeometrico, construir_percurso_fechado
from .regioes import RegiaoFechada, identificar_regioes_fechadas


@dataclass(frozen=True, slots=True)
class MedidaRegiao:
    """Reúne a área exata e o centroide de uma região fechada."""

    area: Fraction
    centroide: PontoGeometrico | None


@dataclass(frozen=True, slots=True)
class ResultadoGeometrico:
    """Reúne as regiões, sua área total e um centro de gravidade global."""

    regioes: tuple[RegiaoFechada, ...]
    medidas_regioes: tuple[MedidaRegiao, ...]
    area_total: Fraction
    centro_gravidade: PontoGeometrico | None


def medir_regiao(regiao: RegiaoFechada) -> MedidaRegiao:
    """Calcula a área e o centroide exatos de uma região fechada.

    Args:
        regiao: Contorno de uma região, em qualquer orientação.

    Returns:
        Área positiva e centroide. Um contorno degenerado produz área zero e
        centroide nulo.

    Raises:
        TypeError: Se o argumento não for uma região geométrica.
    """

    if not isinstance(regiao, RegiaoFechada):
        raise TypeError("A medição exige uma região fechada.")
    vertices = regiao.vertices
    if len(vertices) < 3:
        return MedidaRegiao(Fraction(0), None)

    dobro_area_assinada = Fraction(0)
    soma_x = Fraction(0)
    soma_y = Fraction(0)
    for atual, seguinte in zip(vertices, vertices[1:] + vertices[:1]):
        cruzado = atual.x * seguinte.y - seguinte.x * atual.y
        dobro_area_assinada += cruzado
        soma_x += (atual.x + seguinte.x) * cruzado
        soma_y += (atual.y + seguinte.y) * cruzado

    if dobro_area_assinada == 0:
        return MedidaRegiao(Fraction(0), None)

    centroide = PontoGeometrico(
        soma_x / (3 * dobro_area_assinada),
        soma_y / (3 * dobro_area_assinada),
    )
    return MedidaRegiao(abs(dobro_area_assinada) / 2, centroide)


def consolidar_regioes(regioes: tuple[RegiaoFechada, ...]) -> ResultadoGeometrico:
    """Soma áreas e calcula o centro de gravidade ponderado das regiões.

    Args:
        regioes: Regiões limitadas identificadas na rede planar.

    Returns:
        Medidas individuais, área total positiva e um único centro de gravidade.
        Sem área positiva, o centro de gravidade é nulo.
    """

    if not isinstance(regioes, tuple) or any(
        not isinstance(regiao, RegiaoFechada) for regiao in regioes
    ):
        raise TypeError("A consolidação exige uma tupla de regiões fechadas.")
    medidas = tuple(medir_regiao(regiao) for regiao in regioes)
    area_total = sum((medida.area for medida in medidas), Fraction(0))
    if area_total == 0:
        return ResultadoGeometrico(regioes, medidas, area_total, None)

    centro_gravidade = PontoGeometrico(
        sum(
            medida.area * medida.centroide.x
            for medida in medidas
            if medida.centroide is not None
        )
        / area_total,
        sum(
            medida.area * medida.centroide.y
            for medida in medidas
            if medida.centroide is not None
        )
        / area_total,
    )
    return ResultadoGeometrico(regioes, medidas, area_total, centro_gravidade)


def calcular_area_e_centro_gravidade(dezenas: tuple[int, ...]) -> ResultadoGeometrico:
    """Calcula regiões, área total e centro de gravidade de seis dezenas.

    Args:
        dezenas: Seis dezenas distintas entre 01 e 60, em qualquer ordem.

    Returns:
        Resultado exato da figura construída com as dezenas em ordem crescente.
    """

    percurso = construir_percurso_fechado(dezenas)
    return consolidar_regioes(identificar_regioes_fechadas(percurso))
