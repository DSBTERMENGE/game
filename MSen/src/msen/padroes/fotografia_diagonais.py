"""Fotografia imutável da distribuição histórica diagonal."""

from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from hashlib import sha256
from types import MappingProxyType

from msen.modelos import ResultadoEntrada

from .distribuicao_diagonais import (
    DistribuicaoCategoriasDiagonais,
    IncidenciaCategoriaDiagonal,
    calcular_distribuicao_categorias_diagonais,
)


VERSAO_CALCULO_DIAGONAL = 1


@dataclass(frozen=True, slots=True)
class FotografiaHistoricaDiagonal:
    """Distribuição identificada e indexada para uma execução do funil."""

    identificacao_carga: str
    versao_calculo: int
    distribuicao: DistribuicaoCategoriasDiagonais
    _indice: Mapping[str, IncidenciaCategoriaDiagonal] = field(
        init=False,
        repr=False,
        compare=False,
    )

    def __post_init__(self) -> None:
        if not self.identificacao_carga.startswith("sha256:"):
            raise ValueError("A fotografia exige a identificação SHA-256 da carga.")
        if self.versao_calculo <= 0:
            raise ValueError("A versão do cálculo deve ser positiva.")
        indice = {item.codigo: item for item in self.distribuicao.incidencias}
        if len(indice) != len(self.distribuicao.incidencias):
            raise ValueError("A fotografia não aceita categorias repetidas.")
        object.__setattr__(self, "_indice", MappingProxyType(indice))

    @property
    def total_resultados(self) -> int:
        """Quantidade histórica comum a todas as categorias."""

        return self.distribuicao.total_resultados

    @property
    def incidencias(self) -> tuple[IncidenciaCategoriaDiagonal, ...]:
        """Tabela ordenada usada também pelo futuro comando `Ver tuplas`."""

        return self.distribuicao.incidencias

    def obter(self, codigo: str) -> IncidenciaCategoriaDiagonal:
        """Consulta uma categoria em tempo constante, sem recalcular a tabela."""

        return self._indice[codigo]


def _identificar_carga(resultados: tuple[ResultadoEntrada, ...]) -> str:
    resumo = sha256()
    for resultado in sorted(resultados, key=lambda item: item.numero_ap):
        linha = (
            str(resultado.numero_ap),
            resultado.data_resultado.isoformat(),
            *(str(dezena) for dezena in resultado.resultados),
        )
        resumo.update("|".join(linha).encode("ascii"))
        resumo.update(b"\n")
    return f"sha256:{resumo.hexdigest()}"


def criar_fotografia_historica_diagonal(
    resultados: Iterable[ResultadoEntrada],
) -> FotografiaHistoricaDiagonal:
    """Calcula uma única fotografia reutilizável da carga informada."""

    serie = tuple(resultados)
    distribuicao = calcular_distribuicao_categorias_diagonais(serie)
    return FotografiaHistoricaDiagonal(
        identificacao_carga=_identificar_carga(serie),
        versao_calculo=VERSAO_CALCULO_DIAGONAL,
        distribuicao=distribuicao,
    )
