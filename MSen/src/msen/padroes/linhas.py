"""Registro e análise dos padrões aprovados de dezenas na mesma linha."""

from collections.abc import Iterable

from msen.modelos import ResultadoEntrada

from .estatisticas import EstatisticaPadrao, calcular_estatistica_padrao
from .mesma_linha import (
    detectar_duas_dezenas_na_mesma_linha,
    detectar_mais_de_tres_dezenas_na_mesma_linha,
    detectar_tres_dezenas_na_mesma_linha,
)
from .registro import RegistroDetectores


CODIGO_DUAS_NA_MESMA_LINHA = "PD_007"
CODIGO_TRES_NA_MESMA_LINHA = "PD_008"
CODIGO_MAIS_DE_TRES_NA_MESMA_LINHA = "PD_009"


def criar_registro_detectores_mesma_linha() -> RegistroDetectores:
    """Cria um registro novo com os três detectores de mesma linha.

    Retorno:
        Registro independente contendo `PD_007`, `PD_008` e `PD_009`.

    Regra:
        Cada chamada cria uma instância sem estado global compartilhado. Os
        códigos são associados às funções, nunca aos nomes editáveis do banco.
    """

    registro = RegistroDetectores()
    registro.registrar(
        CODIGO_DUAS_NA_MESMA_LINHA,
        detectar_duas_dezenas_na_mesma_linha,
    )
    registro.registrar(
        CODIGO_TRES_NA_MESMA_LINHA,
        detectar_tres_dezenas_na_mesma_linha,
    )
    registro.registrar(
        CODIGO_MAIS_DE_TRES_NA_MESMA_LINHA,
        detectar_mais_de_tres_dezenas_na_mesma_linha,
    )
    return registro


def calcular_estatisticas_mesma_linha(
    resultados: Iterable[ResultadoEntrada],
) -> tuple[EstatisticaPadrao, ...]:
    """Calcula as estatísticas dos três padrões de mesma linha em memória.

    Parâmetros:
        resultados: Série histórica de resultados validados.

    Retorno:
        Três resumos ordenados por `PD_007`, `PD_008` e `PD_009`.

    Regra:
        A série é materializada uma vez e cada resultado pode ocorrer em apenas
        um dos três padrões, conforme a maior ocupação de linha.
    """

    serie = tuple(resultados)
    registro = criar_registro_detectores_mesma_linha()
    return tuple(
        calcular_estatistica_padrao(codigo, registro.obter(codigo), serie)
        for codigo in registro.codigos_registrados()
    )
