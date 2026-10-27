"""Coordenação do cálculo e da persistência das medidas geométricas."""

from dataclasses import dataclass
from decimal import Decimal, localcontext
from fractions import Fraction

import psycopg

from msen.database import (
    AnaliseGeometricaPersistida,
    RepositorioAnaliseGeometrica,
    RepositorioResultados,
    ResultadoPersistido,
)
from msen.geometria import (
    calcular_area_e_centro_gravidade,
    calcular_extensao_aberta,
    calcular_perimetro_fechado,
)


VERSAO_CALCULO_GEOMETRICO = 1


@dataclass(frozen=True, slots=True)
class RelatorioRecalculoGeometrico:
    """Resume um recálculo integral das análises geométricas."""

    resultados_analisados: int
    analises: tuple[AnaliseGeometricaPersistida, ...]


def _decimal_exato(valor: Fraction) -> Decimal:
    with localcontext() as contexto:
        contexto.prec = 30
        return Decimal(valor.numerator) / Decimal(valor.denominator)


def calcular_e_persistir_analise_geometrica(
    conexao: psycopg.Connection, resultado: ResultadoPersistido
) -> AnaliseGeometricaPersistida:
    """Calcula e grava as medidas geométricas de um resultado persistido.

    Args:
        conexao: Conexão Psycopg participante da transação do caso de uso.
        resultado: Resultado que fornece identificador e seis dezenas.

    Returns:
        A análise gravada, arredondada pelo repositório para doze casas.
    """

    if not isinstance(conexao, psycopg.Connection):
        raise TypeError("O cálculo geométrico exige uma conexão Psycopg válida.")
    if not isinstance(resultado, ResultadoPersistido):
        raise TypeError("É necessário fornecer um ResultadoPersistido.")

    dezenas = resultado.resultado.resultados
    geometria = calcular_area_e_centro_gravidade(dezenas)
    centro = geometria.centro_gravidade
    return RepositorioAnaliseGeometrica(conexao).salvar(
        resultado.id_resultado,
        extensao_aberta=calcular_extensao_aberta(dezenas),
        perimetro_fechado=calcular_perimetro_fechado(dezenas),
        quantidade_regioes=len(geometria.regioes),
        area_total=_decimal_exato(geometria.area_total),
        centro_gravidade_x=None if centro is None else _decimal_exato(centro.x),
        centro_gravidade_y=None if centro is None else _decimal_exato(centro.y),
        versao_calculo=VERSAO_CALCULO_GEOMETRICO,
    )


def recalcular_analises_geometricas(
    conexao: psycopg.Connection,
) -> RelatorioRecalculoGeometrico:
    """Recalcula as análises de todos os resultados na mesma transação.

    Args:
        conexao: Conexão Psycopg do banco que contém o histórico.

    Returns:
        Quantidade processada e linhas geométricas persistidas.

    Regra:
        O limite atual de dez mil cobre o histórico conhecido. Uma ampliação
        futura deverá substituir esta leitura por paginação.
    """

    if not isinstance(conexao, psycopg.Connection):
        raise TypeError("O recálculo geométrico exige uma conexão Psycopg válida.")
    resultados = RepositorioResultados(conexao).listar(limite=10_000)
    with conexao.transaction():
        analises = tuple(
            calcular_e_persistir_analise_geometrica(conexao, resultado)
            for resultado in resultados
        )
    return RelatorioRecalculoGeometrico(len(resultados), analises)
