"""Emissão imutável e conferência posterior das previsões de dezenas."""

from __future__ import annotations

from dataclasses import dataclass

import psycopg

from msen.database.fonte_selecao_dezenas_repository import RepositorioFonteSelecaoDezenas
from msen.database.pesquisa_selecao_repository import (
    AlvoPesquisaEntrada,
    RepositorioPesquisaSelecao,
)

from .backtest_selecao_dezenas import (
    _converter_avaliacao,
    _listar_resultados_ate,
)
from .carga_historico_frequencia import assinatura_resultados
from .configuracao_selecao_dezenas import ConfiguracaoSelecaoDezenas
from .selecao_dezenas import selecionar_dezenas_para_alvo


@dataclass(frozen=True, slots=True)
class RelatorioPrevisaoFutura:
    id_execucao_selecao: int
    concurso_corte: int
    concurso_alvo_inicial: int
    concurso_alvo_final: int
    alvos_criados_agora: int
    alvos_ja_existentes: int
    estado: str


@dataclass(frozen=True, slots=True)
class RelatorioConferenciaPrevisoes:
    previsoes_conferidas: int
    execucoes_afetadas: tuple[int, ...]


@dataclass(frozen=True, slots=True)
class RelatorioAtualizacaoPrevisoes:
    conferencia: RelatorioConferenciaPrevisoes
    nova_previsao: RelatorioPrevisaoFutura


def emitir_previsao_futura(
    conexao: psycopg.Connection,
    configuracao: ConfiguracaoSelecaoDezenas,
) -> RelatorioPrevisaoFutura:
    """Congela o horizonte posterior ao último resultado conhecido."""
    if not isinstance(conexao, psycopg.Connection):
        raise TypeError("conexao deve ser Psycopg Connection.")
    with conexao.transaction():
        with conexao.cursor() as cursor:
            cursor.execute("SELECT MAX(numero_ap) FROM resultados")
            corte = cursor.fetchone()[0]
    if corte is None:
        raise ValueError("Não existem resultados para originar uma previsão.")

    origem = _listar_resultados_ate(conexao, corte)
    assinatura = assinatura_resultados(origem)
    inicio = corte + 1
    final = corte + configuracao.horizonte_concursos
    repositorio = RepositorioPesquisaSelecao(conexao)
    fonte = RepositorioFonteSelecaoDezenas(conexao)
    config_persistida = repositorio.criar_ou_buscar_configuracao(configuracao)
    execucao = repositorio.criar_ou_buscar_execucao(
        config_persistida,
        tipo_execucao="PREVISAO_FUTURA",
        assinatura_resultados=assinatura,
        concurso_corte_origem=corte,
        concurso_alvo_inicial=inicio,
        concurso_alvo_final=final,
    )
    existentes = repositorio.alvos_ja_persistidos(execucao.id_execucao_selecao)
    estado = repositorio.iniciar_ou_retomar_execucao(execucao.id_execucao_selecao)
    if estado == "CONCLUIDA":
        return RelatorioPrevisaoFutura(
            execucao.id_execucao_selecao, corte, inicio, final, 0, len(existentes), estado
        )

    estatisticas = fonte.carregar_estatisticas_corte(corte)
    criados = 0
    try:
        for alvo in range(inicio, final + 1):
            if alvo in existentes:
                continue
            selecao = selecionar_dezenas_para_alvo(
                estatisticas,
                configuracao,
                numero_concurso_alvo=alvo,
                numero_concurso_corte=corte,
            )
            repositorio.salvar_alvo(
                execucao.id_execucao_selecao,
                AlvoPesquisaEntrada(
                    numero_concurso_alvo=alvo,
                    numero_concurso_corte=corte,
                    id_resultado=None,
                    situacao="PENDENTE" if selecao.avaliavel else "NAO_AVALIAVEL",
                    quantidade_configurada=selecao.quantidade_configurada,
                    quantidade_acertos=None,
                    motivo=selecao.motivo,
                ),
                tuple(_converter_avaliacao(item) for item in selecao.avaliacoes),
            )
            criados += 1
        repositorio.concluir_execucao(execucao.id_execucao_selecao)
    except Exception as erro:
        repositorio.registrar_falha(
            execucao.id_execucao_selecao,
            getattr(erro, "codigo", "FALHA_PREVISAO"),
            str(erro),
        )
        raise
    return RelatorioPrevisaoFutura(
        execucao.id_execucao_selecao,
        corte,
        inicio,
        final,
        criados,
        len(existentes),
        repositorio.estado_execucao(execucao.id_execucao_selecao),
    )


def conferir_previsoes_pendentes(
    conexao: psycopg.Connection,
) -> RelatorioConferenciaPrevisoes:
    """Confere previsões congeladas; não recalcula suas dezenas ou faixas."""
    afetadas: set[int] = set()
    conferidas = 0
    while True:
        with conexao.transaction():
            with conexao.cursor() as cursor:
                cursor.execute(
                    "WITH candidato AS ("
                    "SELECT a.id_alvo_selecao FROM alvos_pesquisa_selecao a "
                    "JOIN execucoes_pesquisa_selecao e "
                    "ON e.id_execucao_selecao=a.id_execucao_selecao "
                    "JOIN resultados r ON r.numero_ap=a.numero_concurso_alvo "
                    "WHERE e.tipo_execucao='PREVISAO_FUTURA' "
                    "AND a.situacao='PENDENTE' "
                    "ORDER BY a.numero_concurso_alvo LIMIT 1 "
                    "FOR UPDATE OF a SKIP LOCKED) "
                    "SELECT a.id_alvo_selecao,a.id_execucao_selecao,r.id_resultado,"
                    "ARRAY[r.res_01,r.res_02,r.res_03,r.res_04,r.res_05,r.res_06],"
                    "COALESCE(ARRAY_AGG(d.dezena ORDER BY d.dezena) "
                    "FILTER (WHERE d.retornada),ARRAY[]::SMALLINT[]) "
                    "FROM alvos_pesquisa_selecao a "
                    "JOIN candidato c ON c.id_alvo_selecao=a.id_alvo_selecao "
                    "JOIN execucoes_pesquisa_selecao e "
                    "ON e.id_execucao_selecao=a.id_execucao_selecao "
                    "JOIN resultados r ON r.numero_ap=a.numero_concurso_alvo "
                    "LEFT JOIN avaliacoes_dezenas_pesquisa d "
                    "ON d.id_alvo_selecao=a.id_alvo_selecao "
                    "WHERE e.tipo_execucao='PREVISAO_FUTURA' "
                    "AND a.situacao='PENDENTE' "
                    "GROUP BY a.id_alvo_selecao,e.id_execucao_selecao,r.id_resultado"
                )
                linha = cursor.fetchone()
                if linha is None:
                    break
                acertos = len(set(linha[3]) & set(linha[4]))
                cursor.execute(
                    "UPDATE alvos_pesquisa_selecao SET situacao='AVALIADO',"
                    "id_resultado=%s,quantidade_acertos=%s,classe_acerto=%s,"
                    "conferido_em=CURRENT_TIMESTAMP "
                    "WHERE id_alvo_selecao=%s AND situacao='PENDENTE'",
                    (linha[2], acertos, acertos, linha[0]),
                )
                if cursor.rowcount == 1:
                    conferidas += 1
                    afetadas.add(linha[1])
    return RelatorioConferenciaPrevisoes(conferidas, tuple(sorted(afetadas)))


def atualizar_previsoes_futuras(
    conexao: psycopg.Connection,
    configuracao: ConfiguracaoSelecaoDezenas,
) -> RelatorioAtualizacaoPrevisoes:
    conferencia = conferir_previsoes_pendentes(conexao)
    nova = emitir_previsao_futura(conexao, configuracao)
    return RelatorioAtualizacaoPrevisoes(conferencia, nova)
