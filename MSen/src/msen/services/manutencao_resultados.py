"""Inclusão e edição atômica de um resultado individual."""

from __future__ import annotations

import psycopg

from msen.calculos import ResultadoCalculado, calcular_frequencias, calcular_resultado
from msen.database import RepositorioFrequencias, RepositorioResultados, ResultadoPersistido
from msen.modelos import ResultadoEntrada

from .padroes import recalcular_padroes_iniciais


def _como_entrada(resultado: ResultadoCalculado) -> ResultadoEntrada:
    return ResultadoEntrada(
        data_resultado=resultado.data_resultado,
        numero_ap=resultado.numero_ap,
        res_01=resultado.res_01,
        res_02=resultado.res_02,
        res_03=resultado.res_03,
        res_04=resultado.res_04,
        res_05=resultado.res_05,
        res_06=resultado.res_06,
    )


def _atualizar_frequencias(
    conexao: psycopg.Connection, repositorio: RepositorioResultados
) -> None:
    historico = repositorio.listar(limite=10_000)
    frequencias = calcular_frequencias(
        _como_entrada(item.resultado) for item in historico
    )
    RepositorioFrequencias(conexao).atualizar_todas(frequencias)


def incluir_resultado(
    conexao: psycopg.Connection, entrada: ResultadoEntrada
) -> ResultadoPersistido:
    """Calcula, insere e atualiza frequências e padrões na mesma transação."""

    repositorio = RepositorioResultados(conexao)
    with conexao.transaction():
        persistido = repositorio.inserir(calcular_resultado(entrada))
        _atualizar_frequencias(conexao, repositorio)
        recalcular_padroes_iniciais(conexao)
    return persistido


def editar_resultado(
    conexao: psycopg.Connection, entrada: ResultadoEntrada
) -> ResultadoPersistido:
    """Recalcula, atualiza e refaz frequências e padrões na mesma transação."""

    repositorio = RepositorioResultados(conexao)
    with conexao.transaction():
        persistido = repositorio.atualizar(entrada)
        _atualizar_frequencias(conexao, repositorio)
        recalcular_padroes_iniciais(conexao)
    return persistido
