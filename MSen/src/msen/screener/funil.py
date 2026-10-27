"""Estrutura sequencial do funil e contabilidade das combinações."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from types import MappingProxyType
from typing import Protocol

from .gerador import Combinacao


class ErroFunil(ValueError):
    """Indica contrato inválido de critério ou decisão durante o funil."""

    def __init__(self, codigo: str, mensagem: str) -> None:
        super().__init__(mensagem)
        self.codigo = codigo


@dataclass(frozen=True, slots=True)
class DecisaoCriterio:
    """Informa se uma combinação passou e os valores usados na decisão."""

    aprovada: bool
    codigo_criterio: str
    valores: Mapping[str, object]


class CriterioFunil(Protocol):
    """Contrato mínimo que os adaptadores de critério deverão implementar."""

    codigo: str

    def avaliar(self, combinacao: Combinacao) -> DecisaoCriterio:
        """Avalia uma combinação sem produzir efeitos externos."""


@dataclass(frozen=True, slots=True)
class RelatorioFunil:
    """Consolida entradas, exclusões, saldos e combinações aprovadas."""

    total_recebido: int
    total_aprovado: int
    ordem_criterios: tuple[str, ...]
    avaliacoes_por_criterio: Mapping[str, int]
    exclusoes_por_criterio: Mapping[str, int]
    saldo_apos_criterio: Mapping[str, int]
    combinacoes_aprovadas: tuple[Combinacao, ...]


def _validar_criterios(criterios: tuple[CriterioFunil, ...]) -> tuple[str, ...]:
    """Exige códigos preenchidos e exclusivos, preservando a ordem recebida."""

    codigos = tuple(getattr(criterio, "codigo", "") for criterio in criterios)
    if any(not isinstance(codigo, str) or not codigo.strip() for codigo in codigos):
        raise ErroFunil("CODIGO_CRITERIO_INVALIDO", "Todo critério deve possuir código.")
    if len(set(codigos)) != len(codigos):
        raise ErroFunil("CODIGO_CRITERIO_DUPLICADO", "Os códigos dos critérios devem ser únicos.")
    return codigos


def executar_funil(
    combinacoes: Iterable[Combinacao], criterios: Iterable[CriterioFunil]
) -> RelatorioFunil:
    """Executa critérios em ordem e encerra a combinação na primeira reprovação.

    O relatório atribui cada exclusão somente ao primeiro critério que a
    detectou. Assim, a soma das exclusões com o total aprovado sempre coincide
    com o total recebido.
    """

    criterios_fixos = tuple(criterios)
    codigos = _validar_criterios(criterios_fixos)
    avaliacoes = dict.fromkeys(codigos, 0)
    exclusoes = dict.fromkeys(codigos, 0)
    aprovadas: list[Combinacao] = []
    total = 0

    for combinacao in combinacoes:
        total += 1
        for criterio in criterios_fixos:
            avaliacoes[criterio.codigo] += 1
            decisao = criterio.avaliar(combinacao)
            if not isinstance(decisao, DecisaoCriterio):
                raise ErroFunil(
                    "DECISAO_INVALIDA", "O critério deve retornar DecisaoCriterio."
                )
            if decisao.codigo_criterio != criterio.codigo:
                raise ErroFunil(
                    "CODIGO_DECISAO_DIVERGENTE",
                    "O código da decisão deve coincidir com o do critério.",
                )
            if not decisao.aprovada:
                exclusoes[criterio.codigo] += 1
                break
        else:
            aprovadas.append(combinacao)

    saldo = total
    saldos: dict[str, int] = {}
    for codigo in codigos:
        saldo -= exclusoes[codigo]
        saldos[codigo] = saldo

    return RelatorioFunil(
        total_recebido=total,
        total_aprovado=len(aprovadas),
        ordem_criterios=codigos,
        avaliacoes_por_criterio=MappingProxyType(avaliacoes),
        exclusoes_por_criterio=MappingProxyType(exclusoes),
        saldo_apos_criterio=MappingProxyType(saldos),
        combinacoes_aprovadas=tuple(aprovadas),
    )
