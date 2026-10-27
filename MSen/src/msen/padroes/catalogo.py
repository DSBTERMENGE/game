"""Catálogo unificado dos detectores de padrões já implementados."""

from .colunas import criar_registro_detectores_mesma_coluna
from .iniciais import criar_registro_detectores_iniciais
from .linhas import criar_registro_detectores_mesma_linha
from .registro import RegistroDetectores


def criar_registro_detectores_aprovados() -> RegistroDetectores:
    """Cria um registro novo com todos os detectores aprovados no sistema.

    Retorno:
        Registro contendo os códigos implementados de `PD_001` a `PD_006`.

    Regra:
        Os registros especializados são combinados em uma instância nova. Uma
        duplicidade de código continua sendo rejeitada pelo registro central.
    """

    registro = RegistroDetectores()
    for origem in (
        criar_registro_detectores_iniciais(),
        criar_registro_detectores_mesma_coluna(),
        criar_registro_detectores_mesma_linha(),
    ):
        for codigo in origem.codigos_registrados():
            registro.registrar(codigo, origem.obter(codigo))
    return registro
