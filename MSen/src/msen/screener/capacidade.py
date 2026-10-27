"""Extrapola custo do universo sem executar todas as combinações."""

from __future__ import annotations

from dataclasses import dataclass

from .gerador import TOTAL_COMBINACOES


@dataclass(frozen=True, slots=True)
class EstimativaCapacidade:
    """Resume uma extrapolação linear baseada em uma amostra medida."""

    tamanho_amostra: int
    duracao_amostra_segundos: float
    bytes_amostra: int
    combinacoes_por_segundo: float
    duracao_universo_segundos: float
    bytes_universo: float


def estimar_capacidade(
    tamanho_amostra: int, duracao_amostra_segundos: float, bytes_amostra: int = 0
) -> EstimativaCapacidade:
    """Projeta tempo e espaço linearmente para as 50.063.860 combinações."""

    if tamanho_amostra <= 0:
        raise ValueError("tamanho_amostra deve ser positivo")
    if duracao_amostra_segundos <= 0:
        raise ValueError("duracao_amostra_segundos deve ser positiva")
    if bytes_amostra < 0:
        raise ValueError("bytes_amostra não pode ser negativo")
    fator = TOTAL_COMBINACOES / tamanho_amostra
    return EstimativaCapacidade(
        tamanho_amostra=tamanho_amostra,
        duracao_amostra_segundos=duracao_amostra_segundos,
        bytes_amostra=bytes_amostra,
        combinacoes_por_segundo=tamanho_amostra / duracao_amostra_segundos,
        duracao_universo_segundos=duracao_amostra_segundos * fator,
        bytes_universo=bytes_amostra * fator,
    )
