"""Fontes somente leitura para o Backtest da seleção de dezenas."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterator

import psycopg

from msen.services.selecao_dezenas import EstatisticaDezenaCorte

from .fonte_selecao_dezenas_repository import RepositorioFonteSelecaoDezenas


class ErroFonteBacktest(RuntimeError):
    def __init__(self, codigo: str, mensagem: str) -> None:
        super().__init__(mensagem)
        self.codigo = codigo


@dataclass(frozen=True, slots=True)
class FotografiaCorteBacktest:
    numero_concurso_corte: int
    estatisticas: tuple[EstatisticaDezenaCorte, ...]


@dataclass(frozen=True, slots=True)
class ResultadoAlvoBacktest:
    numero_concurso: int
    dezenas: frozenset[int]


class RepositorioFonteBacktest:
    """Entrega dados ordenados sem persistir resultados derivados."""

    def __init__(self, conexao: psycopg.Connection) -> None:
        if not isinstance(conexao, psycopg.Connection):
            raise TypeError("O repositório exige uma conexão Psycopg válida.")
        self._conexao = conexao

    @staticmethod
    def _validar_periodo(concurso_inicial: int, concurso_final: int) -> None:
        if (
            isinstance(concurso_inicial, bool)
            or not isinstance(concurso_inicial, int)
            or isinstance(concurso_final, bool)
            or not isinstance(concurso_final, int)
            or concurso_inicial < 500
            or concurso_final < concurso_inicial
        ):
            raise ValueError("O período deve começar em 500 ou depois e ser crescente.")

    def validar_periodo(self, concurso_inicial: int, concurso_final: int) -> None:
        self._validar_periodo(concurso_inicial, concurso_final)
        with self._conexao.cursor() as cursor:
            cursor.execute(
                "SELECT COUNT(*),MIN(numero_ap),MAX(numero_ap) "
                "FROM resultados WHERE numero_ap <= %s",
                (concurso_final,),
            )
            quantidade, minimo, maximo = cursor.fetchone()
        if quantidade != concurso_final or minimo != 1 or maximo != concurso_final:
            raise ErroFonteBacktest(
                "PERIODO_INDISPONIVEL",
                "Os resultados necessários não formam uma sequência completa.",
            )

    def iterar_resultados_alvo(
        self, concurso_inicial: int, concurso_final: int
    ) -> Iterator[ResultadoAlvoBacktest]:
        self._validar_periodo(concurso_inicial, concurso_final)
        nome_cursor = f"resultados_backtest_{id(self):x}"
        with self._conexao.cursor(name=nome_cursor) as cursor:
            cursor.itersize = 100
            cursor.execute(
                "SELECT numero_ap,res_01,res_02,res_03,res_04,res_05,res_06 "
                "FROM resultados WHERE numero_ap BETWEEN %s AND %s "
                "ORDER BY numero_ap",
                (concurso_inicial, concurso_final),
            )
            quantidade = 0
            for linha in cursor:
                quantidade += 1
                yield ResultadoAlvoBacktest(linha[0], frozenset(linha[1:7]))
        if quantidade != concurso_final - concurso_inicial + 1:
            raise ErroFonteBacktest(
                "RESULTADO_ALVO_AUSENTE",
                "Há concurso sem resultado no período solicitado.",
            )

    @staticmethod
    def _converter_linha(linha: tuple[object, ...]) -> EstatisticaDezenaCorte:
        quantidade = linha[2]
        media = linha[3]
        previsao_central = linha[5]
        return EstatisticaDezenaCorte(
            dezena=linha[1],
            ultima_ocorrencia=(
                None if quantidade == 0 else int(previsao_central - media)
            ),
            quantidade_intervalos=quantidade,
            media_intervalos=media,
            desvio_padrao=linha[4],
        )

    @staticmethod
    def _validar_grupo(
        numero_corte: int, itens: list[EstatisticaDezenaCorte]
    ) -> FotografiaCorteBacktest:
        if len(itens) != 60 or {item.dezena for item in itens} != set(range(1, 61)):
            raise ErroFonteBacktest(
                "FOTOGRAFIA_INCOMPLETA",
                f"A fotografia do concurso {numero_corte} não contém as 60 dezenas.",
            )
        return FotografiaCorteBacktest(numero_corte, tuple(itens))

    def iterar_fotografias(
        self, concurso_inicial: int, concurso_final: int
    ) -> Iterator[FotografiaCorteBacktest]:
        """Mantém somente as 60 estatísticas necessárias ao corte corrente."""

        self._validar_periodo(concurso_inicial, concurso_final)
        primeiro_corte = concurso_inicial - 1
        ultimo_corte = concurso_final - 1

        if primeiro_corte == 499:
            estatisticas = RepositorioFonteSelecaoDezenas(
                self._conexao
            ).carregar_estatisticas_corte(499)
            yield FotografiaCorteBacktest(499, estatisticas)
            primeiro_corte = 500

        if primeiro_corte > ultimo_corte:
            return

        nome_cursor = f"backtest_{id(self):x}"
        with self._conexao.cursor(name=nome_cursor) as cursor:
            cursor.itersize = 60
            cursor.execute(
                "SELECT h.numero_do_concurso,h.dezena,h.quantidade_intervalos,"
                "h.media_intervalos,h.desvio_padrao_intervalos,h.previsao_central "
                "FROM historico_frequencia_dezenas h "
                "JOIN geracoes_frequencia_dezenas g "
                "ON g.id_geracao=h.id_geracao AND g.estado='ATIVA' "
                "WHERE h.tipo_evento='SIMPLES' "
                "AND h.numero_do_concurso BETWEEN %s AND %s "
                "ORDER BY h.numero_do_concurso,h.dezena",
                (primeiro_corte, ultimo_corte),
            )
            numero_atual: int | None = None
            itens: list[EstatisticaDezenaCorte] = []
            quantidade_grupos = 0
            for linha in cursor:
                numero_linha = linha[0]
                if numero_atual is not None and numero_linha != numero_atual:
                    yield self._validar_grupo(numero_atual, itens)
                    quantidade_grupos += 1
                    itens = []
                numero_atual = numero_linha
                itens.append(self._converter_linha(linha))
            if numero_atual is not None:
                yield self._validar_grupo(numero_atual, itens)
                quantidade_grupos += 1

        quantidade_esperada = ultimo_corte - primeiro_corte + 1
        if quantidade_grupos != quantidade_esperada:
            raise ErroFonteBacktest(
                "FOTOGRAFIA_AUSENTE",
                "Há corte sem fotografia estatística no período solicitado.",
            )
