"""Perfis estatísticos das medidas geométricas persistidas."""

from __future__ import annotations

from collections.abc import Callable, Iterable
from dataclasses import dataclass
from decimal import Decimal

from msen.database import AnaliseGeometricaPersistida

from .perfil_estatistico import PerfilEstatistico, calcular_perfil_estatistico


@dataclass(frozen=True, slots=True)
class PerfilParametroGeometrico:
    """Perfil de uma medida e contabilidade explícita de valores ausentes."""

    codigo: str
    perfil: PerfilEstatistico | None
    quantidade_total: int
    quantidade_com_valor: int
    quantidade_ausente: int


@dataclass(frozen=True, slots=True)
class PerfisGeometricos:
    """Reúne os seis perfis geométricos definidos no catálogo da Etapa 17."""

    extensao_aberta: PerfilParametroGeometrico
    perimetro_fechado: PerfilParametroGeometrico
    quantidade_regioes: PerfilParametroGeometrico
    area_total: PerfilParametroGeometrico
    centro_gravidade_x: PerfilParametroGeometrico
    centro_gravidade_y: PerfilParametroGeometrico

    @property
    def parametros(self) -> tuple[PerfilParametroGeometrico, ...]:
        """Devolve os parâmetros na ordem estável usada pelo catálogo."""

        return (
            self.extensao_aberta,
            self.perimetro_fechado,
            self.quantidade_regioes,
            self.area_total,
            self.centro_gravidade_x,
            self.centro_gravidade_y,
        )


def _criar_perfil(
    codigo: str,
    analises: tuple[AnaliseGeometricaPersistida, ...],
    extrair: Callable[[AnaliseGeometricaPersistida], Decimal | int | None],
) -> PerfilParametroGeometrico:
    valores = tuple(
        valor for analise in analises if (valor := extrair(analise)) is not None
    )
    return PerfilParametroGeometrico(
        codigo=codigo,
        perfil=None if not valores else calcular_perfil_estatistico(valores),
        quantidade_total=len(analises),
        quantidade_com_valor=len(valores),
        quantidade_ausente=len(analises) - len(valores),
    )


def _validar_analises(
    analises: Iterable[AnaliseGeometricaPersistida],
) -> tuple[AnaliseGeometricaPersistida, ...]:
    try:
        serie = tuple(analises)
    except TypeError as erro:
        raise TypeError("As análises geométricas devem ser iteráveis.") from erro
    if any(not isinstance(item, AnaliseGeometricaPersistida) for item in serie):
        raise TypeError("São aceitas somente análises geométricas persistidas.")
    ids = tuple(item.id_resultado for item in serie)
    if len(ids) != len(set(ids)):
        raise ValueError("Um resultado não pode aparecer duas vezes no perfil geométrico.")
    for item in serie:
        if (item.centro_gravidade_x is None) != (item.centro_gravidade_y is None):
            raise ValueError("As coordenadas do centro devem estar presentes ou ausentes juntas.")
        if (item.area_total == 0) != (item.centro_gravidade_x is None):
            raise ValueError("Área e centro de gravidade são incoerentes.")
    return tuple(sorted(serie, key=lambda item: item.id_resultado))


def calcular_perfis_geometricos(
    analises: Iterable[AnaliseGeometricaPersistida],
) -> PerfisGeometricos:
    """Aplica o perfil genérico às seis medidas geométricas da tabela.

    Centros nulos em figuras sem área permanecem ausentes. Eles não são
    substituídos por zero e não entram na média ou no desvio das coordenadas.
    Uma série vazia é representada por seis perfis sem valores, não por medidas
    estatísticas inventadas.
    """

    serie = _validar_analises(analises)
    return PerfisGeometricos(
        extensao_aberta=_criar_perfil(
            "GEO_EXTENSAO_ABERTA", serie, lambda item: item.extensao_aberta
        ),
        perimetro_fechado=_criar_perfil(
            "GEO_PERIMETRO_FECHADO", serie, lambda item: item.perimetro_fechado
        ),
        quantidade_regioes=_criar_perfil(
            "GEO_QUANTIDADE_REGIOES", serie, lambda item: item.quantidade_regioes
        ),
        area_total=_criar_perfil(
            "GEO_AREA_TOTAL", serie, lambda item: item.area_total
        ),
        centro_gravidade_x=_criar_perfil(
            "GEO_CENTRO_GRAVIDADE_X", serie, lambda item: item.centro_gravidade_x
        ),
        centro_gravidade_y=_criar_perfil(
            "GEO_CENTRO_GRAVIDADE_Y", serie, lambda item: item.centro_gravidade_y
        ),
    )
