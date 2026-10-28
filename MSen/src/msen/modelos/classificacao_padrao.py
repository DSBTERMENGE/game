"""Modelo imutável da classificação de um resultado em um grupo de padrões."""

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum


class EstadoClassificacaoPadrao(StrEnum):
    """Estados persistidos possíveis para a classificação em um grupo."""

    PADRAO_IDENTIFICADO = "PADRAO_IDENTIFICADO"
    SEM_CORRESPONDENCIA = "SEM_CORRESPONDENCIA"


def validar_classificacao(
    id_resultado: int,
    id_grupo: int,
    id_padrao: int | None,
    estado: EstadoClassificacaoPadrao,
    versao_calculo: int,
) -> None:
    """Valida identificadores, estado e versão antes do acesso ao banco."""

    for nome, valor in (("id_resultado", id_resultado), ("id_grupo", id_grupo)):
        if isinstance(valor, bool) or not isinstance(valor, int):
            raise TypeError(f"{nome} deve ser inteiro.")
        if valor <= 0:
            raise ValueError(f"{nome} deve ser positivo.")
    if id_padrao is not None:
        if isinstance(id_padrao, bool) or not isinstance(id_padrao, int):
            raise TypeError("id_padrao deve ser inteiro ou nulo.")
        if id_padrao <= 0:
            raise ValueError("id_padrao deve ser positivo quando informado.")
    if not isinstance(estado, EstadoClassificacaoPadrao):
        raise TypeError("estado deve ser EstadoClassificacaoPadrao.")
    if estado is EstadoClassificacaoPadrao.PADRAO_IDENTIFICADO and id_padrao is None:
        raise ValueError("PADRAO_IDENTIFICADO exige id_padrao.")
    if estado is EstadoClassificacaoPadrao.SEM_CORRESPONDENCIA and id_padrao is not None:
        raise ValueError("SEM_CORRESPONDENCIA não aceita id_padrao.")
    if isinstance(versao_calculo, bool) or not isinstance(versao_calculo, int):
        raise TypeError("versao_calculo deve ser inteira.")
    if versao_calculo <= 0:
        raise ValueError("versao_calculo deve ser positiva.")


@dataclass(frozen=True, slots=True)
class ClassificacaoPadrao:
    """Classificação persistida de um resultado dentro de um grupo."""

    id_classificacao: int
    id_resultado: int
    id_grupo: int
    id_padrao: int | None
    estado: EstadoClassificacaoPadrao
    versao_calculo: int
    calculado_em: datetime

    def __post_init__(self) -> None:
        if isinstance(self.id_classificacao, bool) or not isinstance(
            self.id_classificacao, int
        ):
            raise TypeError("id_classificacao deve ser inteiro.")
        if self.id_classificacao <= 0:
            raise ValueError("id_classificacao deve ser positivo.")
        validar_classificacao(
            self.id_resultado,
            self.id_grupo,
            self.id_padrao,
            self.estado,
            self.versao_calculo,
        )
        if not isinstance(self.calculado_em, datetime):
            raise TypeError("calculado_em deve ser datetime.")
        if self.calculado_em.tzinfo is None:
            raise ValueError("calculado_em deve conter fuso horário.")
