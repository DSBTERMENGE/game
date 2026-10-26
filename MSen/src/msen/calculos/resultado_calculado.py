"""Composição dos cálculos derivados de uma linha validada."""

from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from msen.modelos import ResultadoEntrada

from .coordenadas import calcular_media_espacial
from .estatisticas_linha import (
    calcular_desvio_padrao_media,
    calcular_media_aritmetica,
    calcular_mediana,
    calcular_soma,
)


VERSAO_CALCULO_ATUAL = 1


@dataclass(frozen=True, slots=True)
class ResultadoCalculado:
    """Campos originais e derivados prontos para a futura persistência."""

    data_resultado: date
    numero_ap: int
    res_01: int
    res_02: int
    res_03: int
    res_04: int
    res_05: int
    res_06: int
    soma_res: int
    media_aritmetica_res: Decimal
    mediana_res: Decimal
    desvio_padrao_media: Decimal
    media_coordenada_x: Decimal
    media_coordenada_y: Decimal
    versao_calculo: int

    @property
    def resultados(self) -> tuple[int, int, int, int, int, int]:
        return (self.res_01, self.res_02, self.res_03, self.res_04, self.res_05, self.res_06)


def calcular_resultado(resultado: ResultadoEntrada) -> ResultadoCalculado:
    """Executa uma vez todas as funções de linha aprovadas na Etapa 2."""

    if not isinstance(resultado, ResultadoEntrada):
        raise TypeError("O cálculo exige um ResultadoEntrada validado.")

    media_espacial = calcular_media_espacial(resultado)
    return ResultadoCalculado(
        data_resultado=resultado.data_resultado,
        numero_ap=resultado.numero_ap,
        res_01=resultado.res_01,
        res_02=resultado.res_02,
        res_03=resultado.res_03,
        res_04=resultado.res_04,
        res_05=resultado.res_05,
        res_06=resultado.res_06,
        soma_res=calcular_soma(resultado),
        media_aritmetica_res=calcular_media_aritmetica(resultado),
        mediana_res=calcular_mediana(resultado),
        desvio_padrao_media=calcular_desvio_padrao_media(resultado),
        media_coordenada_x=media_espacial.x,
        media_coordenada_y=media_espacial.y,
        versao_calculo=VERSAO_CALCULO_ATUAL,
    )
