"""Geração em memória de combinações positivas para um único filtro."""

from collections.abc import Callable
from dataclasses import dataclass
from random import SystemRandom

import psycopg

from msen.validacao import chave_canonica

from .executor_filtros_validacao_nova import (
    Combinacao,
    ExecutorFiltroValidacao,
    carregar_executor_filtro_validacao,
)


GeradorCombinacao = Callable[[], Combinacao]
_ALEATORIO = SystemRandom()


class ErroTesteDirigidoValidacaoNova(RuntimeError):
    def __init__(self, codigo: str, mensagem: str) -> None:
        super().__init__(mensagem)
        self.codigo = codigo


@dataclass(frozen=True, slots=True)
class ColecaoDirigidaValidacaoNova:
    id_filtro: int
    quantidade: int
    tentativas: int
    combinacoes: tuple[Combinacao, ...]


def _gerador_aleatorio() -> Combinacao:
    return tuple(_ALEATORIO.sample(range(1, 61), 6))  # type: ignore[return-value]


def gerar_colecao_dirigida_validacao_nova(
    id_filtro: int,
    executor: ExecutorFiltroValidacao,
    *,
    quantidade: int = 10,
    maximo_tentativas: int = 500_000,
    gerar_combinacao: GeradorCombinacao = _gerador_aleatorio,
) -> ColecaoDirigidaValidacaoNova:
    """Mantém somente combinações únicas que o detector selecionado reconhece."""

    if isinstance(id_filtro, bool) or not isinstance(id_filtro, int) or id_filtro <= 0:
        raise ValueError("id_filtro deve ser um inteiro positivo.")
    if not callable(executor) or not callable(gerar_combinacao):
        raise TypeError("Executor e gerador de combinações devem ser chamáveis.")
    if isinstance(quantidade, bool) or not isinstance(quantidade, int) or quantidade < 1:
        raise ValueError("quantidade deve ser um inteiro positivo.")
    if (
        isinstance(maximo_tentativas, bool)
        or not isinstance(maximo_tentativas, int)
        or maximo_tentativas < quantidade
    ):
        raise ValueError("maximo_tentativas deve comportar a quantidade solicitada.")

    aceitas: list[Combinacao] = []
    chaves: set[tuple[int, ...]] = set()
    for tentativa in range(1, maximo_tentativas + 1):
        combinacao = tuple(gerar_combinacao())
        try:
            chave = chave_canonica(combinacao)
        except (TypeError, ValueError) as erro:
            raise ErroTesteDirigidoValidacaoNova(
                "COMBINACAO_GERADA_INVALIDA",
                "O gerador produziu uma combinação inválida.",
            ) from erro
        if chave in chaves or not executor(combinacao):
            continue
        chaves.add(chave)
        aceitas.append(combinacao)  # type: ignore[arg-type]
        if len(aceitas) == quantidade:
            return ColecaoDirigidaValidacaoNova(
                id_filtro=id_filtro,
                quantidade=quantidade,
                tentativas=tentativa,
                combinacoes=tuple(aceitas),
            )

    raise ErroTesteDirigidoValidacaoNova(
        "OCORRENCIAS_INSUFICIENTES",
        "Não foi possível formar as 10 combinações positivas dentro do limite de tentativas.",
    )


def gerar_colecao_dirigida_no_banco(
    conexao: psycopg.Connection,
    id_filtro: int,
    *,
    fotografia_diagonal=None,
) -> ColecaoDirigidaValidacaoNova:
    """Carrega um único detector pelo ID e gera sua coleção positiva em memória."""

    if not isinstance(conexao, psycopg.Connection):
        raise TypeError("O teste dirigido exige uma conexão Psycopg válida.")
    executor = carregar_executor_filtro_validacao(
        conexao,
        id_filtro,
        fotografia_diagonal=fotografia_diagonal,
    )
    return gerar_colecao_dirigida_validacao_nova(id_filtro, executor)
