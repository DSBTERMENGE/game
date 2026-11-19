"""Geração aleatória da coleção fixa usada nos testes de detectores."""

from collections.abc import Callable, Sequence
from math import comb
from random import SystemRandom


CombinacaoTeste = tuple[int, int, int, int, int, int]
SorteadorCombinacao = Callable[[], Sequence[int]]
TOTAL_COMBINACOES_POSSIVEIS = comb(60, 6)


def chave_canonica(combinacao: Sequence[int]) -> CombinacaoTeste:
    """Ordena uma cópia somente para reconhecer permutações da combinação."""

    valores = _validar_combinacao(combinacao)
    return tuple(sorted(valores))  # type: ignore[return-value]


def _validar_combinacao(combinacao: Sequence[int]) -> CombinacaoTeste:
    if isinstance(combinacao, (str, bytes)) or not isinstance(combinacao, Sequence):
        raise TypeError("A combinação deve ser uma sequência de seis dezenas.")
    valores = tuple(combinacao)
    if len(valores) != 6:
        raise ValueError("A combinação deve conter exatamente seis dezenas.")
    if any(isinstance(valor, bool) or not isinstance(valor, int) for valor in valores):
        raise TypeError("Cada dezena deve ser um número inteiro.")
    if any(valor < 1 or valor > 60 for valor in valores):
        raise ValueError("Cada dezena deve estar entre 1 e 60.")
    if len(set(valores)) != 6:
        raise ValueError("As seis dezenas da combinação devem ser diferentes.")
    return valores  # type: ignore[return-value]


def gerar_combinacoes_teste(
    quantidade: int = 1_000,
    *,
    sortear: SorteadorCombinacao | None = None,
) -> tuple[CombinacaoTeste, ...]:
    """Gera combinações únicas sem alterar a ordem produzida pelo sorteador.

    A chave ordenada existe apenas no conjunto de controle em memória. A
    combinação devolvida conserva integralmente a ordem em que foi sorteada.
    """

    if isinstance(quantidade, bool) or not isinstance(quantidade, int):
        raise TypeError("A quantidade deve ser um número inteiro.")
    if quantidade < 1 or quantidade > TOTAL_COMBINACOES_POSSIVEIS:
        raise ValueError(
            f"A quantidade deve estar entre 1 e {TOTAL_COMBINACOES_POSSIVEIS}."
        )

    aleatorio = SystemRandom()
    sorteador = sortear or (lambda: aleatorio.sample(range(1, 61), 6))
    chaves_aceitas: set[CombinacaoTeste] = set()
    combinacoes: list[CombinacaoTeste] = []

    while len(combinacoes) < quantidade:
        combinacao = _validar_combinacao(sorteador())
        chave = chave_canonica(combinacao)
        if chave in chaves_aceitas:
            continue
        chaves_aceitas.add(chave)
        combinacoes.append(combinacao)

    return tuple(combinacoes)
