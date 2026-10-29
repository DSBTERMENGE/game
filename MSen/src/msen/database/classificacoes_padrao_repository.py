"""Persistência das classificações dos resultados por grupo de padrões."""

from typing import Any

import psycopg

from msen.modelos import (
    ClassificacaoPadrao,
    validar_classificacao,
)


COLUNAS_CLASSIFICACAO = (
    "id_classificacao, id_resultado, id_grupo, id_padrao, "
    "versao_calculo, calculado_em"
)


def _linha_para_classificacao(linha: tuple[Any, ...]) -> ClassificacaoPadrao:
    """Converte as seis colunas do PostgreSQL para o modelo imutável."""

    if len(linha) != 6:
        raise ValueError("A consulta de classificação deve retornar exatamente 6 colunas.")
    return ClassificacaoPadrao(
        id_classificacao=linha[0],
        id_resultado=linha[1],
        id_grupo=linha[2],
        id_padrao=linha[3],
        versao_calculo=linha[4],
        calculado_em=linha[5],
    )


def _id_positivo(nome: str, valor: int) -> int:
    """Valida um identificador usado isoladamente em consultas."""

    if isinstance(valor, bool) or not isinstance(valor, int):
        raise TypeError(f"{nome} deve ser inteiro.")
    if valor <= 0:
        raise ValueError(f"{nome} deve ser positivo.")
    return valor


class RepositorioClassificacoesPadrao:
    """Grava e consulta uma classificação por resultado e grupo."""

    def __init__(self, conexao: psycopg.Connection) -> None:
        """Associa o repositório a uma conexão Psycopg válida."""

        if not isinstance(conexao, psycopg.Connection):
            raise TypeError("O repositório exige uma conexão Psycopg válida.")
        self._conexao = conexao

    def salvar(
        self,
        id_resultado: int,
        id_grupo: int,
        *,
        id_padrao: int,
        versao_calculo: int = 1,
    ) -> ClassificacaoPadrao:
        """Insere ou atualiza atomicamente a classificação do resultado/grupo.

        Um recálculo preserva `id_classificacao` e atualiza padrão, versão e
        data do cálculo.
        """

        validar_classificacao(id_resultado, id_grupo, id_padrao, versao_calculo)
        with self._conexao.cursor() as cursor:
            cursor.execute(
                "INSERT INTO resultado_classificacao_padrao "
                "(id_resultado, id_grupo, id_padrao, versao_calculo) "
                "VALUES (%s, %s, %s, %s) "
                "ON CONFLICT (id_resultado, id_grupo) DO UPDATE SET "
                "id_padrao = EXCLUDED.id_padrao, "
                "versao_calculo = EXCLUDED.versao_calculo, "
                "calculado_em = CURRENT_TIMESTAMP "
                f"RETURNING {COLUNAS_CLASSIFICACAO}",
                (id_resultado, id_grupo, id_padrao, versao_calculo),
            )
            return _linha_para_classificacao(cursor.fetchone())

    def listar_por_resultado(self, id_resultado: int) -> tuple[ClassificacaoPadrao, ...]:
        """Lista as classificações do resultado em ordem de grupo."""

        _id_positivo("id_resultado", id_resultado)
        with self._conexao.cursor() as cursor:
            cursor.execute(
                f"SELECT {COLUNAS_CLASSIFICACAO} "
                "FROM resultado_classificacao_padrao "
                "WHERE id_resultado = %s ORDER BY id_grupo",
                (id_resultado,),
            )
            return tuple(_linha_para_classificacao(linha) for linha in cursor.fetchall())

    def listar_por_grupo(self, id_grupo: int) -> tuple[ClassificacaoPadrao, ...]:
        """Lista as classificações do grupo em ordem de resultado."""

        _id_positivo("id_grupo", id_grupo)
        with self._conexao.cursor() as cursor:
            cursor.execute(
                f"SELECT {COLUNAS_CLASSIFICACAO} "
                "FROM resultado_classificacao_padrao "
                "WHERE id_grupo = %s ORDER BY id_resultado",
                (id_grupo,),
            )
            return tuple(_linha_para_classificacao(linha) for linha in cursor.fetchall())

    def excluir_por_grupo(self, id_grupo: int) -> int:
        """Remove a fotografia anterior do grupo antes do recálculo completo."""

        _id_positivo("id_grupo", id_grupo)
        with self._conexao.cursor() as cursor:
            cursor.execute(
                "DELETE FROM resultado_classificacao_padrao WHERE id_grupo = %s",
                (id_grupo,),
            )
            return cursor.rowcount

    def excluir_nao_identificados(
        self, id_grupo: int, ids_resultados_identificados: tuple[int, ...]
    ) -> int:
        """Remove somente linhas antigas que não correspondem mais a padrão."""

        _id_positivo("id_grupo", id_grupo)
        if not isinstance(ids_resultados_identificados, tuple):
            raise TypeError("ids_resultados_identificados deve ser uma tupla.")
        for identificador in ids_resultados_identificados:
            _id_positivo("id_resultado", identificador)
        with self._conexao.cursor() as cursor:
            if ids_resultados_identificados:
                cursor.execute(
                    "DELETE FROM resultado_classificacao_padrao "
                    "WHERE id_grupo = %s AND NOT (id_resultado = ANY(%s))",
                    (id_grupo, list(ids_resultados_identificados)),
                )
            else:
                cursor.execute(
                    "DELETE FROM resultado_classificacao_padrao WHERE id_grupo = %s",
                    (id_grupo,),
                )
            return cursor.rowcount
