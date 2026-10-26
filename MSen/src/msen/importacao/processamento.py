"""Composição entre leitura de Excel e cálculos aprovados."""

from pathlib import Path

from msen.calculos import ResultadoCalculado, calcular_resultado

from .excel import ler_resultados_excel


def ler_resultados_calculados_excel(caminho: str | Path) -> tuple[ResultadoCalculado, ...]:
    """Lê, valida e calcula cada linha sem gravar arquivo ou banco de dados."""

    return tuple(calcular_resultado(resultado) for resultado in ler_resultados_excel(caminho))
