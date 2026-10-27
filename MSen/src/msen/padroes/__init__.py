"""Contratos e infraestrutura para os detectores de padrões do MSen."""

from .contratos import DetectorPadrao
from .estatisticas import (
    ErroAnalisePadrao,
    EstatisticaPadrao,
    calcular_estatistica_padrao,
)
from .iniciais import (
    CODIGO_DUAS_SEQUENCIAIS,
    CODIGO_MAIS_DE_TRES_SEQUENCIAIS,
    CODIGO_TRES_SEQUENCIAIS,
    calcular_estatisticas_sequenciais,
    criar_registro_detectores_iniciais,
)
from .registro import (
    CodigoPadraoInvalido,
    DetectorJaRegistrado,
    DetectorNaoRegistrado,
    RegistroDetectores,
)
from .sequenciais import (
    detectar_duas_dezenas_sequenciais,
    detectar_mais_de_tres_dezenas_sequenciais,
    detectar_tres_dezenas_sequenciais,
)

__all__ = [
    "CodigoPadraoInvalido",
    "DetectorJaRegistrado",
    "DetectorNaoRegistrado",
    "DetectorPadrao",
    "ErroAnalisePadrao",
    "EstatisticaPadrao",
    "RegistroDetectores",
    "CODIGO_DUAS_SEQUENCIAIS",
    "CODIGO_TRES_SEQUENCIAIS",
    "CODIGO_MAIS_DE_TRES_SEQUENCIAIS",
    "calcular_estatistica_padrao",
    "calcular_estatisticas_sequenciais",
    "criar_registro_detectores_iniciais",
    "detectar_duas_dezenas_sequenciais",
    "detectar_tres_dezenas_sequenciais",
    "detectar_mais_de_tres_dezenas_sequenciais",
]
