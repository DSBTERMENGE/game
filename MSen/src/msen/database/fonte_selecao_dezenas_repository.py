"""Leitura temporal das estatísticas usadas pelo screener de dezenas."""

from __future__ import annotations

from collections import defaultdict
from decimal import Decimal, ROUND_HALF_UP, localcontext

import psycopg

from msen.calculos import calcular_desvio_padrao_populacional
from msen.services.selecao_dezenas import EstatisticaDezenaCorte


SEIS_CASAS = Decimal("0.000001")


class ErroFonteSelecaoDezenas(RuntimeError):
    def __init__(self, codigo: str, mensagem: str) -> None:
        super().__init__(mensagem)
        self.codigo = codigo


class RepositorioFonteSelecaoDezenas:
    def __init__(self, conexao: psycopg.Connection) -> None:
        if not isinstance(conexao, psycopg.Connection):
            raise TypeError("O repositório exige uma conexão Psycopg válida.")
        self._conexao = conexao

    @staticmethod
    def _validar_corte(numero_concurso_corte: int) -> int:
        if (
            isinstance(numero_concurso_corte, bool)
            or not isinstance(numero_concurso_corte, int)
            or numero_concurso_corte <= 0
        ):
            raise ValueError("numero_concurso_corte deve ser inteiro positivo.")
        return numero_concurso_corte

    def carregar_estatisticas_corte(
        self, numero_concurso_corte: int
    ) -> tuple[EstatisticaDezenaCorte, ...]:
        """Usa a fotografia exata ativa ou reconstrói o corte pelos resultados."""

        corte = self._validar_corte(numero_concurso_corte)
        try:
            with self._conexao.transaction():
                with self._conexao.cursor() as cursor:
                    cursor.execute(
                        "SELECT h.dezena, h.quantidade_intervalos, "
                        "h.media_intervalos, h.desvio_padrao_intervalos, "
                        "h.previsao_central "
                        "FROM historico_frequencia_dezenas h "
                        "JOIN geracoes_frequencia_dezenas g "
                        "ON g.id_geracao=h.id_geracao AND g.estado='ATIVA' "
                        "WHERE h.numero_do_concurso=%s AND h.tipo_evento='SIMPLES' "
                        "ORDER BY h.dezena",
                        (corte,),
                    )
                    fotografia = cursor.fetchall()
                    if len(fotografia) == 60:
                        return tuple(EstatisticaDezenaCorte(
                            dezena=linha[0],
                            ultima_ocorrencia=(
                                None if linha[1] == 0
                                else int(linha[4] - linha[2])
                            ),
                            quantidade_intervalos=linha[1],
                            media_intervalos=linha[2],
                            desvio_padrao=linha[3],
                        ) for linha in fotografia)
                    self._validar_resultados_contiguos(cursor, corte)
                    return self._reconstruir_por_resultados(cursor, corte)
        except psycopg.Error:
            raise ErroFonteSelecaoDezenas(
                "FALHA_LEITURA_CORTE",
                "Não foi possível carregar as estatísticas do corte solicitado.",
            ) from None

    @staticmethod
    def _validar_resultados_contiguos(cursor: psycopg.Cursor, corte: int) -> None:
        cursor.execute(
            "SELECT COUNT(1), MIN(numero_ap), MAX(numero_ap) "
            "FROM resultados WHERE numero_ap <= %s",
            (corte,),
        )
        quantidade, minimo, maximo = cursor.fetchone()
        if quantidade != corte or minimo != 1 or maximo != corte:
            raise ErroFonteSelecaoDezenas(
                "LACUNA_HISTORICA",
                f"Os resultados de 1 a {corte} não formam uma sequência completa.",
            )

    @staticmethod
    def _buscar_ocorrencias(
        cursor: psycopg.Cursor, corte: int
    ) -> dict[int, list[int]]:
        cursor.execute(
            "SELECT d.dezena, r.numero_ap FROM resultados r "
            "CROSS JOIN LATERAL UNNEST(ARRAY[r.res_01,r.res_02,r.res_03," 
            "r.res_04,r.res_05,r.res_06]) AS d(dezena) "
            "WHERE r.numero_ap <= %s ORDER BY d.dezena, r.numero_ap",
            (corte,),
        )
        ocorrencias: dict[int, list[int]] = defaultdict(list)
        for dezena, concurso in cursor.fetchall():
            ocorrencias[dezena].append(concurso)
        return ocorrencias

    @classmethod
    def _buscar_ultimas_ocorrencias(
        cls, cursor: psycopg.Cursor, corte: int
    ) -> dict[int, int]:
        return {
            dezena: concursos[-1]
            for dezena, concursos in cls._buscar_ocorrencias(cursor, corte).items()
        }

    @classmethod
    def _reconstruir_por_resultados(
        cls, cursor: psycopg.Cursor, corte: int
    ) -> tuple[EstatisticaDezenaCorte, ...]:
        ocorrencias = cls._buscar_ocorrencias(cursor, corte)
        saida: list[EstatisticaDezenaCorte] = []
        for dezena in range(1, 61):
            concursos = ocorrencias.get(dezena, [])
            intervalos = [
                atual - anterior
                for anterior, atual in zip(concursos, concursos[1:])
            ]
            if not intervalos:
                saida.append(EstatisticaDezenaCorte(dezena, None, 0, None, None))
                continue
            with localcontext() as contexto:
                contexto.prec = 50
                media = (Decimal(sum(intervalos)) / Decimal(len(intervalos))).quantize(
                    SEIS_CASAS, rounding=ROUND_HALF_UP
                )
            saida.append(EstatisticaDezenaCorte(
                dezena=dezena,
                ultima_ocorrencia=concursos[-1],
                quantidade_intervalos=len(intervalos),
                media_intervalos=media,
                desvio_padrao=calcular_desvio_padrao_populacional(intervalos),
            ))
        return tuple(saida)
