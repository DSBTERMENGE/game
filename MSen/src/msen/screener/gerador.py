"""Gera a amostra reproduzível usada nos ensaios iniciais do screener."""

from __future__ import annotations

from collections.abc import Iterator
from itertools import combinations, islice
from math import comb
from random import Random
from typing import TypeAlias

from .configuracao import ConfiguracaoScreener, LIMITE_EXPERIMENTAL


MENOR_DEZENA = 1
MAIOR_DEZENA = 60
QUANTIDADE_DEZENAS = 6
TOTAL_COMBINACOES = comb(MAIOR_DEZENA, QUANTIDADE_DEZENAS)
CONFIRMACAO_INTEGRAL = "PROCESSAR_50063860_COMBINACOES"

Combinacao: TypeAlias = tuple[int, int, int, int, int, int]


class ErroGeracaoAmostra(ValueError):
    """Indica que a configuração não permite gerar a amostra experimental."""

    def __init__(self, codigo: str, mensagem: str) -> None:
        super().__init__(mensagem)
        self.codigo = codigo


class ErroGeracaoIntegral(ValueError):
    """Indica que uma trava impediu a criação do iterador integral."""

    def __init__(self, codigo: str, mensagem: str) -> None:
        super().__init__(mensagem)
        self.codigo = codigo


def criar_iterador_combinacoes(
    configuracao: ConfiguracaoScreener, *, confirmacao_integral: str | None = None
) -> Iterator[Combinacao]:
    """Cria o iterador lexicográfico protegido das combinações de 01 a 60.

    No modo `amostra`, `islice` impõe o encerramento em 5.000 itens. No modo
    `integral`, a função exige as duas confirmações antes mesmo de devolver o
    iterador. O retorno é preguiçoso e sua criação não percorre o universo.
    """

    if not isinstance(configuracao, ConfiguracaoScreener):
        raise TypeError("configuracao deve ser uma ConfiguracaoScreener validada")
    if configuracao.limite_combinacoes != LIMITE_EXPERIMENTAL:
        raise ErroGeracaoIntegral(
            "LIMITE_NAO_AUTORIZADO", "O limite experimental deve permanecer em 5.000."
        )

    iterador = combinations(
        range(MENOR_DEZENA, MAIOR_DEZENA + 1), QUANTIDADE_DEZENAS
    )
    if configuracao.modo == "amostra":
        return islice(iterador, configuracao.limite_combinacoes)
    if configuracao.modo != "integral":
        raise ErroGeracaoIntegral("MODO_INVALIDO", "Modo de geração desconhecido.")
    if not configuracao.confirmacao_processamento_integral:
        raise ErroGeracaoIntegral(
            "CONFIGURACAO_INTEGRAL_NAO_CONFIRMADA",
            "A configuração não autoriza o processamento integral.",
        )
    if confirmacao_integral != CONFIRMACAO_INTEGRAL:
        raise ErroGeracaoIntegral(
            "CONFIRMACAO_INTEGRAL_AUSENTE",
            "A confirmação explícita do universo integral não foi fornecida.",
        )
    return iterador


def gerar_amostra(configuracao: ConfiguracaoScreener) -> tuple[Combinacao, ...]:
    """Gera 5.000 combinações distintas e ordenadas com a semente configurada.

    Um gerador pseudoaleatório isolado evita alterar o estado aleatório global.
    As repetições eventualmente sorteadas são descartadas até que o limite
    validado seja alcançado. A ordem da tupla de saída também é reproduzível.
    """

    if not isinstance(configuracao, ConfiguracaoScreener):
        raise TypeError("configuracao deve ser uma ConfiguracaoScreener validada")
    if configuracao.modo != "amostra":
        raise ErroGeracaoAmostra(
            "MODO_NAO_AMOSTRAL", "O gerador amostral exige o modo amostra."
        )
    if configuracao.limite_combinacoes != LIMITE_EXPERIMENTAL:
        raise ErroGeracaoAmostra(
            "LIMITE_NAO_AUTORIZADO", "O gerador está limitado a 5.000 combinações."
        )

    aleatorio = Random(configuracao.semente)
    vistos: set[Combinacao] = set()
    amostra: list[Combinacao] = []
    universo = range(MENOR_DEZENA, MAIOR_DEZENA + 1)
    while len(amostra) < configuracao.limite_combinacoes:
        combinacao = tuple(sorted(aleatorio.sample(universo, QUANTIDADE_DEZENAS)))
        if combinacao in vistos:
            continue
        vistos.add(combinacao)
        amostra.append(combinacao)
    return tuple(amostra)
