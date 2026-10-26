"""Modelo e validações dos dados originais de um resultado."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from datetime import date, datetime
from typing import Any


class ErroValidacaoResultado(ValueError):
    """Erro previsível encontrado ao validar uma linha de resultado."""

    def __init__(
        self,
        codigo: str,
        mensagem: str,
        *,
        campo: str | None = None,
        valor: Any = None,
    ) -> None:
        super().__init__(mensagem)
        self.codigo = codigo
        self.campo = campo
        self.valor = valor


def _normalizar_data(valor: date | str | None) -> date:
    """Converte a data aceita pelo contrato para ``datetime.date``."""

    if valor is None or (isinstance(valor, str) and not valor.strip()):
        raise ErroValidacaoResultado(
            "DATA_AUSENTE",
            "A data do resultado é obrigatória.",
            campo="data_resultado",
            valor=valor,
        )

    if isinstance(valor, datetime):
        raise ErroValidacaoResultado(
            "DATA_INVALIDA",
            "A data não pode conter horário.",
            campo="data_resultado",
            valor=valor,
        )

    if isinstance(valor, date):
        return valor

    if not isinstance(valor, str):
        raise ErroValidacaoResultado(
            "DATA_INVALIDA",
            "A data deve usar o formato DD/MM/AAAA.",
            campo="data_resultado",
            valor=valor,
        )

    try:
        return datetime.strptime(valor.strip(), "%d/%m/%Y").date()
    except ValueError as erro:
        raise ErroValidacaoResultado(
            "DATA_INVALIDA",
            "A data deve ser real e usar o formato DD/MM/AAAA.",
            campo="data_resultado",
            valor=valor,
        ) from erro


def _validar_numero_ap(valor: object) -> int:
    """Valida o número funcional da apresentação/concurso."""

    if valor is None:
        raise ErroValidacaoResultado(
            "NUMERO_AP_AUSENTE",
            "O número da apresentação é obrigatório.",
            campo="numero_ap",
            valor=valor,
        )

    if isinstance(valor, bool) or not isinstance(valor, int) or valor < 1:
        raise ErroValidacaoResultado(
            "NUMERO_AP_INVALIDO",
            "O número da apresentação deve ser um inteiro maior que zero.",
            campo="numero_ap",
            valor=valor,
        )

    return valor


def _validar_resultados(valores: Sequence[object] | None) -> tuple[int, ...]:
    """Valida quantidade, tipo, intervalo e unicidade dos seis resultados."""

    if (
        valores is None
        or isinstance(valores, (str, bytes))
        or not isinstance(valores, Sequence)
        or len(valores) != 6
    ):
        raise ErroValidacaoResultado(
            "QUANTIDADE_RESULTADOS_INVALIDA",
            "Devem ser informados exatamente seis resultados.",
            campo="resultados",
            valor=valores,
        )

    resultados: list[int] = []
    for indice, valor in enumerate(valores, start=1):
        campo = f"res_{indice:02d}"

        if valor is None:
            raise ErroValidacaoResultado(
                "RESULTADO_AUSENTE",
                f"O campo {campo} é obrigatório.",
                campo=campo,
                valor=valor,
            )

        if isinstance(valor, bool) or not isinstance(valor, int):
            raise ErroValidacaoResultado(
                "RESULTADO_NAO_INTEIRO",
                f"O campo {campo} deve ser um número inteiro.",
                campo=campo,
                valor=valor,
            )

        if not 1 <= valor <= 60:
            raise ErroValidacaoResultado(
                "RESULTADO_FORA_INTERVALO",
                f"O campo {campo} deve estar entre 1 e 60.",
                campo=campo,
                valor=valor,
            )

        resultados.append(valor)

    if len(set(resultados)) != 6:
        repetidos = sorted(
            numero for numero in set(resultados) if resultados.count(numero) > 1
        )
        raise ErroValidacaoResultado(
            "RESULTADO_REPETIDO",
            "Os seis resultados devem ser diferentes.",
            campo="resultados",
            valor=tuple(repetidos),
        )

    return tuple(resultados)


@dataclass(frozen=True, slots=True)
class ResultadoEntrada:
    """Linha original validada, ainda sem os campos matemáticos derivados."""

    data_resultado: date
    numero_ap: int
    res_01: int
    res_02: int
    res_03: int
    res_04: int
    res_05: int
    res_06: int

    def __post_init__(self) -> None:
        if isinstance(self.data_resultado, datetime) or not isinstance(
            self.data_resultado, date
        ):
            raise ErroValidacaoResultado(
                "DATA_INVALIDA",
                "A data interna deve ser do tipo date e não pode conter horário.",
                campo="data_resultado",
                valor=self.data_resultado,
            )

        _validar_numero_ap(self.numero_ap)
        _validar_resultados(self.resultados)

    @property
    def resultados(self) -> tuple[int, int, int, int, int, int]:
        """Retorna os seis valores preservando a ordem da fonte."""

        return (
            self.res_01,
            self.res_02,
            self.res_03,
            self.res_04,
            self.res_05,
            self.res_06,
        )

    @classmethod
    def criar(
        cls,
        *,
        data_resultado: date | str | None,
        numero_ap: object,
        resultados: Sequence[object] | None,
    ) -> ResultadoEntrada:
        """Normaliza e valida uma entrada vinda de qualquer interface."""

        data_normalizada = _normalizar_data(data_resultado)
        numero_normalizado = _validar_numero_ap(numero_ap)
        resultados_normalizados = _validar_resultados(resultados)

        return cls(
            data_resultado=data_normalizada,
            numero_ap=numero_normalizado,
            res_01=resultados_normalizados[0],
            res_02=resultados_normalizados[1],
            res_03=resultados_normalizados[2],
            res_04=resultados_normalizados[3],
            res_05=resultados_normalizados[4],
            res_06=resultados_normalizados[5],
        )
