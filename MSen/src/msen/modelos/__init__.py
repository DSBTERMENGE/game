"""Modelos de domínio do MSen."""

from .resultado import ErroValidacaoResultado, ResultadoEntrada
from .classificacao_padrao import (
    ClassificacaoPadrao,
    validar_classificacao,
)

__all__ = [
    "ClassificacaoPadrao",
    "ErroValidacaoResultado",
    "ResultadoEntrada",
    "validar_classificacao",
]
