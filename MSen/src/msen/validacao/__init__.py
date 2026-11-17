"""Homologação das funções usadas pelo algoritmo de seleção."""

from .registro import (
    DefinicaoCriterio, RegistroCriteriosValidacao,
    criar_definicao_criterio_diagonal,
    criar_registro_criterios_producao,
)

__all__ = [
    "DefinicaoCriterio", "RegistroCriteriosValidacao",
    "criar_definicao_criterio_diagonal",
    "criar_registro_criterios_producao",
]
