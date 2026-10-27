"""Registro e análise dos padrões sequenciais inicialmente aprovados."""

from collections.abc import Iterable

from msen.modelos import ResultadoEntrada

from .estatisticas import EstatisticaPadrao, calcular_estatistica_padrao
from .registro import RegistroDetectores
from .sequenciais import (
    detectar_duas_dezenas_sequenciais,
    detectar_mais_de_tres_dezenas_sequenciais,
    detectar_tres_dezenas_sequenciais,
)


CODIGO_DUAS_SEQUENCIAIS = "PD_001"
CODIGO_TRES_SEQUENCIAIS = "PD_002"
CODIGO_MAIS_DE_TRES_SEQUENCIAIS = "PD_003"


def criar_registro_detectores_iniciais() -> RegistroDetectores:
    """Cria um registro novo com os três detectores sequenciais aprovados.

    Retorno:
        Registro independente contendo `PD_001`, `PD_002` e `PD_003`.

    Regra:
        Uma nova instância é criada a cada chamada para evitar estado global
        mutável e substituições acidentais entre testes ou operações.
    """

    registro = RegistroDetectores()
    registro.registrar(CODIGO_DUAS_SEQUENCIAIS, detectar_duas_dezenas_sequenciais)
    registro.registrar(CODIGO_TRES_SEQUENCIAIS, detectar_tres_dezenas_sequenciais)
    registro.registrar(
        CODIGO_MAIS_DE_TRES_SEQUENCIAIS,
        detectar_mais_de_tres_dezenas_sequenciais,
    )
    return registro


def calcular_estatisticas_sequenciais(
    resultados: Iterable[ResultadoEntrada],
) -> tuple[EstatisticaPadrao, ...]:
    """Calcula em conjunto as estatísticas dos três padrões sequenciais.

    Parâmetros:
        resultados: Série histórica de resultados validados.

    Retorno:
        Três resumos ordenados por `PD_001`, `PD_002` e `PD_003`.

    Regra:
        A série é materializada uma vez para poder ser analisada pelos três
        detectores sem consumir novamente um iterador recebido.
    """

    serie = tuple(resultados)
    registro = criar_registro_detectores_iniciais()
    return tuple(
        calcular_estatistica_padrao(codigo, registro.obter(codigo), serie)
        for codigo in registro.codigos_registrados()
    )
