"""Caso de uso atômico para cadastrar e recalcular os padrões iniciais."""

from dataclasses import dataclass

import psycopg

from msen.calculos import ResultadoCalculado
from msen.database import RepositorioPadroes, RepositorioResultados
from msen.database.padroes_repository import PadraoPersistido
from msen.modelos import ResultadoEntrada
from msen.padroes import (
    calcular_estatisticas_mesma_coluna,
    calcular_estatisticas_mesma_linha,
    calcular_estatisticas_sequenciais,
)


@dataclass(frozen=True, slots=True)
class RelatorioRecalculoPadroes:
    """Resume quantos resultados foram analisados e os padrões atualizados."""

    resultados_analisados: int
    padroes: tuple[PadraoPersistido, ...]


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


def recalcular_padroes_iniciais(
    conexao: psycopg.Connection,
) -> RelatorioRecalculoPadroes:
    """Recalcula os padrões cadastrados que possuem detector implementado.

    Parâmetros:
        conexao: Conexão Psycopg aberta para o database confirmado.

    Retorno:
        Quantidade de resultados analisados e todas as linhas cadastradas.

    Regra:
        Cadastros ausentes não são recriados, respeitando exclusões do usuário.
        Cadastros sem detector permanecem com estatísticas nulas. Somente
        estatísticas calculadas pelo Python são gravadas e qualquer falha desfaz
        toda a operação.
    """

    if not isinstance(conexao, psycopg.Connection):
        raise TypeError("O recálculo exige uma conexão Psycopg válida.")

    repositorio_resultados = RepositorioResultados(conexao)
    repositorio_padroes = RepositorioPadroes(conexao)
    with conexao.transaction():
        resultados = repositorio_resultados.listar(limite=10_000)
        serie = tuple(_como_entrada(item.resultado) for item in resultados)
        calculadas = (
            *calcular_estatisticas_sequenciais(serie),
            *calcular_estatisticas_mesma_coluna(serie),
            *calcular_estatisticas_mesma_linha(serie),
        )
        estatisticas = {item.padrao_cod: item for item in calculadas}
        cadastrados = repositorio_padroes.listar()
        for padrao in cadastrados:
            estatistica = estatisticas.get(padrao.padrao_cod)
            if estatistica is not None:
                repositorio_padroes.atualizar_estatistica(
                    estatistica, len(resultados)
                )
        atualizados = repositorio_padroes.listar()

    return RelatorioRecalculoPadroes(
        resultados_analisados=len(resultados),
        padroes=atualizados,
    )
