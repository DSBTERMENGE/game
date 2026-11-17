"""Análise das assinaturas formadas pelas diagonais que cruzam uma dezena."""

from dataclasses import dataclass
from functools import cache

from msen.calculos import calcular_coordenada

from .entrada import validar_dezenas


CATEGORIA_SEM_REFERENCIA_LONGA = "SEM_REFERENCIA_LONGA"
PASSO_DIAGONAL_DIREITA = 9
PASSO_DIAGONAL_ESQUERDA = 11
POSICOES_REFERENCIA = (2, 3, 4, 5)
COMPRIMENTO_MINIMO_DIAGONAL = 4


@dataclass(frozen=True, slots=True, order=True)
class AssinaturaDiagonal:
    """Quantidade de companheiras nas inclinações direita e esquerda."""

    direita: int
    esquerda: int

    def __post_init__(self) -> None:
        if self.direita < 0 or self.esquerda < 0:
            raise ValueError("As quantidades diagonais não podem ser negativas.")
        if self.direita + self.esquerda > 5:
            raise ValueError("Uma referência possui somente cinco outras dezenas.")

    @property
    def codigo(self) -> str:
        """Representa a assinatura na notação curta `xDyE`."""

        return f"{self.direita}D{self.esquerda}E"


@dataclass(frozen=True, slots=True)
class AnaliseReferenciaDiagonal:
    """Evidência das diagonais que cruzam uma referência elegível ou não."""

    posicao: int
    dezena: int
    diagonal_direita: tuple[int, ...]
    diagonal_esquerda: tuple[int, ...]
    assinatura: AssinaturaDiagonal | None

    @property
    def elegivel(self) -> bool:
        """Indica se as duas diagonais possuem pelo menos quatro posições."""

        return self.assinatura is not None


@dataclass(frozen=True, slots=True)
class AnaliseAssinaturasDiagonais:
    """Perfil consolidado das referências intermediárias de uma combinação."""

    dezenas_ordenadas: tuple[int, ...]
    referencias: tuple[AnaliseReferenciaDiagonal, ...]
    assinaturas: tuple[AssinaturaDiagonal, ...]

    @property
    def sem_referencia_longa(self) -> bool:
        """Indica que nenhuma referência possuía duas diagonais longas."""

        return not self.assinaturas


@cache
def _diagonais_da_dezena(
    dezena: int,
) -> tuple[tuple[int, ...], tuple[int, ...]]:
    x_referencia, y_referencia = calcular_coordenada(dezena)
    soma_referencia = x_referencia + y_referencia
    diferenca_referencia = x_referencia - y_referencia
    direita: list[int] = []
    esquerda: list[int] = []
    for candidata in range(1, 61):
        x, y = calcular_coordenada(candidata)
        if x + y == soma_referencia:
            direita.append(candidata)
        if x - y == diferenca_referencia:
            esquerda.append(candidata)
    return tuple(direita), tuple(esquerda)


def _analisar_referencia(
    dezenas: tuple[int, ...], posicao: int
) -> AnaliseReferenciaDiagonal:
    dezena = dezenas[posicao - 1]
    direita, esquerda = _diagonais_da_dezena(dezena)
    assinatura = None
    if (
        len(direita) >= COMPRIMENTO_MINIMO_DIAGONAL
        and len(esquerda) >= COMPRIMENTO_MINIMO_DIAGONAL
    ):
        outras = set(dezenas) - {dezena}
        assinatura = AssinaturaDiagonal(
            direita=len(outras.intersection(direita)),
            esquerda=len(outras.intersection(esquerda)),
        )
    return AnaliseReferenciaDiagonal(
        posicao=posicao,
        dezena=dezena,
        diagonal_direita=direita,
        diagonal_esquerda=esquerda,
        assinatura=assinatura,
    )


def analisar_assinaturas_diagonais(
    dezenas: tuple[int, ...],
) -> AnaliseAssinaturasDiagonais:
    """Analisa as assinaturas `xDyE` das referências P2, P3, P4 e P5.

    A própria referência não entra na contagem. A posição relativa das demais
    dezenas, as lacunas e as aparências em V ou X não alteram a assinatura.
    """

    ordenadas = validar_dezenas(dezenas)
    referencias = tuple(
        _analisar_referencia(ordenadas, posicao)
        for posicao in POSICOES_REFERENCIA
    )
    assinaturas = tuple(
        sorted(
            {
                referencia.assinatura
                for referencia in referencias
                if referencia.assinatura is not None
            }
        )
    )
    return AnaliseAssinaturasDiagonais(
        dezenas_ordenadas=ordenadas,
        referencias=referencias,
        assinaturas=assinaturas,
    )


def calcular_categorias_diagonais(dezenas: tuple[int, ...]) -> str:
    """Devolve a assinatura categórica persistível do arranjo diagonal."""

    analise = analisar_assinaturas_diagonais(dezenas)
    if analise.sem_referencia_longa:
        return CATEGORIA_SEM_REFERENCIA_LONGA
    return "|".join(item.codigo for item in analise.assinaturas)
