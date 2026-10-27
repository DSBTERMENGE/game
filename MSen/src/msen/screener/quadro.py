"""Medição e quadro de avaliação reproduzível dos ensaios do screener."""

from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass
from time import perf_counter

from .configuracao import ConfiguracaoScreener
from .funil import CriterioFunil, RelatorioFunil, executar_funil
from .gerador import Combinacao


@dataclass(frozen=True, slots=True)
class LinhaQuadroAvaliacao:
    """Apresenta o efeito de um critério na posição em que foi executado."""

    ordem: int
    codigo_criterio: str
    avaliacoes: int
    exclusoes: int
    saldo: int


@dataclass(frozen=True, slots=True)
class QuadroAvaliacao:
    """Reúne configuração, tempo e contabilidade completa de um ensaio."""

    versao_configuracao: int
    modo: str
    semente: int
    limite_configurado: int
    duracao_segundos: float
    total_recebido: int
    total_aprovado: int
    linhas: tuple[LinhaQuadroAvaliacao, ...]
    configuracao_criterios: Mapping[str, Mapping[str, object]]
    relatorio: RelatorioFunil


def _resumir_criterios(
    configuracao: ConfiguracaoScreener,
) -> dict[str, Mapping[str, object]]:
    """Copia somente os valores necessários para reproduzir o ensaio."""

    return {
        codigo: {
            "habilitado": criterio.habilitado,
            "tolerancias": dict(criterio.tolerancias),
        }
        for codigo, criterio in configuracao.criterios.items()
    }


def executar_ensaio(
    combinacoes: Iterable[Combinacao],
    criterios: Iterable[CriterioFunil],
    configuracao: ConfiguracaoScreener,
    *,
    relogio: Callable[[], float] = perf_counter,
) -> QuadroAvaliacao:
    """Executa o funil, mede sua duração e monta o quadro de avaliação."""

    if not isinstance(configuracao, ConfiguracaoScreener):
        raise TypeError("configuracao deve ser uma ConfiguracaoScreener validada")
    inicio = relogio()
    relatorio = executar_funil(combinacoes, criterios)
    duracao = relogio() - inicio
    if duracao < 0:
        raise ValueError("o relógio do ensaio não pode retroceder")

    linhas = tuple(
        LinhaQuadroAvaliacao(
            ordem=ordem,
            codigo_criterio=codigo,
            avaliacoes=relatorio.avaliacoes_por_criterio[codigo],
            exclusoes=relatorio.exclusoes_por_criterio[codigo],
            saldo=relatorio.saldo_apos_criterio[codigo],
        )
        for ordem, codigo in enumerate(relatorio.ordem_criterios, start=1)
    )
    return QuadroAvaliacao(
        versao_configuracao=configuracao.versao,
        modo=configuracao.modo,
        semente=configuracao.semente,
        limite_configurado=configuracao.limite_combinacoes,
        duracao_segundos=duracao,
        total_recebido=relatorio.total_recebido,
        total_aprovado=relatorio.total_aprovado,
        linhas=linhas,
        configuracao_criterios=_resumir_criterios(configuracao),
        relatorio=relatorio,
    )


def serializar_quadro_avaliacao(quadro: QuadroAvaliacao) -> dict[str, object]:
    """Converte o quadro em dados simples adequados a JSON, API ou futura tela."""

    if not isinstance(quadro, QuadroAvaliacao):
        raise TypeError("quadro deve ser um QuadroAvaliacao")
    return {
        "configuracao": {
            "versao": quadro.versao_configuracao,
            "modo": quadro.modo,
            "semente": quadro.semente,
            "limite_combinacoes": quadro.limite_configurado,
            "criterios": {
                codigo: {
                    "habilitado": valores["habilitado"],
                    "tolerancias": dict(valores["tolerancias"]),
                }
                for codigo, valores in quadro.configuracao_criterios.items()
            },
        },
        "duracao_segundos": quadro.duracao_segundos,
        "total_recebido": quadro.total_recebido,
        "total_aprovado": quadro.total_aprovado,
        "linhas": [
            {
                "ordem": linha.ordem,
                "codigo_criterio": linha.codigo_criterio,
                "avaliacoes": linha.avaliacoes,
                "exclusoes": linha.exclusoes,
                "saldo": linha.saldo,
            }
            for linha in quadro.linhas
        ],
    }
