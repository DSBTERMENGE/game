"""Configuração e, futuramente, execução do funil de combinações."""

from .configuracao import (
    ConfiguracaoCriterio,
    ConfiguracaoScreener,
    ErroConfiguracaoScreener,
    carregar_configuracao_screener,
)
from .gerador import (
    CONFIRMACAO_INTEGRAL,
    TOTAL_COMBINACOES,
    ErroGeracaoAmostra,
    ErroGeracaoIntegral,
    criar_iterador_combinacoes,
    gerar_amostra,
)
from .funil import (
    CriterioFunil,
    DecisaoCriterio,
    ErroFunil,
    RelatorioFunil,
    executar_funil,
)
from .adaptadores import (
    AdaptadorMedidasEstatisticas,
    AdaptadorMedidasGeometricas,
    AdaptadorPadroesHistoricos,
    ErroAdaptadorCriterio,
    ResultadoAvaliador,
)
from .quadro import (
    LinhaQuadroAvaliacao,
    QuadroAvaliacao,
    executar_ensaio,
    serializar_quadro_avaliacao,
)
from .ensaio import ErroEnsaioIntegrado, executar_ensaio_amostral
from .capacidade import EstimativaCapacidade, estimar_capacidade

__all__ = [
    "ConfiguracaoCriterio",
    "ConfiguracaoScreener",
    "ErroConfiguracaoScreener",
    "carregar_configuracao_screener",
    "ErroGeracaoAmostra",
    "ErroGeracaoIntegral",
    "CONFIRMACAO_INTEGRAL",
    "TOTAL_COMBINACOES",
    "criar_iterador_combinacoes",
    "gerar_amostra",
    "CriterioFunil",
    "DecisaoCriterio",
    "ErroFunil",
    "RelatorioFunil",
    "executar_funil",
    "AdaptadorMedidasEstatisticas",
    "AdaptadorMedidasGeometricas",
    "AdaptadorPadroesHistoricos",
    "ErroAdaptadorCriterio",
    "ResultadoAvaliador",
    "LinhaQuadroAvaliacao",
    "QuadroAvaliacao",
    "executar_ensaio",
    "serializar_quadro_avaliacao",
    "ErroEnsaioIntegrado",
    "executar_ensaio_amostral",
    "EstimativaCapacidade",
    "estimar_capacidade",
]
