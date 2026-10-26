"""Persistência PostgreSQL dos resultados, sem dependência da interface."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

import psycopg

from msen.calculos import FrequenciaResultado, ResultadoCalculado, calcular_resultado
from msen.modelos import ResultadoEntrada


COLUNAS_RESULTADO = """
id_resultado, data_resultado, numero_ap,
res_01, res_02, res_03, res_04, res_05, res_06,
soma_res, media_aritmetica_res, mediana_res, desvio_padrao_media,
media_coordenada_x, media_coordenada_y, versao_calculo,
criado_em, atualizado_em
"""


class ErroRepositorioResultado(RuntimeError):
    def __init__(self, codigo: str, mensagem: str, *, numero_ap: int | None = None) -> None:
        super().__init__(mensagem)
        self.codigo = codigo
        self.numero_ap = numero_ap


@dataclass(frozen=True, slots=True)
class ResultadoPersistido:
    id_resultado: int
    resultado: ResultadoCalculado
    criado_em: datetime
    atualizado_em: datetime

    @property
    def numero_ap(self) -> int:
        return self.resultado.numero_ap


def _linha_para_resultado(linha: tuple[Any, ...]) -> ResultadoPersistido:
    if len(linha) != 18:
        raise ValueError("A consulta de resultado deve retornar exatamente 18 colunas.")
    calculado = ResultadoCalculado(
        data_resultado=linha[1], numero_ap=linha[2],
        res_01=linha[3], res_02=linha[4], res_03=linha[5],
        res_04=linha[6], res_05=linha[7], res_06=linha[8],
        soma_res=linha[9], media_aritmetica_res=linha[10],
        mediana_res=linha[11], desvio_padrao_media=linha[12],
        media_coordenada_x=linha[13], media_coordenada_y=linha[14],
        versao_calculo=linha[15],
    )
    return ResultadoPersistido(linha[0], calculado, linha[16], linha[17])


def _parametros(resultado: ResultadoCalculado) -> tuple[Any, ...]:
    return (
        resultado.data_resultado, resultado.numero_ap,
        resultado.res_01, resultado.res_02, resultado.res_03,
        resultado.res_04, resultado.res_05, resultado.res_06,
        resultado.soma_res, resultado.media_aritmetica_res,
        resultado.mediana_res, resultado.desvio_padrao_media,
        resultado.media_coordenada_x, resultado.media_coordenada_y,
        resultado.versao_calculo,
    )


class RepositorioResultados:
    """Operações atômicas da tabela `resultados`."""

    def __init__(self, conexao: psycopg.Connection) -> None:
        if not isinstance(conexao, psycopg.Connection):
            raise TypeError("O repositório exige uma conexão Psycopg válida.")
        self._conexao = conexao

    def inserir(self, resultado: ResultadoCalculado) -> ResultadoPersistido:
        if not isinstance(resultado, ResultadoCalculado):
            raise TypeError("A inserção exige um ResultadoCalculado.")
        sql = f"""
            INSERT INTO resultados (
                data_resultado, numero_ap,
                res_01, res_02, res_03, res_04, res_05, res_06,
                soma_res, media_aritmetica_res, mediana_res,
                desvio_padrao_media, media_coordenada_x, media_coordenada_y,
                versao_calculo
            ) VALUES ({", ".join(["%s"] * 15)})
            RETURNING {COLUNAS_RESULTADO}
        """
        try:
            with self._conexao.transaction():
                with self._conexao.cursor() as cursor:
                    cursor.execute(sql, _parametros(resultado))
                    return _linha_para_resultado(cursor.fetchone())
        except psycopg.errors.UniqueViolation:
            raise ErroRepositorioResultado(
                "RESULTADO_DUPLICADO",
                f"O concurso {resultado.numero_ap} já está cadastrado.",
                numero_ap=resultado.numero_ap,
            ) from None
        except psycopg.Error:
            raise ErroRepositorioResultado(
                "FALHA_INSERCAO", "Não foi possível inserir o resultado.",
                numero_ap=resultado.numero_ap,
            ) from None

    def buscar_por_numero_ap(self, numero_ap: int) -> ResultadoPersistido | None:
        if isinstance(numero_ap, bool) or not isinstance(numero_ap, int) or numero_ap < 1:
            raise ValueError("O número do concurso deve ser um inteiro positivo.")
        try:
            with self._conexao.transaction():
                with self._conexao.cursor() as cursor:
                    cursor.execute(
                        f"SELECT {COLUNAS_RESULTADO} FROM resultados WHERE numero_ap = %s",
                        (numero_ap,),
                    )
                    linha = cursor.fetchone()
                    return None if linha is None else _linha_para_resultado(linha)
        except psycopg.Error:
            raise ErroRepositorioResultado(
                "FALHA_BUSCA", "Não foi possível buscar o resultado.", numero_ap=numero_ap,
            ) from None

    def listar(self, *, limite: int = 100, deslocamento: int = 0) -> tuple[ResultadoPersistido, ...]:
        if isinstance(limite, bool) or not isinstance(limite, int) or not 1 <= limite <= 10_000:
            raise ValueError("O limite deve ser um inteiro entre 1 e 10000.")
        if isinstance(deslocamento, bool) or not isinstance(deslocamento, int) or deslocamento < 0:
            raise ValueError("O deslocamento deve ser um inteiro maior ou igual a zero.")
        try:
            with self._conexao.transaction():
                with self._conexao.cursor() as cursor:
                    cursor.execute(
                        f"SELECT {COLUNAS_RESULTADO} FROM resultados "
                        "ORDER BY numero_ap ASC LIMIT %s OFFSET %s",
                        (limite, deslocamento),
                    )
                    return tuple(_linha_para_resultado(linha) for linha in cursor.fetchall())
        except psycopg.Error:
            raise ErroRepositorioResultado(
                "FALHA_LISTAGEM", "Não foi possível listar os resultados."
            ) from None

    def contar(self) -> int:
        try:
            with self._conexao.transaction():
                with self._conexao.cursor() as cursor:
                    cursor.execute("SELECT count(*) FROM resultados")
                    return cursor.fetchone()[0]
        except psycopg.Error:
            raise ErroRepositorioResultado(
                "FALHA_CONTAGEM", "Não foi possível contar os resultados."
            ) from None

    def atualizar(self, entrada: ResultadoEntrada) -> ResultadoPersistido:
        """Recalcula todos os derivados e atualiza o concurso informado."""

        if not isinstance(entrada, ResultadoEntrada):
            raise TypeError("A atualização exige um ResultadoEntrada validado.")
        resultado = calcular_resultado(entrada)
        atribuicoes = """
            data_resultado = %s,
            res_01 = %s, res_02 = %s, res_03 = %s,
            res_04 = %s, res_05 = %s, res_06 = %s,
            soma_res = %s, media_aritmetica_res = %s, mediana_res = %s,
            desvio_padrao_media = %s, media_coordenada_x = %s,
            media_coordenada_y = %s, versao_calculo = %s,
            atualizado_em = CURRENT_TIMESTAMP
        """
        parametros = (
            resultado.data_resultado,
            resultado.res_01, resultado.res_02, resultado.res_03,
            resultado.res_04, resultado.res_05, resultado.res_06,
            resultado.soma_res, resultado.media_aritmetica_res,
            resultado.mediana_res, resultado.desvio_padrao_media,
            resultado.media_coordenada_x, resultado.media_coordenada_y,
            resultado.versao_calculo, resultado.numero_ap,
        )
        try:
            with self._conexao.transaction():
                with self._conexao.cursor() as cursor:
                    cursor.execute(
                        f"UPDATE resultados SET {atribuicoes} WHERE numero_ap = %s "
                        f"RETURNING {COLUNAS_RESULTADO}",
                        parametros,
                    )
                    linha = cursor.fetchone()
                    if linha is None:
                        raise ErroRepositorioResultado(
                            "RESULTADO_NAO_ENCONTRADO",
                            f"O concurso {resultado.numero_ap} não está cadastrado.",
                            numero_ap=resultado.numero_ap,
                        )
                    return _linha_para_resultado(linha)
        except ErroRepositorioResultado:
            raise
        except psycopg.Error:
            raise ErroRepositorioResultado(
                "FALHA_ATUALIZACAO", "Não foi possível atualizar o resultado.",
                numero_ap=resultado.numero_ap,
            ) from None


class RepositorioFrequencias:
    """Atualização integral das 60 linhas derivadas de frequência."""

    def __init__(self, conexao: psycopg.Connection) -> None:
        if not isinstance(conexao, psycopg.Connection):
            raise TypeError("O repositório exige uma conexão Psycopg válida.")
        self._conexao = conexao

    def atualizar_todas(
        self, frequencias: tuple[FrequenciaResultado, ...], *, versao_calculo: int = 1
    ) -> None:
        if len(frequencias) != 60 or tuple(item.dezena for item in frequencias) != tuple(range(1, 61)):
            raise ValueError("Devem ser fornecidas as 60 dezenas em ordem de 1 a 60.")
        if isinstance(versao_calculo, bool) or not isinstance(versao_calculo, int) or versao_calculo < 1:
            raise ValueError("A versão do cálculo deve ser um inteiro positivo.")
        sql = """
            UPDATE frequencia_de_resultado SET
                prim_oco = %s, ult_oco = %s, num_oco = %s,
                media_oco = %s, mediana_oco = %s, desv_padrao_oco = %s,
                versao_calculo = %s, atualizado_em = CURRENT_TIMESTAMP
            WHERE dezena = %s
        """
        try:
            with self._conexao.transaction():
                with self._conexao.cursor() as cursor:
                    for item in frequencias:
                        cursor.execute(sql, (
                            item.prim_oco, item.ult_oco, item.num_oco,
                            item.media_oco, item.mediana_oco, item.desv_padrao_oco,
                            versao_calculo, item.dezena,
                        ))
                        if cursor.rowcount != 1:
                            raise ErroRepositorioResultado(
                                "DEZENA_NAO_ENCONTRADA",
                                f"A dezena {item.dezena} não está cadastrada.",
                            )
        except ErroRepositorioResultado:
            raise
        except psycopg.Error:
            raise ErroRepositorioResultado(
                "FALHA_ATUALIZACAO_FREQUENCIAS",
                "Não foi possível atualizar as frequências.",
            ) from None
