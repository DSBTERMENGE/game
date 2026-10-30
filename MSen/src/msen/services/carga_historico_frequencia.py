"""Carga completa, troca atômica e acréscimo do histórico de frequências."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from time import perf_counter
from typing import Callable, Iterable

import psycopg
from psycopg.types.json import Jsonb

from msen.modelos import ResultadoEntrada

from .configuracao_frequencia import ConfiguracaoFrequencia
from .frequencia_historica import FotografiaFrequencia, MotorFrequenciaAcumulada


class ErroCargaHistoricoFrequencia(RuntimeError):
    def __init__(self, codigo: str, mensagem: str) -> None:
        super().__init__(mensagem)
        self.codigo = codigo


class OperacaoFrequenciaCancelada(ErroCargaHistoricoFrequencia):
    def __init__(self) -> None:
        super().__init__(
            "OPERACAO_CANCELADA",
            "A operação foi cancelada com segurança antes da confirmação.",
        )


@dataclass(frozen=True, slots=True)
class RelatorioCargaHistoricoFrequencia:
    modo: str
    id_geracao: int
    concurso_inicial: int
    concurso_final: int
    fotografias_adicionadas: int
    linhas_adicionadas: int
    quantidade_resultados: int
    assinatura_resultados: str
    duracao_segundos: float


@dataclass(frozen=True, slots=True)
class _GeracaoAtiva:
    id_geracao: int
    assinatura_configuracao: str
    versao_calculo: int
    concurso_inicial: int
    concurso_final: int
    quantidade_fotografias: int
    assinatura_resultados: str
    quantidade_resultados: int


SQL_INSERIR_FOTOGRAFIA = """
    INSERT INTO historico_frequencia_dezenas (
        id_geracao, numero_do_concurso, dezena, tipo_evento,
        quantidade_ocorrencias, quantidade_intervalos,
        intervalo_minimo, intervalo_maximo, media_intervalos,
        mediana_intervalos, desvio_padrao_intervalos, previsao_central,
        limite_inferior_exato, limite_superior_exato,
        concurso_limite_inferior, concurso_limite_superior
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
"""


def assinatura_resultados(resultados: Iterable[ResultadoEntrada]) -> str:
    digest = hashlib.sha256()
    quantidade = 0
    for item in resultados:
        if not isinstance(item, ResultadoEntrada):
            raise TypeError("A assinatura aceita somente ResultadoEntrada.")
        registro = {
            "data": item.data_resultado.isoformat(),
            "dezenas": item.resultados,
            "numero_do_concurso": item.numero_ap,
        }
        digest.update(json.dumps(
            registro, ensure_ascii=False, sort_keys=True, separators=(",", ":")
        ).encode("utf-8"))
        digest.update(b"\n")
        quantidade += 1
    if quantidade == 0:
        raise ErroCargaHistoricoFrequencia(
            "ORIGEM_VAZIA", "Não existem resultados para construir o histórico."
        )
    return digest.hexdigest()


def _listar_resultados(
    cursor: psycopg.Cursor, concurso_inicial: int
) -> tuple[ResultadoEntrada, ...]:
    cursor.execute(
        "SELECT data_resultado, numero_ap, res_01, res_02, res_03, res_04, "
        "res_05, res_06 FROM resultados WHERE numero_ap >= %s "
        "ORDER BY numero_ap",
        (concurso_inicial,),
    )
    return tuple(
        ResultadoEntrada.criar(
            data_resultado=linha[0], numero_ap=linha[1], resultados=linha[2:8]
        )
        for linha in cursor.fetchall()
    )


def _buscar_geracao_ativa(cursor: psycopg.Cursor) -> _GeracaoAtiva | None:
    cursor.execute(
        "SELECT id_geracao, assinatura_configuracao, versao_calculo, "
        "concurso_inicial, concurso_final, quantidade_fotografias, "
        "assinatura_resultados, quantidade_resultados "
        "FROM geracoes_frequencia_dezenas WHERE estado='ATIVA'"
    )
    linha = cursor.fetchone()
    if linha is None:
        return None
    return _GeracaoAtiva(
        linha[0], linha[1].strip(), linha[2], linha[3], linha[4], linha[5],
        linha[6].strip(), linha[7],
    )


def _parametros_fotografia(
    id_geracao: int, item: FotografiaFrequencia
) -> tuple[object, ...]:
    return (
        id_geracao, item.numero_do_concurso, item.dezena, item.tipo_evento,
        item.quantidade_ocorrencias, item.quantidade_intervalos,
        item.intervalo_minimo, item.intervalo_maximo, item.media_intervalos,
        item.mediana_intervalos, item.desvio_padrao_intervalos,
        item.previsao_central, item.limite_inferior_exato,
        item.limite_superior_exato, item.concurso_limite_inferior,
        item.concurso_limite_superior,
    )


def _inserir_lote(
    cursor: psycopg.Cursor,
    id_geracao: int,
    fotografias: tuple[FotografiaFrequencia, ...],
) -> int:
    if not fotografias:
        return 0
    cursor.executemany(
        SQL_INSERIR_FOTOGRAFIA,
        (_parametros_fotografia(id_geracao, item) for item in fotografias),
    )
    return len(fotografias)


def _validar_origem(
    resultados: tuple[ResultadoEntrada, ...], configuracao: ConfiguracaoFrequencia
) -> int:
    primeiro_corte = configuracao.concurso_inicial + configuracao.tamanho_inicial - 1
    if not resultados or resultados[-1].numero_ap < primeiro_corte:
        raise ErroCargaHistoricoFrequencia(
            "RESULTADOS_INSUFICIENTES",
            f"São necessários resultados até o concurso {primeiro_corte}.",
        )
    esperado = configuracao.concurso_inicial
    for item in resultados:
        if item.numero_ap != esperado:
            raise ErroCargaHistoricoFrequencia(
                "LACUNA_HISTORICA",
                f"Era esperado o concurso {esperado}, recebido {item.numero_ap}.",
            )
        esperado += 1
    return primeiro_corte


def _carga_completa(
    cursor: psycopg.Cursor,
    conexao: psycopg.Connection,
    resultados: tuple[ResultadoEntrada, ...],
    configuracao: ConfiguracaoFrequencia,
    *,
    falhar_apos_lotes: int | None,
    informar_progresso: Callable[[str, int, int], None] | None,
    cancelamento_solicitado: Callable[[], bool] | None,
) -> RelatorioCargaHistoricoFrequencia:
    # Importação local evita ciclo entre os pacotes públicos database/services.
    from msen.database.configuracao_frequencia_repository import (
        RepositorioConfiguracaoFrequencia,
    )

    inicio_tempo = perf_counter()
    primeiro_corte = _validar_origem(resultados, configuracao)
    assinatura_origem = assinatura_resultados(resultados)
    ultimo_concurso = resultados[-1].numero_ap
    quantidade_cortes = ultimo_concurso - primeiro_corte + 1
    cursor.execute(
        "INSERT INTO geracoes_frequencia_dezenas "
        "(assinatura_configuracao, configuracao_json, assinatura_resultados, "
        "quantidade_resultados, versao_calculo, concurso_inicial, concurso_final, "
        "quantidade_fotografias) VALUES (%s, %s, %s, %s, %s, %s, %s, %s) "
        "RETURNING id_geracao",
        (
            configuracao.assinatura_sha256, Jsonb(configuracao.conteudo_assinavel()),
            assinatura_origem, len(resultados), configuracao.versao_calculo,
            primeiro_corte, ultimo_concurso, quantidade_cortes,
        ),
    )
    id_geracao = cursor.fetchone()[0]
    motor = MotorFrequenciaAcumulada(configuracao)
    linhas = 0
    lotes = 0
    total = len(resultados)
    for indice, resultado in enumerate(resultados, start=1):
        if cancelamento_solicitado and cancelamento_solicitado():
            raise OperacaoFrequenciaCancelada()
        fotografias = motor.processar(resultado)
        if fotografias:
            linhas += _inserir_lote(cursor, id_geracao, fotografias)
            lotes += 1
            if falhar_apos_lotes is not None and lotes >= falhar_apos_lotes:
                raise ErroCargaHistoricoFrequencia(
                    "FALHA_SIMULADA", "Falha controlada durante a carga completa."
                )
        if informar_progresso:
            informar_progresso("Construindo geração completa", indice, total)

    cursor.execute(
        "DELETE FROM geracoes_frequencia_dezenas WHERE id_geracao <> %s",
        (id_geracao,),
    )
    cursor.execute(
        "UPDATE geracoes_frequencia_dezenas SET estado='ATIVA', "
        "concluida_em=CURRENT_TIMESTAMP WHERE id_geracao=%s",
        (id_geracao,),
    )
    RepositorioConfiguracaoFrequencia(conexao).substituir_ativa(configuracao)
    return RelatorioCargaHistoricoFrequencia(
        "CARGA_COMPLETA", id_geracao, primeiro_corte, ultimo_concurso,
        quantidade_cortes, linhas, len(resultados), assinatura_origem,
        perf_counter() - inicio_tempo,
    )


def atualizar_historico_frequencia(
    conexao: psycopg.Connection,
    configuracao: ConfiguracaoFrequencia,
    *,
    reconstruir_origem_alterada: bool = False,
    confirmacao_gravacao: bool = False,
    informar_progresso: Callable[[str, int, int], None] | None = None,
    cancelamento_solicitado: Callable[[], bool] | None = None,
    _falhar_apos_lotes: int | None = None,
) -> RelatorioCargaHistoricoFrequencia:
    if not isinstance(conexao, psycopg.Connection):
        raise TypeError("conexao deve ser Psycopg Connection.")
    if not isinstance(configuracao, ConfiguracaoFrequencia):
        raise TypeError("configuracao deve ser ConfiguracaoFrequencia.")
    if confirmacao_gravacao is not True:
        raise ErroCargaHistoricoFrequencia(
            "CONFIRMACAO_OBRIGATORIA",
            "Confirme explicitamente a gravação antes de salvar os dados.",
        )
    with conexao.transaction():
        with conexao.cursor() as cursor:
            cursor.execute("LOCK TABLE resultados IN SHARE MODE")
            cursor.execute(
                "LOCK TABLE geracoes_frequencia_dezenas IN SHARE ROW EXCLUSIVE MODE"
            )
            resultados = _listar_resultados(cursor, configuracao.concurso_inicial)
            primeiro_corte = _validar_origem(resultados, configuracao)
            ativa = _buscar_geracao_ativa(cursor)
            if (
                ativa is None
                or ativa.assinatura_configuracao != configuracao.assinatura_sha256
                or ativa.versao_calculo != configuracao.versao_calculo
            ):
                return _carga_completa(
                    cursor, conexao, resultados, configuracao,
                    falhar_apos_lotes=_falhar_apos_lotes,
                    informar_progresso=informar_progresso,
                    cancelamento_solicitado=cancelamento_solicitado,
                )

            prefixo = tuple(
                item for item in resultados if item.numero_ap <= ativa.concurso_final
            )
            prefixo_valido = (
                len(prefixo) == ativa.quantidade_resultados
                and assinatura_resultados(prefixo) == ativa.assinatura_resultados
                and ativa.concurso_inicial == primeiro_corte
            )
            if not prefixo_valido:
                if not reconstruir_origem_alterada:
                    raise ErroCargaHistoricoFrequencia(
                        "RECONSTRUCAO_NECESSARIA",
                        "Resultados já processados mudaram; é necessária reconstrução integral.",
                    )
                return _carga_completa(
                    cursor, conexao, resultados, configuracao,
                    falhar_apos_lotes=_falhar_apos_lotes,
                    informar_progresso=informar_progresso,
                    cancelamento_solicitado=cancelamento_solicitado,
                )

            ultimo_concurso = resultados[-1].numero_ap
            if ultimo_concurso == ativa.concurso_final:
                return RelatorioCargaHistoricoFrequencia(
                    "SEM_ALTERACAO", ativa.id_geracao, primeiro_corte,
                    ultimo_concurso, 0, 0, len(resultados),
                    ativa.assinatura_resultados, 0.0,
                )
            if ultimo_concurso < ativa.concurso_final:
                raise ErroCargaHistoricoFrequencia(
                    "RECONSTRUCAO_NECESSARIA",
                    "A origem atual termina antes da geração ativa.",
                )

            inicio_tempo = perf_counter()
            motor = MotorFrequenciaAcumulada(configuracao)
            linhas = 0
            novos_cortes = 0
            lotes = 0
            total = len(resultados)
            for indice, resultado in enumerate(resultados, start=1):
                if cancelamento_solicitado and cancelamento_solicitado():
                    raise OperacaoFrequenciaCancelada()
                if resultado.numero_ap <= ativa.concurso_final:
                    motor.processar(resultado, emitir=False)
                    if informar_progresso:
                        informar_progresso("Recompondo estado acumulado", indice, total)
                    continue
                fotografias = motor.processar(resultado)
                linhas += _inserir_lote(cursor, ativa.id_geracao, fotografias)
                novos_cortes += 1
                lotes += 1
                if _falhar_apos_lotes is not None and lotes >= _falhar_apos_lotes:
                    raise ErroCargaHistoricoFrequencia(
                        "FALHA_SIMULADA", "Falha controlada durante o acréscimo."
                    )
                if informar_progresso:
                    informar_progresso("Gravando novos concursos", indice, total)

            assinatura_origem = assinatura_resultados(resultados)
            cursor.execute(
                "UPDATE geracoes_frequencia_dezenas SET concurso_final=%s, "
                "quantidade_fotografias=%s, assinatura_resultados=%s, "
                "quantidade_resultados=%s, concluida_em=CURRENT_TIMESTAMP "
                "WHERE id_geracao=%s",
                (
                    ultimo_concurso, ultimo_concurso - primeiro_corte + 1,
                    assinatura_origem, len(resultados), ativa.id_geracao,
                ),
            )
            return RelatorioCargaHistoricoFrequencia(
                "INCREMENTAL", ativa.id_geracao, ativa.concurso_final + 1,
                ultimo_concurso, novos_cortes, linhas, len(resultados),
                assinatura_origem, perf_counter() - inicio_tempo,
            )
