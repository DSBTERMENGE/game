"""Contratos e infraestrutura para os detectores de padrões do MSen."""

from .catalogo import criar_registro_detectores_aprovados
from .classificacao import (
    CODIGO_GRUPO_SEQUENCIAIS,
    ClassificacaoGrupoSequenciais,
    classificar_grupo_dezenas_sequenciais,
)
from .contratos import DetectorPadrao
from .colunas import (
    CODIGO_DUAS_NA_MESMA_COLUNA,
    CODIGO_MAIS_DE_TRES_NA_MESMA_COLUNA,
    CODIGO_TRES_NA_MESMA_COLUNA,
    calcular_estatisticas_mesma_coluna,
    criar_registro_detectores_mesma_coluna,
)
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
from .linhas import (
    CODIGO_DUAS_NA_MESMA_LINHA,
    CODIGO_MAIS_DE_TRES_NA_MESMA_LINHA,
    CODIGO_TRES_NA_MESMA_LINHA,
    calcular_estatisticas_mesma_linha,
    criar_registro_detectores_mesma_linha,
)
from .mesma_coluna import (
    detectar_duas_dezenas_na_mesma_coluna,
    detectar_mais_de_tres_dezenas_na_mesma_coluna,
    detectar_tres_dezenas_na_mesma_coluna,
)
from .mesma_linha import (
    detectar_duas_dezenas_na_mesma_linha,
    detectar_mais_de_tres_dezenas_na_mesma_linha,
    detectar_tres_dezenas_na_mesma_linha,
)
from .registro import (
    CodigoPadraoInvalido,
    DetectorJaRegistrado,
    DetectorNaoRegistrado,
    RegistroDetectores,
)
from .sequenciais import (
    AnaliseSequencial,
    analisar_dezenas_sequenciais,
    detectar_duas_dezenas_sequenciais,
    detectar_mais_de_tres_dezenas_sequenciais,
    detectar_tres_dezenas_sequenciais,
)

__all__ = [
    "CodigoPadraoInvalido",
    "AnaliseSequencial",
    "ClassificacaoGrupoSequenciais",
    "DetectorJaRegistrado",
    "DetectorNaoRegistrado",
    "DetectorPadrao",
    "ErroAnalisePadrao",
    "EstatisticaPadrao",
    "RegistroDetectores",
    "CODIGO_DUAS_SEQUENCIAIS",
    "CODIGO_GRUPO_SEQUENCIAIS",
    "CODIGO_TRES_SEQUENCIAIS",
    "CODIGO_MAIS_DE_TRES_SEQUENCIAIS",
    "CODIGO_DUAS_NA_MESMA_COLUNA",
    "CODIGO_TRES_NA_MESMA_COLUNA",
    "CODIGO_MAIS_DE_TRES_NA_MESMA_COLUNA",
    "CODIGO_DUAS_NA_MESMA_LINHA",
    "CODIGO_TRES_NA_MESMA_LINHA",
    "CODIGO_MAIS_DE_TRES_NA_MESMA_LINHA",
    "calcular_estatistica_padrao",
    "analisar_dezenas_sequenciais",
    "classificar_grupo_dezenas_sequenciais",
    "calcular_estatisticas_sequenciais",
    "calcular_estatisticas_mesma_coluna",
    "calcular_estatisticas_mesma_linha",
    "criar_registro_detectores_iniciais",
    "criar_registro_detectores_mesma_coluna",
    "criar_registro_detectores_mesma_linha",
    "criar_registro_detectores_aprovados",
    "detectar_duas_dezenas_sequenciais",
    "detectar_tres_dezenas_sequenciais",
    "detectar_mais_de_tres_dezenas_sequenciais",
    "detectar_duas_dezenas_na_mesma_coluna",
    "detectar_tres_dezenas_na_mesma_coluna",
    "detectar_mais_de_tres_dezenas_na_mesma_coluna",
    "detectar_duas_dezenas_na_mesma_linha",
    "detectar_tres_dezenas_na_mesma_linha",
    "detectar_mais_de_tres_dezenas_na_mesma_linha",
]
