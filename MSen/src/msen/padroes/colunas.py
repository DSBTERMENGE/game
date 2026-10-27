"""Registro e análise dos padrões aprovados de dezenas na mesma coluna."""

from collections.abc import Iterable

from msen.modelos import ResultadoEntrada

from .estatisticas import EstatisticaPadrao, calcular_estatistica_padrao
from .mesma_coluna import (
    detectar_duas_dezenas_na_mesma_coluna,
    detectar_mais_de_tres_dezenas_na_mesma_coluna,
    detectar_tres_dezenas_na_mesma_coluna,
)
from .registro import RegistroDetectores


CODIGO_DUAS_NA_MESMA_COLUNA = "PD_004"
CODIGO_TRES_NA_MESMA_COLUNA = "PD_005"
CODIGO_MAIS_DE_TRES_NA_MESMA_COLUNA = "PD_006"


def criar_registro_detectores_mesma_coluna() -> RegistroDetectores:
    """Cria um registro novo com os três detectores de mesma coluna.

    Retorno:
        Registro independente contendo `PD_004`, `PD_005` e `PD_006`.

    Regra:
        Cada chamada cria uma instância sem estado global compartilhado. Os
        códigos são associados às funções, nunca aos nomes editáveis do banco.
    """

    registro = RegistroDetectores()
    registro.registrar(
        CODIGO_DUAS_NA_MESMA_COLUNA,
        detectar_duas_dezenas_na_mesma_coluna,
    )
    registro.registrar(
        CODIGO_TRES_NA_MESMA_COLUNA,
        detectar_tres_dezenas_na_mesma_coluna,
    )
    registro.registrar(
        CODIGO_MAIS_DE_TRES_NA_MESMA_COLUNA,
        detectar_mais_de_tres_dezenas_na_mesma_coluna,
    )
    return registro


def calcular_estatisticas_mesma_coluna(
    resultados: Iterable[ResultadoEntrada],
) -> tuple[EstatisticaPadrao, ...]:
    """Calcula as estatísticas dos três padrões de mesma coluna em memória.

    Parâmetros:
        resultados: Série histórica de resultados validados.

    Retorno:
        Três resumos ordenados por `PD_004`, `PD_005` e `PD_006`.

    Regra:
        A série é materializada uma vez e cada resultado pode ocorrer em apenas
        um dos três padrões, conforme a maior sequência vertical em linhas
        subjacentes.
    """

    serie = tuple(resultados)
    registro = criar_registro_detectores_mesma_coluna()
    return tuple(
        calcular_estatistica_padrao(codigo, registro.obter(codigo), serie)
        for codigo in registro.codigos_registrados()
    )
