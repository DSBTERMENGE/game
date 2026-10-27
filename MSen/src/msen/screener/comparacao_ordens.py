"""Compara ordens do funil sem alterar regras, amostra ou decisão final."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from time import perf_counter

from .ativacao import ORDEM_ATIVA_PADRAO, executar_padroes_ativos
from .configuracao import ConfiguracaoScreener


@dataclass(frozen=True, slots=True)
class ResultadoOrdemFiltros:
    """Resume custo e resultado observado para uma ordem dos filtros."""

    nome: str
    ordem: tuple[str, ...]
    total_avaliacoes: int
    avaliacoes_evitadas: int
    duracao_segundos: float
    total_aprovado: int
    exclusoes_por_criterio: Mapping[str, int]


ORDENS_EXPERIMENTAIS = {
    "atual": ORDEM_ATIVA_PADRAO,
    "historicos_frequentes_primeiro": (
        "PD_002", "PD_005", "PD_003", "PD_006",
        "EST_DESVIO_P01_P99", "EST_MEDIA_P01_P99",
        "GEO_EXTENSAO_P01_P99", "EST_MEDIANA_P01_P99",
    ),
    "geometria_e_estatisticas_primeiro": (
        "GEO_EXTENSAO_P01_P99", "EST_DESVIO_P01_P99",
        "EST_MEDIA_P01_P99", "EST_MEDIANA_P01_P99",
        "PD_002", "PD_005", "PD_003", "PD_006",
    ),
}


def comparar_ordens_filtros(
    configuracao: ConfiguracaoScreener,
    ordens: Mapping[str, tuple[str, ...]] = ORDENS_EXPERIMENTAIS,
    *,
    relogio: Callable[[], float] = perf_counter,
) -> tuple[ResultadoOrdemFiltros, ...]:
    """Executa ordens sobre a mesma amostra e exige o mesmo conjunto aprovado."""

    resultados: list[ResultadoOrdemFiltros] = []
    aprovadas_referencia = None
    maximo_avaliacoes = configuracao.limite_combinacoes * len(ORDEM_ATIVA_PADRAO)
    for nome, ordem in ordens.items():
        inicio = relogio()
        relatorio = executar_padroes_ativos(configuracao, ordem)
        duracao = relogio() - inicio
        if duracao < 0:
            raise ValueError("o relógio da comparação não pode retroceder")
        aprovadas = frozenset(relatorio.combinacoes_aprovadas)
        if aprovadas_referencia is None:
            aprovadas_referencia = aprovadas
        elif aprovadas != aprovadas_referencia:
            raise RuntimeError("a ordem alterou o conjunto final de combinações")
        total_avaliacoes = sum(relatorio.avaliacoes_por_criterio.values())
        resultados.append(
            ResultadoOrdemFiltros(
                nome=nome,
                ordem=relatorio.ordem_criterios,
                total_avaliacoes=total_avaliacoes,
                avaliacoes_evitadas=maximo_avaliacoes - total_avaliacoes,
                duracao_segundos=duracao,
                total_aprovado=relatorio.total_aprovado,
                exclusoes_por_criterio=relatorio.exclusoes_por_criterio,
            )
        )
    return tuple(resultados)
