"""Seleção segura da amostra histórica para perfis e futuros backtests."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date, datetime
from typing import TypeAlias

from msen.calculos import ResultadoCalculado
from msen.modelos import ResultadoEntrada


ResultadoHistorico: TypeAlias = ResultadoEntrada | ResultadoCalculado


class ErroJanelaHistorica(ValueError):
    """Informa uma inconsistência previsível na seleção histórica."""

    def __init__(self, codigo: str, mensagem: str) -> None:
        super().__init__(mensagem)
        self.codigo = codigo


@dataclass(frozen=True, slots=True)
class JanelaHistorica:
    """Resultado imutável de uma seleção histórica exclusiva."""

    resultados: tuple[ResultadoHistorico, ...]
    total_disponivel: int
    numero_ap_antes_de: int | None
    data_antes_de: date | None

    @property
    def quantidade(self) -> int:
        """Retorna o tamanho efetivo da amostra selecionada."""

        return len(self.resultados)

    @property
    def primeiro_numero_ap(self) -> int | None:
        """Retorna o primeiro concurso da janela ou nulo quando vazia."""

        return None if not self.resultados else self.resultados[0].numero_ap

    @property
    def ultimo_numero_ap(self) -> int | None:
        """Retorna o último concurso da janela ou nulo quando vazia."""

        return None if not self.resultados else self.resultados[-1].numero_ap


def _validar_cortes(
    numero_ap_antes_de: int | None,
    data_antes_de: date | None,
) -> None:
    if numero_ap_antes_de is not None and (
        isinstance(numero_ap_antes_de, bool)
        or not isinstance(numero_ap_antes_de, int)
        or numero_ap_antes_de < 1
    ):
        raise ErroJanelaHistorica(
            "CONCURSO_INVALIDO",
            "O concurso de corte deve ser um inteiro positivo.",
        )
    if data_antes_de is not None and (
        isinstance(data_antes_de, datetime) or not isinstance(data_antes_de, date)
    ):
        raise ErroJanelaHistorica(
            "DATA_INVALIDA",
            "A data de corte deve ser date e não pode conter horário.",
        )
    if numero_ap_antes_de is not None and data_antes_de is not None:
        raise ErroJanelaHistorica(
            "CORTES_CONFLITANTES",
            "Informe concurso ou data de corte, não ambos.",
        )


def _ordenar_e_validar(
    resultados: Iterable[ResultadoHistorico],
) -> tuple[ResultadoHistorico, ...]:
    try:
        serie = tuple(resultados)
    except TypeError as erro:
        raise TypeError("Os resultados históricos devem ser iteráveis.") from erro
    if any(not isinstance(item, (ResultadoEntrada, ResultadoCalculado)) for item in serie):
        raise TypeError(
            "A janela aceita somente ResultadoEntrada ou ResultadoCalculado."
        )

    ordenados = tuple(sorted(serie, key=lambda item: item.numero_ap))
    for anterior, atual in zip(ordenados, ordenados[1:]):
        if anterior.numero_ap == atual.numero_ap:
            raise ErroJanelaHistorica(
                "CONCURSO_DUPLICADO",
                f"O concurso {atual.numero_ap} aparece mais de uma vez.",
            )
        if anterior.data_resultado > atual.data_resultado:
            raise ErroJanelaHistorica(
                "ORDEM_HISTORICA_DIVERGENTE",
                "A ordem das datas diverge da ordem dos concursos.",
            )
    return ordenados


def selecionar_janela_historica(
    resultados: Iterable[ResultadoHistorico],
    *,
    numero_ap_antes_de: int | None = None,
    data_antes_de: date | None = None,
) -> JanelaHistorica:
    """Seleciona a amostra completa ou somente registros anteriores ao corte.

    Sem corte, devolve toda a série validada e ordenada. Com corte, a comparação
    é estrita: ao avaliar um concurso ou uma data, o próprio resultado e tudo o
    que vier depois ficam fora da amostra. Concurso e data são alternativas para
    que não existam duas interpretações concorrentes do mesmo corte.
    """

    _validar_cortes(numero_ap_antes_de, data_antes_de)
    ordenados = _ordenar_e_validar(resultados)
    selecionados = tuple(
        item
        for item in ordenados
        if (numero_ap_antes_de is None or item.numero_ap < numero_ap_antes_de)
        and (data_antes_de is None or item.data_resultado < data_antes_de)
    )
    return JanelaHistorica(
        resultados=selecionados,
        total_disponivel=len(ordenados),
        numero_ap_antes_de=numero_ap_antes_de,
        data_antes_de=data_antes_de,
    )
