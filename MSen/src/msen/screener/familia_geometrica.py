"""Família geométrica do funil extensível baseada nos cálculos oficiais."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, localcontext
from fractions import Fraction
from functools import lru_cache

from msen.geometria import (
    calcular_area_e_centro_gravidade,
    calcular_extensao_aberta,
    calcular_perimetro_fechado,
)

from .contrato_extensivel import DecisaoFiltro, DefinicaoFamilia, DefinicaoFiltro
from .gerador import Combinacao


class ErroFamiliaGeometrica(ValueError):
    """Indica uma configuração geométrica inválida ou ambígua."""

    def __init__(self, codigo: str, mensagem: str) -> None:
        super().__init__(mensagem)
        self.codigo = codigo


@dataclass(frozen=True, slots=True)
class FaixaGeometrica:
    """Intervalo fechado usado para aceitar uma medida geométrica."""

    limite_inferior: Decimal
    limite_superior: Decimal

    @classmethod
    def criar(
        cls, limite_inferior: Decimal | int | str, limite_superior: Decimal | int | str
    ) -> FaixaGeometrica:
        """Cria uma faixa exata, finita e não invertida."""

        try:
            inferior = Decimal(limite_inferior)
            superior = Decimal(limite_superior)
        except Exception as erro:
            raise ErroFamiliaGeometrica(
                "LIMITE_INVALIDO", "Os limites devem ser números decimais exatos."
            ) from erro
        if not inferior.is_finite() or not superior.is_finite():
            raise ErroFamiliaGeometrica("LIMITE_INVALIDO", "Os limites devem ser finitos.")
        if inferior > superior:
            raise ErroFamiliaGeometrica(
                "FAIXA_INVERTIDA", "O limite inferior não pode superar o superior."
            )
        return cls(inferior, superior)

    def contem(self, valor: Decimal | int) -> bool:
        decimal = valor if isinstance(valor, Decimal) else Decimal(valor)
        return self.limite_inferior <= decimal <= self.limite_superior


@dataclass(frozen=True, slots=True)
class MedidasGeometricasCombinacao:
    """Conjunto único de medidas compartilhado por todos os filtros."""

    extensao_aberta: Decimal
    perimetro_fechado: Decimal
    quantidade_regioes: int
    area_total: Decimal
    centro_gravidade_x: Decimal | None
    centro_gravidade_y: Decimal | None


def _decimal_exato(valor: Fraction) -> Decimal:
    with localcontext() as contexto:
        contexto.prec = 30
        return Decimal(valor.numerator) / Decimal(valor.denominator)


def calcular_medidas_geometricas(combinacao: Combinacao) -> MedidasGeometricasCombinacao:
    """Executa uma vez o conjunto oficial de cálculos para uma combinação."""

    figura = calcular_area_e_centro_gravidade(combinacao)
    centro = figura.centro_gravidade
    return MedidasGeometricasCombinacao(
        calcular_extensao_aberta(combinacao),
        calcular_perimetro_fechado(combinacao),
        len(figura.regioes),
        _decimal_exato(figura.area_total),
        None if centro is None else _decimal_exato(centro.x),
        None if centro is None else _decimal_exato(centro.y),
    )


def _decisao(
    codigo: str, nome: str, valor: Decimal | int, faixa: FaixaGeometrica
) -> DecisaoFiltro:
    aprovada = faixa.contem(valor)
    return DecisaoFiltro.criar(
        codigo_filtro=codigo,
        aprovada=aprovada,
        motivo="DENTRO_DA_FAIXA" if aprovada else "FORA_DA_FAIXA",
        evidencias={
            nome: format(valor, "f") if isinstance(valor, Decimal) else valor,
            "limite_inferior": format(faixa.limite_inferior, "f"),
            "limite_superior": format(faixa.limite_superior, "f"),
            "intervalo": "fechado",
        },
    )


def criar_familia_geometrica(
    *,
    faixa_extensao: FaixaGeometrica,
    faixa_perimetro: FaixaGeometrica,
    faixa_area: FaixaGeometrica,
    faixa_quantidade_regioes: FaixaGeometrica,
    faixa_centro_x: FaixaGeometrica,
    faixa_centro_y: FaixaGeometrica,
    politica_centro_ausente: str,
    ordem: int = 2,
) -> DefinicaoFamilia:
    """Monta cinco filtros que compartilham uma única análise geométrica.

    O centro de gravidade é uma decisão única sobre X e Y. Quando não existe
    área positiva, o centro é nulo e a política explícita determina a decisão.
    """

    faixas = (
        faixa_extensao, faixa_perimetro, faixa_area, faixa_quantidade_regioes,
        faixa_centro_x, faixa_centro_y,
    )
    if any(not isinstance(item, FaixaGeometrica) for item in faixas):
        raise TypeError("Todas as faixas devem ser FaixaGeometrica.")
    if politica_centro_ausente not in {"aprovar", "excluir"}:
        raise ErroFamiliaGeometrica(
            "POLITICA_CENTRO_INVALIDA",
            "A política para centro ausente deve ser aprovar ou excluir.",
        )

    @lru_cache(maxsize=10_000)
    def medidas(combinacao: Combinacao) -> MedidasGeometricasCombinacao:
        return calcular_medidas_geometricas(combinacao)

    def extensao(combinacao: Combinacao) -> DecisaoFiltro:
        return _decisao(
            "GEO_EXTENSAO", "extensao_aberta", medidas(combinacao).extensao_aberta,
            faixa_extensao,
        )

    def perimetro(combinacao: Combinacao) -> DecisaoFiltro:
        return _decisao(
            "GEO_PERIMETRO", "perimetro_fechado",
            medidas(combinacao).perimetro_fechado, faixa_perimetro,
        )

    def area(combinacao: Combinacao) -> DecisaoFiltro:
        return _decisao(
            "GEO_AREA", "area_total", medidas(combinacao).area_total, faixa_area
        )

    def regioes(combinacao: Combinacao) -> DecisaoFiltro:
        return _decisao(
            "GEO_REGIOES", "quantidade_regioes",
            medidas(combinacao).quantidade_regioes, faixa_quantidade_regioes,
        )

    def centro(combinacao: Combinacao) -> DecisaoFiltro:
        calculadas = medidas(combinacao)
        x, y = calculadas.centro_gravidade_x, calculadas.centro_gravidade_y
        if x is None or y is None:
            aprovada = politica_centro_ausente == "aprovar"
            return DecisaoFiltro.criar(
                codigo_filtro="GEO_CENTRO_GRAVIDADE",
                aprovada=aprovada,
                motivo="CENTRO_AUSENTE_ACEITO" if aprovada else "CENTRO_AUSENTE_EXCLUIDO",
                evidencias={
                    "centro_gravidade_x": None,
                    "centro_gravidade_y": None,
                    "politica_centro_ausente": politica_centro_ausente,
                },
            )
        aprovada = faixa_centro_x.contem(x) and faixa_centro_y.contem(y)
        return DecisaoFiltro.criar(
            codigo_filtro="GEO_CENTRO_GRAVIDADE",
            aprovada=aprovada,
            motivo="DENTRO_DA_FAIXA" if aprovada else "FORA_DA_FAIXA",
            evidencias={
                "centro_gravidade_x": format(x, "f"),
                "centro_gravidade_y": format(y, "f"),
                "limite_inferior_x": format(faixa_centro_x.limite_inferior, "f"),
                "limite_superior_x": format(faixa_centro_x.limite_superior, "f"),
                "limite_inferior_y": format(faixa_centro_y.limite_inferior, "f"),
                "limite_superior_y": format(faixa_centro_y.limite_superior, "f"),
                "intervalo": "fechado",
            },
        )

    return DefinicaoFamilia(
        "GEOMETRIA", "Análise geométrica", ordem,
        (
            DefinicaoFiltro("GEO_EXTENSAO", "Extensão aberta", 1, extensao),
            DefinicaoFiltro("GEO_PERIMETRO", "Perímetro fechado", 2, perimetro),
            DefinicaoFiltro("GEO_AREA", "Área total", 3, area),
            DefinicaoFiltro("GEO_REGIOES", "Quantidade de regiões", 4, regioes),
            DefinicaoFiltro(
                "GEO_CENTRO_GRAVIDADE", "Centro de gravidade", 5, centro
            ),
        ),
    )
