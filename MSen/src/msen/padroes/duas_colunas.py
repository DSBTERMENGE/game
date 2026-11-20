"""Detector do padrão geral de dezenas em exatamente duas colunas."""

from collections.abc import Iterable

from msen.modelos import ResultadoEntrada

from .estatisticas import EstatisticaPadrao, calcular_estatistica_padrao
from .entrada import validar_dezenas


CODIGO_DEZENAS_EM_DUAS_COLUNAS = "PD_012"


def detectar_dezenas_em_duas_colunas(
    dezenas: tuple[int, ...],
) -> bool:
    """Indica se as seis dezenas ocupam exatamente duas colunas do volante."""

    ordenadas = validar_dezenas(dezenas)
    colunas = {(dezena - 1) % 10 + 1 for dezena in ordenadas}
    return len(colunas) == 2


def calcular_estatistica_duas_colunas(
    resultados: Iterable[ResultadoEntrada],
) -> EstatisticaPadrao:
    """Calcula a incidência histórica do padrão PD_012."""

    return calcular_estatistica_padrao(
        CODIGO_DEZENAS_EM_DUAS_COLUNAS,
        detectar_dezenas_em_duas_colunas,
        resultados,
    )
