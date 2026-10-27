"""Executa e resume marcações hipotéticas sem excluir combinações."""

from __future__ import annotations

from collections.abc import Callable, Iterable
from dataclasses import dataclass
from time import perf_counter

from .funil import CriterioFunil
from .gerador import Combinacao


@dataclass(frozen=True, slots=True)
class ResultadoSimulacaoSombra:
    """Resume contagem, saldo hipotético, tempo e exemplos de uma simulação."""

    semente: int
    total_avaliado: int
    total_marcado: int
    percentual_marcado: float
    saldo_hipotetico: int
    total_aprovado_real: int
    total_excluido_real: int
    duracao_segundos: float
    exemplos_marcados: tuple[Combinacao, ...]


def simular_modo_sombra(
    combinacoes: Iterable[Combinacao],
    criterio: CriterioFunil,
    *,
    semente: int,
    limite_exemplos: int = 20,
    relogio: Callable[[], float] = perf_counter,
) -> ResultadoSimulacaoSombra:
    """Conta `marcaria_exclusao`, exigindo que a decisão real sempre aprove."""

    if isinstance(semente, bool) or not isinstance(semente, int) or semente < 0:
        raise ValueError("semente deve ser inteira e não negativa")
    if isinstance(limite_exemplos, bool) or not isinstance(limite_exemplos, int):
        raise TypeError("limite_exemplos deve ser inteiro")
    if limite_exemplos < 0:
        raise ValueError("limite_exemplos não pode ser negativo")

    inicio = relogio()
    total = 0
    marcadas = 0
    exemplos: list[Combinacao] = []
    for combinacao in combinacoes:
        total += 1
        decisao = criterio.avaliar(combinacao)
        if not decisao.aprovada:
            raise ValueError("um critério sombra não pode reprovar combinações")
        marca = decisao.valores.get("marcaria_exclusao")
        if not isinstance(marca, bool):
            raise ValueError("a decisão sombra deve informar marcaria_exclusao")
        if marca:
            marcadas += 1
            if len(exemplos) < limite_exemplos:
                exemplos.append(combinacao)
    duracao = relogio() - inicio
    if duracao < 0:
        raise ValueError("o relógio da simulação não pode retroceder")
    percentual = 0.0 if total == 0 else marcadas * 100 / total
    return ResultadoSimulacaoSombra(
        semente=semente,
        total_avaliado=total,
        total_marcado=marcadas,
        percentual_marcado=percentual,
        saldo_hipotetico=total - marcadas,
        total_aprovado_real=total,
        total_excluido_real=0,
        duracao_segundos=duracao,
        exemplos_marcados=tuple(exemplos),
    )
