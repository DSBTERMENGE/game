"""Homologação das funções usadas pelo algoritmo de seleção."""

from .registro import (
    DefinicaoCriterio, RegistroCriteriosValidacao,
    criar_definicao_criterio_diagonal,
    criar_registro_criterios_producao,
)
from .gerador_resultados_teste import (
    CombinacaoTeste,
    chave_canonica,
    gerar_combinacoes_teste,
)

__all__ = [
    "DefinicaoCriterio", "RegistroCriteriosValidacao",
    "criar_definicao_criterio_diagonal",
    "criar_registro_criterios_producao",
    "CombinacaoTeste",
    "chave_canonica",
    "gerar_combinacoes_teste",
]
