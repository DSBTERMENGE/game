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
    aprovar_referencia_numerica,
    aprovar_referencia_padrao,
)
from .execucao_validacao import (
    ErroExecucaoValidacao,
    RelatorioExecucaoValidacao,
    ResultadoExecucaoCriterio,
    calcular_valor_criterio,
    comparar_resultado_padrao,
    comparar_resultado_numerico,
    executar_criterios_padroes,
    executar_criterios_numericos,
)
from .motor_validacao import RelatorioMotorValidacao, atualizar_validacao_e_auditoria
from .configuracao_frequencia import (
    ConfiguracaoFrequencia,
    DivergenciaConfiguracaoFrequencia,
    comparar_configuracoes_frequencia,
    configuracao_frequencia_inicial,
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
    "aprovar_referencia_numerica",
    "aprovar_referencia_padrao",
    "ErroExecucaoValidacao",
    "RelatorioExecucaoValidacao",
    "ResultadoExecucaoCriterio",
    "calcular_valor_criterio",
    "comparar_resultado_padrao",
    "comparar_resultado_numerico",
    "executar_criterios_padroes",
    "executar_criterios_numericos",
    "RelatorioMotorValidacao",
    "atualizar_validacao_e_auditoria",
    "ConfiguracaoFrequencia",
    "DivergenciaConfiguracaoFrequencia",
    "comparar_configuracoes_frequencia",
    "configuracao_frequencia_inicial",
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
]
