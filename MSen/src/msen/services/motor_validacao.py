"""Orquestra sincronização, recálculo e comparação da homologação."""

from dataclasses import dataclass
from collections.abc import Callable

import psycopg

from msen.validacao import criar_registro_criterios_producao

from .execucao_validacao import (
    RelatorioExecucaoValidacao, executar_criterios_numericos,
    executar_criterios_padroes,
)
from .sincronizacao_validacao import (
    ResultadoSincronizacaoCriterios, sincronizar_criterios_validacao,
)


@dataclass(frozen=True, slots=True)
class RelatorioMotorValidacao:
    sincronizacao: ResultadoSincronizacaoCriterios
    categorias: tuple[RelatorioExecucaoValidacao, ...]
    total_criterios: int
    total_avaliacoes: int
    aprovadas: int
    reprovadas: int
    pendentes: int
    criterios_aprovados: int
    criterios_reprovados: int
    criterios_pendentes: int
    homologacao_concluida: bool
    motivo_estado_global: str


def _motivo_global(*, reprovadas: int, pendentes: int) -> str:
    if pendentes:
        return "REFERENCIAS_PENDENTES"
    if reprovadas:
        return "CRITERIOS_REPROVADOS"
    return "HOMOLOGACAO_CONCLUIDA_AGUARDANDO_COBERTURA"


def atualizar_validacao_e_auditoria(
    conexao: psycopg.Connection, *, confirmar_exclusoes: bool = False,
    informar_progresso: Callable[[str, int, int], None] | None = None,
) -> RelatorioMotorValidacao:
    """Executa o ciclo completo sem fabricar referências nem liberar cobertura."""

    if not isinstance(conexao, psycopg.Connection):
        raise TypeError("O motor exige uma conexão Psycopg válida.")
    if not isinstance(confirmar_exclusoes, bool):
        raise TypeError("confirmar_exclusoes deve ser booleano.")
    if informar_progresso is not None and not callable(informar_progresso):
        raise TypeError("informar_progresso deve ser chamável ou nulo.")
    progresso = informar_progresso or (lambda _etapa, _concluido, _total: None)
    progresso("Sincronizando catálogo", 0, 4)
    with conexao.transaction():
        sincronizacao = sincronizar_criterios_validacao(
            conexao, criar_registro_criterios_producao(),
            confirmar_exclusoes=confirmar_exclusoes,
        )
        progresso("Executando critérios estatísticos", 1, 4)
        categorias = (
            executar_criterios_numericos(
                conexao, categoria="ESTATISTICA",
                permitir_referencias_pendentes=True,
            ),
        )
        progresso("Executando critérios geométricos", 2, 4)
        categorias += (
            executar_criterios_numericos(
                conexao, categoria="GEOMETRIA",
                permitir_referencias_pendentes=True,
            ),
        )
        progresso("Executando detectores de padrões", 3, 4)
        categorias += (
            executar_criterios_padroes(
                conexao, permitir_referencias_pendentes=True,
            ),
        )
        total_avaliacoes = sum(item.total_avaliacoes for item in categorias)
        aprovadas = sum(item.aprovadas for item in categorias)
        reprovadas = sum(item.reprovadas for item in categorias)
        pendentes = total_avaliacoes - aprovadas - reprovadas
        criterios = tuple(
            criterio for categoria in categorias for criterio in categoria.criterios
        )
        criterios_aprovados = sum(item.estado == "APROVADO" for item in criterios)
        criterios_reprovados = sum(item.estado == "REPROVADO" for item in criterios)
        criterios_pendentes = sum(item.estado == "PENDENTE" for item in criterios)
        motivo = _motivo_global(reprovadas=reprovadas, pendentes=pendentes)
        with conexao.cursor() as cursor:
            cursor.execute(
                "UPDATE estado_algoritmo_selecao SET atualizado = FALSE, motivo = %s, "
                "alterado_em = CURRENT_TIMESTAMP WHERE id_estado = 1",
                (motivo,),
            )
        progresso("Consolidação concluída", 4, 4)
    return RelatorioMotorValidacao(
        sincronizacao=sincronizacao, categorias=categorias,
        total_criterios=len(criterios), total_avaliacoes=total_avaliacoes,
        aprovadas=aprovadas, reprovadas=reprovadas, pendentes=pendentes,
        criterios_aprovados=criterios_aprovados,
        criterios_reprovados=criterios_reprovados,
        criterios_pendentes=criterios_pendentes,
        homologacao_concluida=not reprovadas and not pendentes,
        motivo_estado_global=motivo,
    )
