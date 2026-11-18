"""Contrato comum das coleções submetidas ao motor do Screener.

Este módulo descreve somente a origem e o fluxo das combinações. Filtros,
referências históricas e decisões pertencem a outros contratos do Screener.
"""

from __future__ import annotations

from collections.abc import Iterable, Iterator, Mapping
from dataclasses import dataclass
from types import MappingProxyType

from .gerador import Combinacao


ORIGEM_TESTE_5000 = "TESTE_5000"
ORIGEM_APLICACAO_INTEGRAL = "APLICACAO_INTEGRAL"
ORIGEM_SELECAO_DEZENAS = "SELECAO_DE_DEZENAS"
ORIGENS_SCREENER = frozenset({
    ORIGEM_TESTE_5000,
    ORIGEM_APLICACAO_INTEGRAL,
    ORIGEM_SELECAO_DEZENAS,
})


class ErroEntradaCombinacoes(ValueError):
    """Indica uma coleção incompatível com o motor comum do Screener."""


def _normalizar_combinacao(valor: object) -> Combinacao:
    if not isinstance(valor, (tuple, list)) or len(valor) != 6:
        raise ErroEntradaCombinacoes(
            "Cada combinação deve ser uma lista ou tupla com seis dezenas."
        )
    if any(type(dezena) is not int or not 1 <= dezena <= 60 for dezena in valor):
        raise ErroEntradaCombinacoes(
            "As dezenas devem ser números inteiros entre 1 e 60."
        )
    if len(set(valor)) != 6:
        raise ErroEntradaCombinacoes("Uma combinação não pode repetir dezenas.")
    return tuple(sorted(valor))  # type: ignore[return-value]


def _iterar_normalizadas(itens: Iterable[object]) -> Iterator[Combinacao]:
    """Valida cada item somente quando o motor o solicitar."""

    for item in itens:
        yield _normalizar_combinacao(item)


@dataclass(frozen=True, slots=True)
class EntradaCombinacoesScreener:
    """Coleção preguiçosa e identificada entregue ao motor comum.

    ``total_combinacoes`` permite progresso e reconciliação sem materializar a
    coleção. ``itens`` pode, portanto, representar tanto 5.000 combinações
    quanto todo o universo de 50.063.860 ou uma seleção variável de dezenas.
    """

    origem: str
    total_combinacoes: int
    itens: Iterable[Combinacao]
    contexto: Mapping[str, object]


def criar_entrada_combinacoes(
    *,
    origem: str,
    total_combinacoes: int,
    itens: Iterable[object],
    contexto: Mapping[str, object] | None = None,
) -> EntradaCombinacoesScreener:
    """Valida o envelope sem percorrer antecipadamente suas combinações."""

    if origem not in ORIGENS_SCREENER:
        raise ErroEntradaCombinacoes("A origem das combinações não é reconhecida.")
    if (
        isinstance(total_combinacoes, bool)
        or not isinstance(total_combinacoes, int)
        or total_combinacoes <= 0
    ):
        raise ErroEntradaCombinacoes(
            "A quantidade total de combinações deve ser um inteiro positivo."
        )
    if not isinstance(itens, Iterable):
        raise ErroEntradaCombinacoes("As combinações devem formar um iterável.")
    if contexto is not None and not isinstance(contexto, Mapping):
        raise ErroEntradaCombinacoes("O contexto deve ser um mapeamento.")

    return EntradaCombinacoesScreener(
        origem=origem,
        total_combinacoes=total_combinacoes,
        itens=_iterar_normalizadas(itens),
        contexto=MappingProxyType(dict(contexto or {})),
    )
