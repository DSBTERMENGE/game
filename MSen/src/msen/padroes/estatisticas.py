"""Estatísticas históricas calculadas a partir de detectores de padrões."""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
from typing import Any

from msen.calculos import calcular_desvio_padrao_populacional
from msen.modelos import ResultadoEntrada

from .contratos import DetectorPadrao


SEIS_CASAS_DECIMAIS = Decimal("0.000001")


class ErroAnalisePadrao(ValueError):
    """Representa uma inconsistência previsível na série histórica de padrões."""

    def __init__(self, codigo: str, mensagem: str, *, valor: Any = None) -> None:
        """Cria o erro com código estável, mensagem segura e valor relacionado."""

        super().__init__(mensagem)
        self.codigo = codigo
        self.valor = valor


@dataclass(frozen=True, slots=True)
class EstatisticaPadrao:
    """Reúne ocorrências, intervalos e resumo calculado de um padrão."""

    padrao_cod: str
    ocorrencias: tuple[int, ...]
    intervalos: tuple[int, ...]
    num_oco: int
    intervalo_medio: Decimal | None
    desv_padrao: Decimal | None


def _ordenar_e_validar_historico(
    resultados: Iterable[ResultadoEntrada],
) -> tuple[ResultadoEntrada, ...]:
    serie = tuple(resultados)
    if any(not isinstance(item, ResultadoEntrada) for item in serie):
        raise TypeError("A análise de padrões aceita somente ResultadoEntrada.")

    ordenados = tuple(sorted(serie, key=lambda item: item.numero_ap))
    for anterior, atual in zip(ordenados, ordenados[1:]):
        if anterior.numero_ap == atual.numero_ap:
            raise ErroAnalisePadrao(
                "NUMERO_AP_DUPLICADO",
                f"A apresentação {atual.numero_ap} aparece mais de uma vez.",
                valor=atual.numero_ap,
            )
        if anterior.data_resultado > atual.data_resultado:
            raise ErroAnalisePadrao(
                "ORDEM_HISTORICA_DIVERGENTE",
                "A ordem das datas diverge da ordem das apresentações.",
                valor=(anterior.numero_ap, atual.numero_ap),
            )
    return ordenados


def _media_intervalos(intervalos: Sequence[int]) -> Decimal:
    media = Decimal(sum(intervalos)) / Decimal(len(intervalos))
    return media.quantize(SEIS_CASAS_DECIMAIS, rounding=ROUND_HALF_UP)


def calcular_estatistica_padrao(
    padrao_cod: str,
    detector: DetectorPadrao,
    resultados: Iterable[ResultadoEntrada],
) -> EstatisticaPadrao:
    """Calcula ocorrências e intervalos históricos de um detector.

    Parâmetros:
        padrao_cod: Código estável associado ao detector.
        detector: Função pura que classifica as seis dezenas.
        resultados: Série histórica validada, em qualquer ordem de entrada.

    Retorno:
        Resumo imutável com concursos, intervalos, contagem, média e desvio.

    Regra:
        Cada concurso conta no máximo uma vez. Com menos de duas ocorrências não
        existe intervalo; média e desvio ficam nulos. O desvio é populacional.
    """

    if not isinstance(padrao_cod, str) or not padrao_cod:
        raise ValueError("O código do padrão é obrigatório.")
    if not callable(detector):
        raise TypeError("A estatística exige uma função detectora.")

    ordenados = _ordenar_e_validar_historico(resultados)
    ocorrencias: list[int] = []
    for resultado in ordenados:
        corresponde = detector(resultado.resultados)
        if not isinstance(corresponde, bool):
            raise TypeError("O detector deve devolver um valor booleano.")
        if corresponde:
            ocorrencias.append(resultado.numero_ap)

    ocorrencias_finais = tuple(ocorrencias)
    intervalos = tuple(
        atual - anterior
        for anterior, atual in zip(ocorrencias_finais, ocorrencias_finais[1:])
    )
    if intervalos:
        media = _media_intervalos(intervalos)
        desvio = calcular_desvio_padrao_populacional(intervalos)
    else:
        media = None
        desvio = None

    return EstatisticaPadrao(
        padrao_cod=padrao_cod,
        ocorrencias=ocorrencias_finais,
        intervalos=intervalos,
        num_oco=len(ocorrencias_finais),
        intervalo_medio=media,
        desv_padrao=desvio,
    )
