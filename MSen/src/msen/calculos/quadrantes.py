"""Distribuição das seis dezenas nos quatro quadrantes do volante."""

from collections import Counter
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP

from .coordenadas import calcular_coordenada
from .estatisticas_linha import calcular_desvio_padrao_populacional


SEIS_CASAS_DECIMAIS = Decimal("0.000001")


@dataclass(frozen=True, slots=True)
class DistribuicaoQuadrantes:
    q1: int
    q2: int
    q3: int
    q4: int
    codigo: str

    @property
    def contagens(self) -> tuple[int, int, int, int]:
        return self.q1, self.q2, self.q3, self.q4


@dataclass(frozen=True, slots=True)
class FrequenciaCodigoQuadrantes:
    codigo: str
    quantidade: int
    percentual: Decimal


@dataclass(frozen=True, slots=True)
class EstatisticaQuadrante:
    media: Decimal
    desvio_padrao_populacional: Decimal
    minimo: int
    maximo: int


@dataclass(frozen=True, slots=True)
class ResumoHistoricoQuadrantes:
    quantidade_resultados: int
    frequencias: tuple[FrequenciaCodigoQuadrantes, ...]
    quadrantes: tuple[EstatisticaQuadrante, ...]


def _validar_dezenas(dezenas: Sequence[int]) -> tuple[int, ...]:
    if isinstance(dezenas, (str, bytes)) or not isinstance(dezenas, Sequence):
        raise TypeError("Os quadrantes exigem uma sequência com seis dezenas.")
    if len(dezenas) != 6:
        raise ValueError("Os quadrantes exigem exatamente seis dezenas.")
    if any(isinstance(valor, bool) or not isinstance(valor, int) for valor in dezenas):
        raise TypeError("As dezenas dos quadrantes devem ser números inteiros.")
    if any(valor < 1 or valor > 60 for valor in dezenas):
        raise ValueError("As dezenas dos quadrantes devem estar entre 1 e 60.")
    if len(set(dezenas)) != 6:
        raise ValueError("As seis dezenas dos quadrantes devem ser diferentes.")
    return tuple(dezenas)


def identificar_quadrante(dezena: int) -> int:
    """Classifica uma dezena: Q1 superior direito, depois sentido anti-horário."""

    x, y = calcular_coordenada(dezena)
    if y <= 2:
        return 1 if x >= 5 else 2
    return 4 if x >= 5 else 3


def calcular_distribuicao_quadrantes(
    dezenas: Sequence[int],
) -> DistribuicaoQuadrantes:
    contagens = [0, 0, 0, 0]
    for dezena in _validar_dezenas(dezenas):
        contagens[identificar_quadrante(dezena) - 1] += 1
    codigo = "".join(str(valor) for valor in contagens)
    return DistribuicaoQuadrantes(*contagens, codigo=codigo)


def calcular_resumo_historico_quadrantes(
    resultados: Iterable[Sequence[int]],
) -> ResumoHistoricoQuadrantes:
    distribuicoes = tuple(calcular_distribuicao_quadrantes(item) for item in resultados)
    if not distribuicoes:
        raise ValueError("O resumo dos quadrantes exige ao menos um resultado.")

    total = len(distribuicoes)
    codigos = Counter(item.codigo for item in distribuicoes)
    frequencias = tuple(
        FrequenciaCodigoQuadrantes(
            codigo=codigo,
            quantidade=quantidade,
            percentual=(Decimal(quantidade) * Decimal(100) / Decimal(total)).quantize(
                SEIS_CASAS_DECIMAIS, rounding=ROUND_HALF_UP
            ),
        )
        for codigo, quantidade in sorted(codigos.items())
    )

    estatisticas = []
    for indice in range(4):
        valores = tuple(item.contagens[indice] for item in distribuicoes)
        media = (Decimal(sum(valores)) / Decimal(total)).quantize(
            SEIS_CASAS_DECIMAIS, rounding=ROUND_HALF_UP
        )
        estatisticas.append(
            EstatisticaQuadrante(
                media=media,
                desvio_padrao_populacional=calcular_desvio_padrao_populacional(valores),
                minimo=min(valores),
                maximo=max(valores),
            )
        )
    return ResumoHistoricoQuadrantes(total, frequencias, tuple(estatisticas))
