"""Configuração e, futuramente, execução do funil de combinações."""

from .configuracao import (
    ConfiguracaoCriterio,
    ConfiguracaoScreener,
    ErroConfiguracaoScreener,
    RegraConfigurada,
    RegraEstatisticaConfigurada,
    RegraGeometricaConfigurada,
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
from .politicas import (
    ErroPoliticaSombra,
    EvidenciaHistoricaPadrao,
    PoliticaPadraoAtiva,
    PoliticaPadraoSombra,
)
from .sombra import ResultadoSimulacaoSombra, simular_modo_sombra
from .ativacao import (
    ORDEM_ATIVA_PADRAO,
    criar_adaptadores_ativos,
    executar_padroes_ativos,
    executar_pd003_ativo,
)
from .comparacao_ordens import (
    ORDENS_EXPERIMENTAIS,
    ResultadoOrdemFiltros,
    comparar_ordens_filtros,
)
from .quadro_ativo import gerar_quadro_screener
from .politicas_geometricas import (
    PoliticaExtensaoAtiva,
    PoliticaExtensaoSombra,
    extensao_fora_faixa,
)
from .politicas_estatisticas import (
    PoliticaDesvioPadraoSombra,
    PoliticaDesvioPadraoAtiva,
    PoliticaMediaAtiva,
    PoliticaMediaSombra,
    PoliticaMedianaSombra,
    PoliticaMedianaAtiva,
    desvio_fora_faixa,
    media_fora_faixa,
    mediana_fora_faixa,
)

__all__ = [
    "ConfiguracaoCriterio",
    "ConfiguracaoScreener",
    "ErroConfiguracaoScreener",
    "RegraConfigurada",
    "RegraEstatisticaConfigurada",
    "RegraGeometricaConfigurada",
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
    "ErroPoliticaSombra",
    "EvidenciaHistoricaPadrao",
    "PoliticaPadraoAtiva",
    "PoliticaPadraoSombra",
    "ResultadoSimulacaoSombra",
    "simular_modo_sombra",
    "executar_pd003_ativo",
    "executar_padroes_ativos",
    "criar_adaptadores_ativos",
    "ORDEM_ATIVA_PADRAO",
    "ORDENS_EXPERIMENTAIS",
    "ResultadoOrdemFiltros",
    "comparar_ordens_filtros",
    "gerar_quadro_screener",
    "PoliticaMediaSombra",
    "PoliticaMediaAtiva",
    "PoliticaMedianaSombra",
    "PoliticaMedianaAtiva",
    "PoliticaDesvioPadraoSombra",
    "PoliticaDesvioPadraoAtiva",
    "desvio_fora_faixa",
    "mediana_fora_faixa",
    "media_fora_faixa",
    "PoliticaExtensaoSombra",
    "PoliticaExtensaoAtiva",
    "extensao_fora_faixa",
]
