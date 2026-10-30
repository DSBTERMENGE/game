"""Frequências e estatísticas dos intervalos entre ocorrências."""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
from typing import Any

from msen.modelos import ResultadoEntrada

from .estatisticas_linha import calcular_desvio_padrao_populacional


SEIS_CASAS_DECIMAIS = Decimal("0.000001")


class ErroAnaliseHistorica(ValueError):
    """Erro previsível ao preparar uma série histórica."""

    def __init__(self, codigo: str, mensagem: str, *, valor: Any = None) -> None:
        super().__init__(mensagem)
        self.codigo = codigo
        self.valor = valor


@dataclass(frozen=True, slots=True)
class FrequenciaResultado:
    """Resumo imutável das ocorrências de uma dezena."""

    dezena: int
    ocorrencias: tuple[int, ...]
    intervalos: tuple[int, ...]
    prim_oco: int | None
    ult_oco: int | None
    num_oco: int
    qtd_intervalos: int
    intervalo_minimo: int | None
    intervalo_maximo: int | None
    media_oco: Decimal | None
    mediana_oco: Decimal | None
    desv_padrao_oco: Decimal | None


def _validar_limite_periodo(nome: str, valor: int | None) -> int | None:
    if valor is None:
        return None
    if isinstance(valor, bool) or not isinstance(valor, int) or valor < 1:
        raise ErroAnaliseHistorica(
            "PERIODO_INVALIDO",
            f"{nome} deve ser um inteiro maior que zero.",
            valor=valor,
        )
    return valor


def _ordenar_e_validar_historico(
    resultados: Iterable[ResultadoEntrada],
) -> tuple[ResultadoEntrada, ...]:
    serie = tuple(resultados)
    if any(not isinstance(item, ResultadoEntrada) for item in serie):
        raise TypeError("A série histórica aceita somente ResultadoEntrada.")

    ordenados = tuple(sorted(serie, key=lambda item: item.numero_ap))
    for anterior, atual in zip(ordenados, ordenados[1:]):
        if anterior.numero_ap == atual.numero_ap:
            raise ErroAnaliseHistorica(
                "NUMERO_AP_DUPLICADO",
                f"A apresentação {atual.numero_ap} aparece mais de uma vez.",
                valor=atual.numero_ap,
            )
        if anterior.data_resultado > atual.data_resultado:
            raise ErroAnaliseHistorica(
                "ORDEM_HISTORICA_DIVERGENTE",
                "A ordem das datas diverge da ordem das apresentações.",
                valor=(anterior.numero_ap, atual.numero_ap),
            )

    return ordenados


def _calcular_media(valores: Sequence[int]) -> Decimal:
    media_exata = Decimal(sum(valores)) / Decimal(len(valores))
    return media_exata.quantize(SEIS_CASAS_DECIMAIS, rounding=ROUND_HALF_UP)


def _calcular_mediana(valores: Sequence[int]) -> Decimal:
    ordenados = sorted(valores)
    meio = len(ordenados) // 2
    if len(ordenados) % 2:
        mediana_exata = Decimal(ordenados[meio])
    else:
        mediana_exata = (
            Decimal(ordenados[meio - 1]) + Decimal(ordenados[meio])
        ) / Decimal(2)
    return mediana_exata.quantize(SEIS_CASAS_DECIMAIS, rounding=ROUND_HALF_UP)


def _resumir_dezena(dezena: int, ocorrencias: Sequence[int]) -> FrequenciaResultado:
    ocorrencias_ordenadas = tuple(ocorrencias)
    intervalos = tuple(
        atual - anterior
        for anterior, atual in zip(ocorrencias_ordenadas, ocorrencias_ordenadas[1:])
    )

    if intervalos:
        media = _calcular_media(intervalos)
        mediana = _calcular_mediana(intervalos)
        desvio = calcular_desvio_padrao_populacional(intervalos)
    else:
        media = None
        mediana = None
        desvio = None

    return FrequenciaResultado(
        dezena=dezena,
        ocorrencias=ocorrencias_ordenadas,
        intervalos=intervalos,
        prim_oco=ocorrencias_ordenadas[0] if ocorrencias_ordenadas else None,
        ult_oco=ocorrencias_ordenadas[-1] if ocorrencias_ordenadas else None,
        num_oco=len(ocorrencias_ordenadas),
        qtd_intervalos=len(intervalos),
        intervalo_minimo=min(intervalos) if intervalos else None,
        intervalo_maximo=max(intervalos) if intervalos else None,
        media_oco=media,
        mediana_oco=mediana,
        desv_padrao_oco=desvio,
    )


def calcular_frequencias(
    resultados: Iterable[ResultadoEntrada],
    *,
    numero_ap_inicial: int | None = None,
    numero_ap_final: int | None = None,
) -> tuple[FrequenciaResultado, ...]:
    """Calcula os 60 resumos dentro de um período inclusivo opcional."""

    inicio = _validar_limite_periodo("numero_ap_inicial", numero_ap_inicial)
    fim = _validar_limite_periodo("numero_ap_final", numero_ap_final)
    if inicio is not None and fim is not None and inicio > fim:
        raise ErroAnaliseHistorica(
            "PERIODO_INVALIDO",
            "A apresentação inicial não pode ser posterior à final.",
            valor=(inicio, fim),
        )

    ordenados = _ordenar_e_validar_historico(resultados)
    ocorrencias: dict[int, list[int]] = {dezena: [] for dezena in range(1, 61)}

    for resultado in ordenados:
        if inicio is not None and resultado.numero_ap < inicio:
            continue
        if fim is not None and resultado.numero_ap > fim:
            continue
        for dezena in resultado.resultados:
            ocorrencias[dezena].append(resultado.numero_ap)

    return tuple(
        _resumir_dezena(dezena, ocorrencias[dezena]) for dezena in range(1, 61)
    )
