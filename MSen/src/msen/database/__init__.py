"""Acesso controlado ao PostgreSQL."""

from .connection import ErroConexaoBanco, InformacaoConexao, abrir_conexao, verificar_conexao
from .migrations import (
    ErroMigracao,
    Migracao,
    RelatorioMigracoes,
    aplicar_migracoes,
    descobrir_migracoes,
    executar_migracoes,
)
from .grupos_padroes_repository import (
    ErroRepositorioGrupoPadrao,
    GrupoPadraoPersistido,
    RepositorioGruposPadroes,
)
from .padroes_repository import (
    ErroRepositorioPadrao,
    PadraoPersistido,
    RepositorioPadroes,
)
from .repositories import (
    ErroRepositorioResultado,
    RepositorioFrequencias,
    RepositorioResultados,
    ResultadoPersistido,
)
from .analise_geometrica_repository import (
    AnaliseGeometricaPersistida,
    RepositorioAnaliseGeometrica,
)
from .classificacoes_padrao_repository import RepositorioClassificacoesPadrao
from .validacao_repository import (
    AmostraValidacao,
    AvaliacaoValidacaoDetalhada,
    RepositorioValidacao,
)
from .configuracao_frequencia_repository import (
    ConfiguracaoFrequenciaPersistida,
    ErroRepositorioConfiguracaoFrequencia,
    RepositorioConfiguracaoFrequencia,
)

__all__ = [
    "ErroConexaoBanco", "InformacaoConexao", "abrir_conexao", "verificar_conexao",
    "ErroMigracao", "Migracao", "RelatorioMigracoes", "aplicar_migracoes",
    "descobrir_migracoes", "executar_migracoes",
    "ErroRepositorioGrupoPadrao", "GrupoPadraoPersistido",
    "RepositorioGruposPadroes",
    "ErroRepositorioResultado", "RepositorioFrequencias", "RepositorioResultados",
    "ResultadoPersistido",
    "ErroRepositorioPadrao", "PadraoPersistido", "RepositorioPadroes",
    "AnaliseGeometricaPersistida", "RepositorioAnaliseGeometrica",
    "RepositorioClassificacoesPadrao",
    "AmostraValidacao", "AvaliacaoValidacaoDetalhada", "RepositorioValidacao",
    "ConfiguracaoFrequenciaPersistida", "ErroRepositorioConfiguracaoFrequencia",
    "RepositorioConfiguracaoFrequencia",
]
