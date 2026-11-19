"""Associação por ID entre filtros cadastrados e funções executáveis."""

from collections.abc import Callable
from decimal import Decimal

import psycopg

from msen.padroes import (
    ErroResolucaoDetector,
    FotografiaHistoricaDiagonal,
    calcular_categorias_diagonais,
    resolver_funcao_detectora,
)
from msen.screener import avaliar_filtro_diagonal


Combinacao = tuple[int, int, int, int, int, int]
ExecutorFiltroValidacao = Callable[[Combinacao], bool]


class ErroExecutorFiltroValidacao(RuntimeError):
    def __init__(self, codigo: str, mensagem: str) -> None:
        super().__init__(mensagem)
        self.codigo = codigo


def criar_executor_filtro_validacao(
    funcao: Callable,
    *,
    fotografia_diagonal: FotografiaHistoricaDiagonal | None = None,
    limite_diagonal: Decimal | int | float | str = "10",
) -> ExecutorFiltroValidacao:
    """Uniformiza detectores booleanos e o classificador diagonal em booleano."""

    if not callable(funcao):
        raise TypeError("A função do filtro deve ser chamável.")
    if funcao is calcular_categorias_diagonais:
        if not isinstance(fotografia_diagonal, FotografiaHistoricaDiagonal):
            raise ErroExecutorFiltroValidacao(
                "FOTOGRAFIA_DIAGONAL_AUSENTE",
                "O filtro diagonal exige sua fotografia histórica aprovada.",
            )

        def executar_diagonal(combinacao: Combinacao) -> bool:
            decisao = avaliar_filtro_diagonal(
                combinacao,
                fotografia_diagonal,
                limite_diagonal,
                calcular_categorias_diagonais,
            )
            return not decisao.aprovada

        return executar_diagonal

    def executar_booleano(combinacao: Combinacao) -> bool:
        resultado = funcao(combinacao)
        if not isinstance(resultado, bool):
            raise ErroExecutorFiltroValidacao(
                "RETORNO_INVALIDO",
                "A função detectora deve devolver True ou False.",
            )
        return resultado

    return executar_booleano


def carregar_executor_filtro_validacao(
    conexao: psycopg.Connection,
    id_filtro: int,
    *,
    fotografia_diagonal: FotografiaHistoricaDiagonal | None = None,
    limite_diagonal: Decimal | int | float | str = "10",
) -> ExecutorFiltroValidacao:
    """Localiza pelo ID interno e devolve um executor booleano uniforme."""

    if not isinstance(conexao, psycopg.Connection):
        raise TypeError("O executor exige uma conexão Psycopg válida.")
    if isinstance(id_filtro, bool) or not isinstance(id_filtro, int) or id_filtro <= 0:
        raise ValueError("id_filtro deve ser um inteiro positivo.")
    with conexao.transaction(), conexao.cursor() as cursor:
        cursor.execute(
            "SELECT funcao_detectora FROM padroes_subgrupo WHERE id_padrao=%s",
            (id_filtro,),
        )
        linha = cursor.fetchone()
    if linha is None:
        raise ErroExecutorFiltroValidacao(
            "FILTRO_NAO_ENCONTRADO", "O filtro selecionado não foi encontrado."
        )
    try:
        funcao = resolver_funcao_detectora(linha[0])
    except ErroResolucaoDetector as erro:
        raise ErroExecutorFiltroValidacao(
            "FUNCAO_INDISPONIVEL",
            "O filtro selecionado ainda não possui função disponível.",
        ) from erro
    return criar_executor_filtro_validacao(
        funcao,
        fotografia_diagonal=fotografia_diagonal,
        limite_diagonal=limite_diagonal,
    )
