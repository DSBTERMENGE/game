"""Detector do padrão geral de dezenas em exatamente duas linhas."""

from collections.abc import Iterable

from msen.modelos import ResultadoEntrada

from .estatisticas import EstatisticaPadrao, calcular_estatistica_padrao
from .entrada import validar_dezenas


CODIGO_DEZENAS_EM_DUAS_LINHAS = "PD_011"


def detectar_dezenas_em_duas_linhas(
    dezenas: tuple[int, ...],
) -> bool:
    """Indica se as seis dezenas ocupam exatamente duas linhas do volante."""

    ordenadas = validar_dezenas(dezenas)
    linhas = {((dezena - 1) // 10) + 1 for dezena in ordenadas}
    return len(linhas) == 2


def calcular_estatistica_duas_linhas(
    resultados: Iterable[ResultadoEntrada],
) -> EstatisticaPadrao:
    """Calcula a incidência histórica do padrão PD_011."""

    return calcular_estatistica_padrao(
        CODIGO_DEZENAS_EM_DUAS_LINHAS,
        detectar_dezenas_em_duas_linhas,
        resultados,
    )
