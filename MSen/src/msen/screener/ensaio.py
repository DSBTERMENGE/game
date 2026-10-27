"""Orquestra o ensaio integrado seguro enquanto não há filtros aprovados."""

from __future__ import annotations

from collections.abc import Callable
from time import perf_counter

from .configuracao import ConfiguracaoScreener
from .gerador import gerar_amostra
from .quadro import QuadroAvaliacao, executar_ensaio


class ErroEnsaioIntegrado(ValueError):
    """Indica quebra das proteções ou da contabilidade do ensaio integrado."""

    def __init__(self, codigo: str, mensagem: str) -> None:
        super().__init__(mensagem)
        self.codigo = codigo


def executar_ensaio_amostral(
    configuracao: ConfiguracaoScreener,
    *,
    relogio: Callable[[], float] = perf_counter,
) -> QuadroAvaliacao:
    """Executa geração, funil vazio e quadro para a amostra configurada.

    Nesta fase, qualquer critério habilitado interrompe o ensaio. A função
    somente poderá receber filtros quando suas regras de exclusão forem
    aprovadas e conectadas explicitamente em uma etapa futura.
    """

    if not isinstance(configuracao, ConfiguracaoScreener):
        raise TypeError("configuracao deve ser uma ConfiguracaoScreener validada")
    if (
        any(item.habilitado for item in configuracao.criterios.values())
        or configuracao.regras
        or configuracao.regras_estatisticas
        or configuracao.regras_geometricas
    ):
        raise ErroEnsaioIntegrado(
            "CRITERIO_REAL_NAO_AUTORIZADO",
            "O ensaio integrado ainda não autoriza critérios reais.",
        )

    amostra = gerar_amostra(configuracao)
    quadro = executar_ensaio(amostra, (), configuracao, relogio=relogio)
    if quadro.total_recebido != configuracao.limite_combinacoes:
        raise ErroEnsaioIntegrado(
            "TOTAL_RECEBIDO_DIVERGENTE", "O funil não recebeu toda a amostra."
        )
    if quadro.total_aprovado != quadro.total_recebido or quadro.linhas:
        raise ErroEnsaioIntegrado(
            "CONTABILIDADE_SEM_FILTROS_INVALIDA",
            "Um ensaio sem filtros deve aprovar toda a amostra.",
        )
    return quadro
