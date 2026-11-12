"""Geração controlada e sem persistência das combinações de uma seleção."""

from __future__ import annotations

from collections.abc import Callable, Iterable
from dataclasses import dataclass
from time import monotonic
from typing import Literal, Protocol

from .combinacoes_selecao_dezenas import (
    calcular_previa_combinacoes,
    gerar_combinacoes_seis_dezenas,
)


Combinacao = tuple[int, int, int, int, int, int]
EstadoGeracao = Literal["CONCLUIDA", "CANCELADA"]


class AdaptadorCombinacao(Protocol):
    def __call__(self, combinacao: Combinacao) -> object:
        """Recebe uma combinação uma única vez, sem exigir materialização."""


class ErroMotorFormacaoJogos(RuntimeError):
    def __init__(self, codigo: str, mensagem: str) -> None:
        super().__init__(mensagem)
        self.codigo = codigo


@dataclass(frozen=True, slots=True)
class RelatorioGeracaoControlada:
    estado: EstadoGeracao
    quantidade_dezenas: int
    quantidade_combinacoes: int
    quantidade_encaminhada: int
    duracao_segundos: float

    @property
    def percentual_concluido(self) -> float:
        if self.quantidade_combinacoes == 0:
            return 100.0
        return round(
            self.quantidade_encaminhada * 100 / self.quantidade_combinacoes, 2
        )


def executar_geracao_controlada(
    dezenas: Iterable[int],
    adaptador_screener: AdaptadorCombinacao,
    *,
    informar_progresso: Callable[[int, int], None] | None = None,
    cancelamento_solicitado: Callable[[], bool] | None = None,
    intervalo_progresso: int = 1_000,
    relogio: Callable[[], float] = monotonic,
) -> RelatorioGeracaoControlada:
    """Encaminha combinações em fluxo e para com segurança quando solicitado.

    O motor não acumula combinações, não executa filtros por conta própria e
    não grava dados. O adaptador é o único consumidor de cada item produzido.
    """

    if not callable(adaptador_screener):
        raise TypeError("adaptador_screener deve ser chamável.")
    if informar_progresso is not None and not callable(informar_progresso):
        raise TypeError("informar_progresso deve ser chamável.")
    if cancelamento_solicitado is not None and not callable(cancelamento_solicitado):
        raise TypeError("cancelamento_solicitado deve ser chamável.")
    if (
        isinstance(intervalo_progresso, bool)
        or not isinstance(intervalo_progresso, int)
        or intervalo_progresso < 1
    ):
        raise ValueError("intervalo_progresso deve ser um inteiro positivo.")
    if not callable(relogio):
        raise TypeError("relogio deve ser chamável.")

    dezenas_fixas = tuple(dezenas)
    previa = calcular_previa_combinacoes(dezenas_fixas)
    if previa.quantidade_combinacoes == 0:
        raise ErroMotorFormacaoJogos(
            "DEZENAS_INSUFICIENTES",
            "São necessárias ao menos seis dezenas para iniciar a geração.",
        )

    progresso = informar_progresso or (lambda _concluidas, _total: None)
    cancelar = cancelamento_solicitado or (lambda: False)
    total = previa.quantidade_combinacoes
    encaminhadas = 0
    inicio = relogio()
    progresso(0, total)

    for combinacao in gerar_combinacoes_seis_dezenas(dezenas_fixas):
        if cancelar():
            progresso(encaminhadas, total)
            return RelatorioGeracaoControlada(
                "CANCELADA", len(dezenas_fixas), total, encaminhadas,
                round(relogio() - inicio, 6),
            )
        try:
            adaptador_screener(combinacao)
        except Exception as erro:
            raise ErroMotorFormacaoJogos(
                "FALHA_ADAPTADOR_SCREENER",
                f"O adaptador falhou depois de {encaminhadas} combinações concluídas.",
            ) from erro
        encaminhadas += 1
        if encaminhadas % intervalo_progresso == 0:
            progresso(encaminhadas, total)

    progresso(encaminhadas, total)
    return RelatorioGeracaoControlada(
        "CONCLUIDA", len(dezenas_fixas), total, encaminhadas,
        round(relogio() - inicio, 6),
    )
