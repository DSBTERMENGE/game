"""Backtest da seleção de dezenas, sem persistência de resultados derivados."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
from time import monotonic
from typing import Callable

import psycopg

from msen.database.fonte_backtest_repository import (
    ErroFonteBacktest,
    RepositorioFonteBacktest,
)
from msen.database.pesquisa_selecao_repository import RepositorioPesquisaSelecao

from .selecao_dezenas import selecionar_dezenas_para_alvo


SEIS_CASAS = Decimal("0.000001")


class ErroBacktest(RuntimeError):
    def __init__(self, codigo: str, mensagem: str) -> None:
        super().__init__(mensagem)
        self.codigo = codigo


@dataclass(frozen=True, slots=True)
class PontoBacktest:
    concurso: int
    quantidade_dezenas: int
    quantidade_acertos: int


@dataclass(frozen=True, slots=True)
class ClasseBacktest:
    classe: int
    quantidade: int
    percentual: Decimal


@dataclass(frozen=True, slots=True)
class ResumoBacktest:
    testes_efetuados: int
    classes: tuple[ClasseBacktest, ...]
    minimo_dezenas: int
    maximo_dezenas: int
    media_dezenas: Decimal
    media_acertos: Decimal
    concursos_premiados: int
    percentual_premiados: Decimal


@dataclass(frozen=True, slots=True)
class RelatorioBacktest:
    id_configuracao_selecao: int
    concurso_inicial: int
    concurso_final: int
    pontos: tuple[PontoBacktest, ...]
    resumo: ResumoBacktest
    duracao_segundos: Decimal


def _dividir(numerador: int, denominador: int) -> Decimal:
    return (Decimal(numerador) / Decimal(denominador)).quantize(
        SEIS_CASAS, rounding=ROUND_HALF_UP
    )


def _percentual(numerador: int, denominador: int) -> Decimal:
    return (Decimal(numerador) * 100 / Decimal(denominador)).quantize(
        SEIS_CASAS, rounding=ROUND_HALF_UP
    )


def resumir_pontos(
    pontos: tuple[PontoBacktest, ...],
) -> ResumoBacktest:
    if not pontos:
        raise ValueError("O relatório exige ao menos um concurso avaliado.")
    classes = {classe: 0 for classe in range(7)}
    for ponto in pontos:
        if not 0 <= ponto.quantidade_acertos <= 6:
            raise ValueError("A quantidade de acertos deve ficar entre 0 e 6.")
        classes[ponto.quantidade_acertos] += 1
    quantidade = len(pontos)
    quantidades_dezenas = [ponto.quantidade_dezenas for ponto in pontos]
    total_acertos = sum(ponto.quantidade_acertos for ponto in pontos)
    premiados = sum(classes[classe] for classe in (4, 5, 6))
    return ResumoBacktest(
        testes_efetuados=quantidade,
        classes=tuple(
            ClasseBacktest(
                classe, classes[classe], _percentual(classes[classe], quantidade)
            )
            for classe in range(7)
        ),
        minimo_dezenas=min(quantidades_dezenas),
        maximo_dezenas=max(quantidades_dezenas),
        media_dezenas=_dividir(sum(quantidades_dezenas), quantidade),
        media_acertos=_dividir(total_acertos, quantidade),
        concursos_premiados=premiados,
        percentual_premiados=_percentual(premiados, quantidade),
    )


def executar_backtest(
    conexao: psycopg.Connection,
    id_configuracao_selecao: int,
    *,
    concurso_inicial: int = 500,
    concurso_final: int,
    cancelamento_solicitado: Callable[[], bool] | None = None,
    informar_progresso: Callable[[int, int], None] | None = None,
) -> RelatorioBacktest:
    """Calcula e devolve o relatório em uma transação somente de leitura."""

    if not isinstance(conexao, psycopg.Connection):
        raise TypeError("conexao deve ser Psycopg Connection.")
    inicio = monotonic()
    try:
        with conexao.transaction():
            with conexao.cursor() as cursor:
                cursor.execute("SET TRANSACTION READ ONLY")
            configuracao_persistida = RepositorioPesquisaSelecao(
                conexao
            ).buscar_configuracao_disponivel(id_configuracao_selecao)
            fonte = RepositorioFonteBacktest(conexao)
            fonte.validar_periodo(concurso_inicial, concurso_final)
            resultados = iter(
                fonte.iterar_resultados_alvo(concurso_inicial, concurso_final)
            )
            total = concurso_final - concurso_inicial + 1
            pontos: list[PontoBacktest] = []
            for indice, fotografia in enumerate(
                fonte.iterar_fotografias(concurso_inicial, concurso_final),
                start=1,
            ):
                if cancelamento_solicitado is not None and cancelamento_solicitado():
                    raise ErroBacktest(
                        "BACKTEST_CANCELADO", "O backtest foi cancelado pelo usuário."
                    )
                alvo = fotografia.numero_concurso_corte + 1
                selecao = selecionar_dezenas_para_alvo(
                    fotografia.estatisticas,
                    configuracao_persistida.configuracao,
                    numero_concurso_alvo=alvo,
                    numero_concurso_corte=fotografia.numero_concurso_corte,
                )
                if not selecao.avaliavel:
                    raise ErroBacktest(
                        "ALVO_NAO_AVALIAVEL",
                        f"O concurso {alvo} não possui base estatística avaliável.",
                    )
                try:
                    resultado = next(resultados)
                except StopIteration as erro:
                    raise ErroBacktest(
                        "RESULTADO_ALVO_AUSENTE",
                        f"O resultado do concurso {alvo} não está disponível.",
                    ) from erro
                if resultado.numero_concurso != alvo:
                    raise ErroBacktest(
                        "RESULTADO_FORA_DE_ORDEM",
                        "Os resultados do período não estão na ordem esperada.",
                    )
                quantidade_acertos = len(
                    set(selecao.dezenas_retornadas) & resultado.dezenas
                )
                pontos.append(
                    PontoBacktest(
                        concurso=alvo,
                        quantidade_dezenas=len(selecao.dezenas_retornadas),
                        quantidade_acertos=quantidade_acertos,
                    )
                )
                if informar_progresso is not None:
                    informar_progresso(indice, total)
            if len(pontos) != total:
                raise ErroBacktest(
                    "PERIODO_INCOMPLETO",
                    "O relatório não recebeu todos os concursos solicitados.",
                )
            try:
                next(resultados)
            except StopIteration:
                pass
            else:
                raise ErroBacktest(
                    "RESULTADOS_EXCEDENTES",
                    "O período retornou mais resultados que o solicitado.",
                )
    except ErroBacktest:
        raise
    except ErroFonteBacktest as erro:
        raise ErroBacktest(erro.codigo, str(erro)) from erro

    pontos_finais = tuple(pontos)
    duracao = Decimal(str(monotonic() - inicio)).quantize(SEIS_CASAS)
    return RelatorioBacktest(
        id_configuracao_selecao=id_configuracao_selecao,
        concurso_inicial=concurso_inicial,
        concurso_final=concurso_final,
        pontos=pontos_finais,
        resumo=resumir_pontos(pontos_finais),
        duracao_segundos=duracao,
    )
