"""Contagem, geração e materialização autorizada de jogos de seis dezenas."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from itertools import combinations, islice
from math import comb
from typing import IO, Iterable, Iterator

import psycopg


QUANTIDADE_DEZENAS_JOGO = 6
LIMITE_VOLUME_ELEVADO = 10_000
TAMANHO_LOTE_INSERCAO = 2_000


class ErroCombinacoesSelecao(RuntimeError):
    def __init__(self, codigo: str, mensagem: str) -> None:
        super().__init__(mensagem)
        self.codigo = codigo


@dataclass(frozen=True, slots=True)
class PreviaCombinacoesSelecao:
    quantidade_dezenas: int
    quantidade_combinacoes: int
    volume_elevado: bool
    exige_confirmacao: bool


@dataclass(frozen=True, slots=True)
class RelatorioPersistenciaCombinacoes:
    id_lote_jogos: int
    id_alvo_selecao: int
    quantidade_combinacoes: int


def _normalizar_dezenas(dezenas: Iterable[int]) -> tuple[int, ...]:
    itens = tuple(dezenas)
    if any(isinstance(item, bool) or not isinstance(item, int) for item in itens):
        raise ValueError("As dezenas devem ser números inteiros.")
    ordenadas = tuple(sorted(itens))
    if len(ordenadas) != len(set(ordenadas)):
        raise ValueError("As dezenas não podem se repetir.")
    if any(item < 1 or item > 60 for item in ordenadas):
        raise ValueError("Cada dezena deve estar entre 1 e 60.")
    return ordenadas


def calcular_previa_combinacoes(
    dezenas: Iterable[int],
) -> PreviaCombinacoesSelecao:
    ordenadas = _normalizar_dezenas(dezenas)
    total = comb(len(ordenadas), QUANTIDADE_DEZENAS_JOGO) if len(ordenadas) >= 6 else 0
    elevado = total >= LIMITE_VOLUME_ELEVADO
    return PreviaCombinacoesSelecao(len(ordenadas), total, elevado, elevado)


def gerar_combinacoes_seis_dezenas(
    dezenas: Iterable[int],
) -> Iterator[tuple[int, int, int, int, int, int]]:
    """Gera combinações distintas em ordem lexicográfica, sem materializá-las."""
    ordenadas = _normalizar_dezenas(dezenas)
    return combinations(ordenadas, QUANTIDADE_DEZENAS_JOGO)


def _exigir_autorizacoes(
    previa: PreviaCombinacoesSelecao,
    *,
    autorizar_operacao: bool,
    confirmar_volume_elevado: bool,
) -> None:
    if previa.quantidade_combinacoes == 0:
        raise ErroCombinacoesSelecao(
            "DEZENAS_INSUFICIENTES",
            "São necessárias ao menos seis dezenas para formar um jogo.",
        )
    if not autorizar_operacao:
        raise ErroCombinacoesSelecao(
            "OPERACAO_NAO_AUTORIZADA",
            "A gravação ou exportação dos jogos precisa ser autorizada.",
        )
    if previa.volume_elevado and not confirmar_volume_elevado:
        raise ErroCombinacoesSelecao(
            "VOLUME_ELEVADO_NAO_CONFIRMADO",
            f"A operação produzirá {previa.quantidade_combinacoes:,} jogos e exige confirmação.",
        )


def exportar_combinacoes_csv(
    dezenas: Iterable[int],
    destino: IO[str],
    *,
    autorizar_exportacao: bool = False,
    confirmar_volume_elevado: bool = False,
) -> int:
    """Escreve CSV no destino fornecido somente após a autorização aplicável."""
    ordenadas = _normalizar_dezenas(dezenas)
    previa = calcular_previa_combinacoes(ordenadas)
    _exigir_autorizacoes(
        previa,
        autorizar_operacao=autorizar_exportacao,
        confirmar_volume_elevado=confirmar_volume_elevado,
    )
    escritor = csv.writer(destino, lineterminator="\n")
    escritor.writerow(("ordem", "dezena_1", "dezena_2", "dezena_3", "dezena_4", "dezena_5", "dezena_6"))
    for ordem, jogo in enumerate(gerar_combinacoes_seis_dezenas(ordenadas), 1):
        escritor.writerow((ordem, *jogo))
    return previa.quantidade_combinacoes


def _dezenas_retornadas_do_alvo(
    conexao: psycopg.Connection, id_alvo_selecao: int
) -> tuple[int, ...]:
    with conexao.cursor() as cursor:
        cursor.execute(
            "SELECT dezena FROM avaliacoes_dezenas_pesquisa "
            "WHERE id_alvo_selecao=%s AND retornada ORDER BY posicao_ranking",
            (id_alvo_selecao,),
        )
        dezenas = tuple(linha[0] for linha in cursor.fetchall())
    if not dezenas:
        raise ErroCombinacoesSelecao(
            "ALVO_SEM_DEZENAS",
            "O alvo não possui dezenas selecionadas para formar jogos.",
        )
    return dezenas


def persistir_combinacoes_alvo(
    conexao: psycopg.Connection,
    id_alvo_selecao: int,
    *,
    autorizar_persistencia: bool = False,
    confirmar_volume_elevado: bool = False,
) -> RelatorioPersistenciaCombinacoes:
    """Persiste um lote completo, atômico e vinculado à pesquisa do alvo."""
    if not isinstance(conexao, psycopg.Connection):
        raise TypeError("A persistência exige uma conexão Psycopg válida.")
    if isinstance(id_alvo_selecao, bool) or not isinstance(id_alvo_selecao, int) or id_alvo_selecao <= 0:
        raise ValueError("id_alvo_selecao deve ser um inteiro positivo.")
    dezenas = _dezenas_retornadas_do_alvo(conexao, id_alvo_selecao)
    previa = calcular_previa_combinacoes(dezenas)
    _exigir_autorizacoes(
        previa,
        autorizar_operacao=autorizar_persistencia,
        confirmar_volume_elevado=confirmar_volume_elevado,
    )
    try:
        with conexao.transaction():
            with conexao.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO lotes_jogos_selecao "
                    "(id_alvo_selecao,quantidade_dezenas,quantidade_combinacoes) "
                    "VALUES (%s,%s,%s) RETURNING id_lote_jogos",
                    (id_alvo_selecao, len(dezenas), previa.quantidade_combinacoes),
                )
                id_lote = cursor.fetchone()[0]
                iterador = enumerate(gerar_combinacoes_seis_dezenas(dezenas), 1)
                while lote := tuple(islice(iterador, TAMANHO_LOTE_INSERCAO)):
                    cursor.executemany(
                        "INSERT INTO jogos_selecao_dezenas "
                        "(id_lote_jogos,ordem,dezena_1,dezena_2,dezena_3,dezena_4,dezena_5,dezena_6) "
                        "VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
                        ((id_lote, ordem, *jogo) for ordem, jogo in lote),
                    )
                cursor.execute(
                    "UPDATE lotes_jogos_selecao SET estado='CONCLUIDO',"
                    "concluido_em=CURRENT_TIMESTAMP WHERE id_lote_jogos=%s",
                    (id_lote,),
                )
    except psycopg.errors.ForeignKeyViolation as erro:
        raise ErroCombinacoesSelecao(
            "ALVO_NAO_ENCONTRADO", "O alvo informado não existe."
        ) from erro
    return RelatorioPersistenciaCombinacoes(
        id_lote, id_alvo_selecao, previa.quantidade_combinacoes
    )
