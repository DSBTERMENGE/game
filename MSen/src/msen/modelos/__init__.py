"""Modelos de domínio do MSen."""

from .resultado import ErroValidacaoResultado, ResultadoEntrada
from .classificacao_padrao import (
    ClassificacaoPadrao,
    EstadoClassificacaoPadrao,
    validar_classificacao,
)

__all__ = [
    "ClassificacaoPadrao",
    "EstadoClassificacaoPadrao",
    "ErroValidacaoResultado",
    "ResultadoEntrada",
    "validar_classificacao",
]
