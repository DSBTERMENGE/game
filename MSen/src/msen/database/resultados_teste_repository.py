"""Persistência atômica da coleção fixa de combinações para testes."""

from collections.abc import Iterable
from dataclasses import dataclass

import psycopg

from msen.validacao import CombinacaoTeste, chave_canonica


QUANTIDADE_COLECAO_FIXA = 1_000


class ErroRepositorioResultadosTeste(RuntimeError):
    def __init__(self, codigo: str, mensagem: str) -> None:
        super().__init__(mensagem)
        self.codigo = codigo


@dataclass(frozen=True, slots=True)
class ColecaoResultadosTesteGravada:
    quantidade: int


def _validar_colecao(
    combinacoes: Iterable[CombinacaoTeste],
) -> tuple[CombinacaoTeste, ...]:
    colecao = tuple(tuple(item) for item in combinacoes)
    if len(colecao) != QUANTIDADE_COLECAO_FIXA:
        raise ErroRepositorioResultadosTeste(
            "QUANTIDADE_INVALIDA",
            "A coleção fixa deve conter exatamente 1.000 combinações.",
        )

    chaves = tuple(chave_canonica(item) for item in colecao)
    if len(set(chaves)) != QUANTIDADE_COLECAO_FIXA:
        raise ErroRepositorioResultadosTeste(
            "COMBINACAO_REPETIDA",
            "A coleção contém combinações equivalentes por permutação.",
        )
    return colecao  # type: ignore[return-value]


class RepositorioResultadosTeste:
    def __init__(self, conexao: psycopg.Connection) -> None:
        if not isinstance(conexao, psycopg.Connection):
            raise TypeError("O repositório exige uma conexão Psycopg válida.")
        self._conexao = conexao

    def gravar_colecao_fixa(
        self, combinacoes: Iterable[CombinacaoTeste]
    ) -> ColecaoResultadosTesteGravada:
        """Grava as 1.000 combinações em uma transação ou não grava nenhuma."""

        colecao = _validar_colecao(combinacoes)
        with self._conexao.transaction(), self._conexao.cursor() as cursor:
            cursor.execute("LOCK TABLE resultados_teste IN EXCLUSIVE MODE")
            cursor.execute("SELECT count(*) FROM resultados_teste")
            quantidade_atual = cursor.fetchone()[0]
            if quantidade_atual != 0:
                raise ErroRepositorioResultadosTeste(
                    "COLECAO_JA_EXISTENTE",
                    "A tabela de resultados de teste já contém uma coleção fixa.",
                )

            cursor.executemany(
                "INSERT INTO resultados_teste "
                "(res_01,res_02,res_03,res_04,res_05,res_06) "
                "VALUES (%s,%s,%s,%s,%s,%s)",
                colecao,
            )
            cursor.execute("SELECT count(*) FROM resultados_teste")
            quantidade_final = cursor.fetchone()[0]
            if quantidade_final != QUANTIDADE_COLECAO_FIXA:
                raise ErroRepositorioResultadosTeste(
                    "GRAVACAO_INCOMPLETA",
                    "A transação não produziu exatamente 1.000 registros.",
                )

        return ColecaoResultadosTesteGravada(quantidade=quantidade_final)

    def listar_colecao_fixa(self) -> tuple[CombinacaoTeste, ...]:
        """Lê a coleção fixa preservando a ordem original de cada combinação."""

        try:
            with self._conexao.transaction(), self._conexao.cursor() as cursor:
                cursor.execute(
                    "SELECT res_01,res_02,res_03,res_04,res_05,res_06 "
                    "FROM resultados_teste ORDER BY id_resultado_teste"
                )
                colecao = tuple(tuple(linha) for linha in cursor.fetchall())
        except psycopg.Error as erro:
            raise ErroRepositorioResultadosTeste(
                "FALHA_LEITURA",
                "Não foi possível ler a coleção fixa de resultados de teste.",
            ) from erro
        if len(colecao) != QUANTIDADE_COLECAO_FIXA:
            raise ErroRepositorioResultadosTeste(
                "COLECAO_INCOMPLETA",
                "A coleção fixa deve conter exatamente 1.000 combinações.",
            )
        return colecao  # type: ignore[return-value]
