"""Casos de uso coordenados da aplicação."""

from .importacao_banco import (
    RelatorioImportacaoBanco,
    importar_planilha_no_banco,
    salvar_relatorio_importacao,
)
from .manutencao_resultados import editar_resultado, incluir_resultado
from .padroes import RelatorioRecalculoPadroes, recalcular_padroes_iniciais
from .analise_geometrica import (
    RelatorioRecalculoGeometrico,
    calcular_e_persistir_analise_geometrica,
    recalcular_analises_geometricas,
)
from .classificacao_padroes import (
    ClassePerfilPadrao,
    ContagemClassificacao,
    ErroRecalculoClassificacao,
    PerfilClassificacaoGrupo,
    RelatorioRecalculoClassificacao,
    calcular_perfil_grupo_sequenciais,
    recalcular_classificacoes_grupo_sequenciais,
)
from .janela_historica import (
    ErroJanelaHistorica,
    JanelaHistorica,
    selecionar_janela_historica,
)
from .perfil_estatistico import (
    ErroPerfilEstatistico,
    FaixaPerfil,
    PerfilEstatistico,
    PontoDistribuicao,
    calcular_faixa_desvio_padrao,
    calcular_faixa_percentual_media,
    calcular_perfil_estatistico,
)
from .perfis_geometricos import (
    PerfilParametroGeometrico,
    PerfisGeometricos,
    calcular_perfis_geometricos,
)
from .distribuicoes import (
    ClasseHistograma,
    DistribuicaoVisual,
    PontoCurvaNormal,
    construir_distribuicao_visual,
)
from .selecao_padroes import SelecaoPadroesRaros, selecionar_padroes_raros
from .sincronizacao_validacao import (
    ExclusaoCriteriosNaoConfirmada,
    ResultadoSincronizacaoCriterios,
    sincronizar_criterios_validacao,
)
from .perfis_operacionais import (
    RelatorioPerfisOperacionais,
    atualizar_perfis_operacionais_atuais,
    marcar_perfis_operacionais_desatualizados,
)
from .carga_amostras_validacao import (
    RelatorioCargaAmostrasValidacao,
    carregar_amostras_iniciais_validacao,
)
from .referencias_validacao import (
    ErroReferenciaValidacao,
    ReferenciaAprovada,
    aprovar_referencia_categorica,
    aprovar_referencia_numerica,
    aprovar_referencia_padrao,
)
from .execucao_validacao import (
    ErroExecucaoValidacao,
    RelatorioExecucaoValidacao,
    ResultadoExecucaoCriterio,
    calcular_valor_criterio,
    comparar_resultado_categorico,
    comparar_resultado_padrao,
    comparar_resultado_numerico,
    executar_criterios_padroes,
    executar_criterio_categorico,
    executar_criterios_numericos,
)
from .motor_validacao import RelatorioMotorValidacao, atualizar_validacao_e_auditoria
from .configuracao_frequencia import (
    ConfiguracaoFrequencia,
    DivergenciaConfiguracaoFrequencia,
    comparar_configuracoes_frequencia,
    configuracao_frequencia_inicial,
)
from .configuracao_selecao_dezenas import (
    ConfiguracaoSelecaoDezenas,
    configuracao_selecao_inicial,
)
from .selecao_dezenas import (
    AvaliacaoSelecaoDezena,
    ErroSelecaoDezenas,
    EstatisticaDezenaCorte,
    ResultadoSelecaoDezenas,
    selecionar_dezenas_para_alvo,
)
from .backtest_selecao_dezenas import (
    ClasseBacktest,
    ErroBacktest,
    PontoBacktest,
    RelatorioBacktest,
    ResumoBacktest,
    executar_backtest,
    resumir_pontos,
)
from .previsao_selecao_dezenas import (
    DetalhePrevisao,
    RelatorioAtualizacaoPrevisoes,
    RelatorioConferenciaPrevisoes,
    RelatorioPrevisaoFutura,
    atualizar_previsoes_futuras,
    conferir_previsoes_pendentes,
    detalhar_previsao,
    listar_previsoes_configuracao,
    emitir_previsao_futura,
)
from .combinacoes_selecao_dezenas import (
    LIMITE_VOLUME_ELEVADO,
    ErroCombinacoesSelecao,
    PreviaCombinacoesSelecao,
    RelatorioPersistenciaCombinacoes,
    calcular_previa_combinacoes,
    exportar_combinacoes_csv,
    gerar_combinacoes_seis_dezenas,
    persistir_combinacoes_alvo,
)
from .inicializacao_screener_selecao import criar_dicionario_combinacoes
from .entradas_motor_screener import (
    adaptar_aplicacao_integral,
    adaptar_selecao_dezenas,
    adaptar_teste_5000,
)
from .solicitacao_screener_selecao import (
    ErroSolicitacaoScreenerSelecao,
    SolicitacaoScreenerSelecao,
)
from .dicionario_filtros_screener_selecao import (
    ErroDicionarioFiltrosScreener,
    montar_dicionario_filtros,
)
from .aplicacao_screener_selecao import aplicar_screener_selecao
from .configuracao_formacao_jogos import (
    ConfiguracaoFormacaoJogos,
    ErroConfiguracaoFormacaoJogos,
    MAXIMO_JOGOS,
)
from .motor_formacao_jogos import (
    AdaptadorCombinacao,
    ErroMotorFormacaoJogos,
    RelatorioGeracaoControlada,
    executar_geracao_controlada,
)
from .integracao_screener_formacao_jogos import (
    AdaptadorScreenerFormacao,
    PlanoScreenerFormacao,
    RelatorioScreenerFormacao,
    ResultadoIntegracaoScreener,
    executar_screener_formacao,
)
from .frequencia_historica import (
    ErroMotorFrequencia,
    FotografiaFrequencia,
    MotorFrequenciaAcumulada,
    calcular_fotografias_acumuladas,
)
from .carga_historico_frequencia import (
    ErroCargaHistoricoFrequencia,
    OperacaoFrequenciaCancelada,
    RelatorioCargaHistoricoFrequencia,
    assinatura_resultados,
    atualizar_historico_frequencia,
)
from .operacao_historico_frequencia import (
    CoordenadorOperacaoFrequencia,
    ExecucaoFrequenciaEmAndamento,
    MENSAGEM_CONFIRMACAO,
    PreviaOperacaoHistoricoFrequencia,
    RelatorioSimulacaoHistoricoFrequencia,
    preparar_operacao_historico_frequencia,
    simular_historico_frequencia,
)
from .gestao_desenvolvimento import (
    DadosManutencao,
    ErroGestaoDesenvolvimento,
)
from .catalogo_filtros_validacao_nova import (
    ErroCatalogoFiltrosValidacao,
    FiltroExecutavelValidacao,
    GrupoFiltrosValidacao,
    carregar_catalogo_filtros_validacao,
    montar_catalogo_filtros_validacao,
)
from .executor_filtros_validacao_nova import (
    ErroExecutorFiltroValidacao,
    ExecutorFiltroValidacao,
    carregar_executor_filtro_validacao,
    criar_executor_filtro_validacao,
)
from .processamento_validacao_nova import (
    ErroProcessamentoValidacaoNova,
    OperacaoValidacaoNovaCancelada,
    OcorrenciaFiltroValidacaoNova,
    RelatorioValidacaoNova,
    ResultadoFiltroValidacaoNova,
    processar_colecao_validacao_nova,
    processar_validacao_nova_no_banco,
)
from .teste_dirigido_validacao_nova import (
    ColecaoDirigidaValidacaoNova,
    ErroTesteDirigidoValidacaoNova,
    gerar_colecao_dirigida_no_banco,
    gerar_colecao_dirigida_validacao_nova,
)
from .desenho_ocorrencia_validacao_nova import (
    DesenhoOcorrenciaValidacao,
    SegmentoPainelValidacao,
    construir_desenho_ocorrencia_validacao,
    carregar_desenho_ocorrencia_validacao,
)

__all__ = [
    "RelatorioImportacaoBanco",
    "importar_planilha_no_banco",
    "salvar_relatorio_importacao",
    "editar_resultado",
    "incluir_resultado",
    "RelatorioRecalculoPadroes",
    "recalcular_padroes_iniciais",
    "RelatorioRecalculoGeometrico",
    "calcular_e_persistir_analise_geometrica",
    "recalcular_analises_geometricas",
    "ContagemClassificacao",
    "ClassePerfilPadrao",
    "ErroRecalculoClassificacao",
    "PerfilClassificacaoGrupo",
    "RelatorioRecalculoClassificacao",
    "calcular_perfil_grupo_sequenciais",
    "recalcular_classificacoes_grupo_sequenciais",
    "ErroJanelaHistorica",
    "JanelaHistorica",
    "selecionar_janela_historica",
    "ErroPerfilEstatistico",
    "FaixaPerfil",
    "PerfilEstatistico",
    "PontoDistribuicao",
    "calcular_faixa_desvio_padrao",
    "calcular_faixa_percentual_media",
    "calcular_perfil_estatistico",
    "PerfilParametroGeometrico",
    "PerfisGeometricos",
    "calcular_perfis_geometricos",
    "ClasseHistograma",
    "DistribuicaoVisual",
    "PontoCurvaNormal",
    "construir_distribuicao_visual",
    "SelecaoPadroesRaros",
    "selecionar_padroes_raros",
    "ExclusaoCriteriosNaoConfirmada",
    "ResultadoSincronizacaoCriterios",
    "sincronizar_criterios_validacao",
    "RelatorioPerfisOperacionais",
    "atualizar_perfis_operacionais_atuais",
    "marcar_perfis_operacionais_desatualizados",
    "RelatorioCargaAmostrasValidacao",
    "carregar_amostras_iniciais_validacao",
    "ErroReferenciaValidacao",
    "ReferenciaAprovada",
    "aprovar_referencia_categorica",
    "aprovar_referencia_numerica",
    "aprovar_referencia_padrao",
    "ErroExecucaoValidacao",
    "RelatorioExecucaoValidacao",
    "ResultadoExecucaoCriterio",
    "calcular_valor_criterio",
    "comparar_resultado_categorico",
    "comparar_resultado_padrao",
    "comparar_resultado_numerico",
    "executar_criterios_padroes",
    "executar_criterio_categorico",
    "executar_criterios_numericos",
    "RelatorioMotorValidacao",
    "atualizar_validacao_e_auditoria",
    "ConfiguracaoFrequencia",
    "DivergenciaConfiguracaoFrequencia",
    "comparar_configuracoes_frequencia",
    "configuracao_frequencia_inicial",
    "ConfiguracaoSelecaoDezenas",
    "configuracao_selecao_inicial",
    "AvaliacaoSelecaoDezena",
    "ErroSelecaoDezenas",
    "EstatisticaDezenaCorte",
    "ResultadoSelecaoDezenas",
    "selecionar_dezenas_para_alvo",
    "ClasseBacktest",
    "ErroBacktest",
    "PontoBacktest",
    "RelatorioBacktest",
    "ResumoBacktest",
    "executar_backtest",
    "resumir_pontos",
    "RelatorioAtualizacaoPrevisoes",
    "RelatorioConferenciaPrevisoes",
    "RelatorioPrevisaoFutura",
    "atualizar_previsoes_futuras",
    "conferir_previsoes_pendentes",
    "DetalhePrevisao",
    "detalhar_previsao",
    "listar_previsoes_configuracao",
    "emitir_previsao_futura",
    "LIMITE_VOLUME_ELEVADO",
    "ErroCombinacoesSelecao",
    "PreviaCombinacoesSelecao",
    "RelatorioPersistenciaCombinacoes",
    "calcular_previa_combinacoes",
    "exportar_combinacoes_csv",
    "gerar_combinacoes_seis_dezenas",
    "persistir_combinacoes_alvo",
    "criar_dicionario_combinacoes",
    "adaptar_aplicacao_integral",
    "adaptar_selecao_dezenas",
    "adaptar_teste_5000",
    "ErroSolicitacaoScreenerSelecao",
    "SolicitacaoScreenerSelecao",
    "ErroDicionarioFiltrosScreener",
    "montar_dicionario_filtros",
    "aplicar_screener_selecao",
    "ConfiguracaoFormacaoJogos",
    "ErroConfiguracaoFormacaoJogos",
    "MAXIMO_JOGOS",
    "AdaptadorCombinacao",
    "ErroMotorFormacaoJogos",
    "RelatorioGeracaoControlada",
    "executar_geracao_controlada",
    "AdaptadorScreenerFormacao",
    "PlanoScreenerFormacao",
    "RelatorioScreenerFormacao",
    "ResultadoIntegracaoScreener",
    "executar_screener_formacao",
    "ErroMotorFrequencia",
    "FotografiaFrequencia",
    "MotorFrequenciaAcumulada",
    "calcular_fotografias_acumuladas",
    "ErroCargaHistoricoFrequencia",
    "OperacaoFrequenciaCancelada",
    "RelatorioCargaHistoricoFrequencia",
    "assinatura_resultados",
    "atualizar_historico_frequencia",
    "CoordenadorOperacaoFrequencia",
    "ExecucaoFrequenciaEmAndamento",
    "MENSAGEM_CONFIRMACAO",
    "PreviaOperacaoHistoricoFrequencia",
    "RelatorioSimulacaoHistoricoFrequencia",
    "preparar_operacao_historico_frequencia",
    "simular_historico_frequencia",
    "DadosManutencao", "ErroGestaoDesenvolvimento",
    "FiltroExecutavelValidacao", "GrupoFiltrosValidacao",
    "ErroCatalogoFiltrosValidacao",
    "carregar_catalogo_filtros_validacao", "montar_catalogo_filtros_validacao",
    "ErroExecutorFiltroValidacao", "ExecutorFiltroValidacao",
    "carregar_executor_filtro_validacao", "criar_executor_filtro_validacao",
    "ErroProcessamentoValidacaoNova", "RelatorioValidacaoNova",
    "OperacaoValidacaoNovaCancelada",
    "OcorrenciaFiltroValidacaoNova",
    "ResultadoFiltroValidacaoNova", "processar_colecao_validacao_nova",
    "processar_validacao_nova_no_banco",
    "ColecaoDirigidaValidacaoNova", "ErroTesteDirigidoValidacaoNova",
    "gerar_colecao_dirigida_no_banco", "gerar_colecao_dirigida_validacao_nova",
    "DesenhoOcorrenciaValidacao", "SegmentoPainelValidacao",
    "construir_desenho_ocorrencia_validacao",
    "carregar_desenho_ocorrencia_validacao",
]
