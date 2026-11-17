"""Distribuição histórica, em memória, das categorias diagonais."""

from collections import Counter
from collections.abc import Iterable
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP

from msen.modelos import ResultadoEntrada

from .diagonais import (
    CATEGORIA_SEM_REFERENCIA_LONGA,
    analisar_assinaturas_diagonais,
)


SEIS_CASAS_DECIMAIS = Decimal("0.000001")
CODIGOS_ASSINATURAS_DIAGONAIS = tuple(
    f"{direita}D{esquerda}E"
    for direita in range(6)
    for esquerda in range(6 - direita)
)
CODIGOS_CATEGORIAS_DIAGONAIS = (
    *CODIGOS_ASSINATURAS_DIAGONAIS,
    CATEGORIA_SEM_REFERENCIA_LONGA,
)


@dataclass(frozen=True, slots=True)
class IncidenciaCategoriaDiagonal:
    """Ocorrência e percentual de uma categoria no mesmo denominador."""

    codigo: str
    ocorrencias: int
    total_resultados: int
    percentual: Decimal


@dataclass(frozen=True, slots=True)
class DistribuicaoCategoriasDiagonais:
    """Tabela completa das categorias diagonais calculada em memória."""

    total_resultados: int
    incidencias: tuple[IncidenciaCategoriaDiagonal, ...]

    def obter(self, codigo: str) -> IncidenciaCategoriaDiagonal:
        """Obtém uma categoria pelo código estável."""

        for incidencia in self.incidencias:
            if incidencia.codigo == codigo:
                return incidencia
        raise KeyError(codigo)


def _percentual(ocorrencias: int, total: int) -> Decimal:
    return (Decimal(ocorrencias) * Decimal(100) / Decimal(total)).quantize(
        SEIS_CASAS_DECIMAIS,
        rounding=ROUND_HALF_UP,
    )


def calcular_distribuicao_categorias_diagonais(
    resultados: Iterable[ResultadoEntrada],
) -> DistribuicaoCategoriasDiagonais:
    """Conta cada categoria uma vez por resultado, sem decidir raridade.

    As categorias não são mutuamente exclusivas: um resultado pode contribuir
    para várias assinaturas. Somente resultados sem assinatura contribuem para
    `SEM_REFERENCIA_LONGA`.
    """

    serie = tuple(resultados)
    if not serie:
        raise ValueError("A distribuição diagonal exige ao menos um resultado.")
    if any(not isinstance(item, ResultadoEntrada) for item in serie):
        raise TypeError("A distribuição diagonal aceita somente ResultadoEntrada.")
    numeros = tuple(item.numero_ap for item in serie)
    if len(set(numeros)) != len(numeros):
        raise ValueError("A distribuição diagonal não aceita concursos repetidos.")

    contagens: Counter[str] = Counter()
    for resultado in serie:
        analise = analisar_assinaturas_diagonais(resultado.resultados)
        if analise.sem_referencia_longa:
            contagens[CATEGORIA_SEM_REFERENCIA_LONGA] += 1
        else:
            contagens.update(item.codigo for item in analise.assinaturas)

    total = len(serie)
    incidencias = tuple(
        IncidenciaCategoriaDiagonal(
            codigo=codigo,
            ocorrencias=contagens[codigo],
            total_resultados=total,
            percentual=_percentual(contagens[codigo], total),
        )
        for codigo in CODIGOS_CATEGORIAS_DIAGONAIS
    )
    return DistribuicaoCategoriasDiagonais(
        total_resultados=total,
        incidencias=incidencias,
    )
