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
from .repositories import (
    ErroRepositorioResultado,
    RepositorioFrequencias,
    RepositorioResultados,
    ResultadoPersistido,
)

__all__ = [
    "ErroConexaoBanco", "InformacaoConexao", "abrir_conexao", "verificar_conexao",
    "ErroMigracao", "Migracao", "RelatorioMigracoes", "aplicar_migracoes",
    "descobrir_migracoes", "executar_migracoes",
    "ErroRepositorioResultado", "RepositorioFrequencias", "RepositorioResultados",
    "ResultadoPersistido",
]
