"""Prévia, simulação e coordenação segura das operações de frequência."""

from __future__ import annotations

from dataclasses import dataclass
from time import perf_counter
from threading import Event, Lock
from typing import Callable

import psycopg

from .carga_historico_frequencia import (
    OperacaoFrequenciaCancelada,
    _buscar_geracao_ativa,
    _listar_resultados,
    _validar_origem,
    assinatura_resultados,
)
from .configuracao_frequencia import (
    ConfiguracaoFrequencia,
    DivergenciaConfiguracaoFrequencia,
    comparar_configuracoes_frequencia,
)
from .frequencia_historica import MotorFrequenciaAcumulada


MENSAGEM_CONFIRMACAO = (
    "O tick para salvar está ativo. Você realmente deseja salvar os dados?"
)


@dataclass(frozen=True, slots=True)
class PreviaOperacaoHistoricoFrequencia:
    modo: str
    salvar_dados: bool
    exige_confirmacao: bool
    mensagem_confirmacao: str | None
    concurso_inicial: int
    concurso_final: int
    concursos_novos: tuple[int, ...]
    substitui_geracao: bool
    divergencias_configuracao: tuple[DivergenciaConfiguracaoFrequencia, ...]
    motivo: str


@dataclass(frozen=True, slots=True)
class RelatorioSimulacaoHistoricoFrequencia:
    previa: PreviaOperacaoHistoricoFrequencia
    fotografias_calculadas: int
    linhas_calculadas: int
    duracao_segundos: float


class ExecucaoFrequenciaEmAndamento(RuntimeError):
    pass


class CoordenadorOperacaoFrequencia:
    """Impede duas operações simultâneas e oferece cancelamento cooperativo."""

    def __init__(self) -> None:
        self._trava = Lock()
        self._cancelamento = Event()
        self._executando = False

    def executar(self, operacao: Callable[[Callable[[], bool]], object]) -> object:
        if not callable(operacao):
            raise TypeError("operacao deve ser chamável.")
        with self._trava:
            if self._executando:
                raise ExecucaoFrequenciaEmAndamento(
                    "Já existe uma operação de frequência em andamento."
                )
            self._executando = True
            self._cancelamento.clear()
        try:
            return operacao(self._cancelamento.is_set)
        finally:
            with self._trava:
                self._executando = False

    def solicitar_cancelamento(self) -> bool:
        with self._trava:
            if not self._executando:
                return False
            self._cancelamento.set()
            return True

    def esta_executando(self) -> bool:
        with self._trava:
            return self._executando


def preparar_operacao_historico_frequencia(
    conexao: psycopg.Connection,
    configuracao: ConfiguracaoFrequencia,
    *,
    salvar_dados: bool = True,
) -> PreviaOperacaoHistoricoFrequencia:
    if not isinstance(conexao, psycopg.Connection):
        raise TypeError("conexao deve ser Psycopg Connection.")
    if not isinstance(configuracao, ConfiguracaoFrequencia):
        raise TypeError("configuracao deve ser ConfiguracaoFrequencia.")
    if not isinstance(salvar_dados, bool):
        raise TypeError("salvar_dados deve ser booleano.")

    with conexao.cursor() as cursor:
        resultados = _listar_resultados(cursor, configuracao.concurso_inicial)
        primeiro_corte = _validar_origem(resultados, configuracao)
        ativa = _buscar_geracao_ativa(cursor)
    ultimo_concurso = resultados[-1].numero_ap
    divergencias: tuple[DivergenciaConfiguracaoFrequencia, ...] = ()
    concursos_novos: tuple[int, ...] = ()
    substitui = False

    if ativa is None:
        modo = "PRIMEIRA_CARGA"
        substitui = True
        motivo = "Ainda não existe geração histórica ativa."
    elif ativa.assinatura_configuracao != configuracao.assinatura_sha256:
        modo = "RECONSTRUCAO_CONFIGURACAO"
        substitui = True
        from msen.database.configuracao_frequencia_repository import (
            RepositorioConfiguracaoFrequencia,
        )
        gravada = RepositorioConfiguracaoFrequencia(conexao).buscar_ativa().configuracao
        divergencias = comparar_configuracoes_frequencia(gravada, configuracao)
        motivo = "A configuração calculada difere da configuração gravada."
    else:
        prefixo = tuple(
            item for item in resultados if item.numero_ap <= ativa.concurso_final
        )
        prefixo_valido = (
            len(prefixo) == ativa.quantidade_resultados
            and assinatura_resultados(prefixo) == ativa.assinatura_resultados
            and ativa.concurso_inicial == primeiro_corte
        )
        if not prefixo_valido:
            modo = "RECONSTRUCAO_ORIGEM"
            substitui = True
            motivo = "Resultados já processados foram alterados ou removidos."
        elif ultimo_concurso < ativa.concurso_final:
            modo = "RECONSTRUCAO_ORIGEM"
            substitui = True
            motivo = "A origem atual termina antes da geração ativa."
        elif ultimo_concurso == ativa.concurso_final:
            modo = "SEM_ALTERACAO"
            motivo = "A geração ativa já contém todos os concursos disponíveis."
        else:
            modo = "INCREMENTAL"
            concursos_novos = tuple(range(ativa.concurso_final + 1, ultimo_concurso + 1))
            motivo = "Somente os concursos novos serão acrescentados."

    exige_confirmacao = salvar_dados and modo != "SEM_ALTERACAO"
    return PreviaOperacaoHistoricoFrequencia(
        modo=modo,
        salvar_dados=salvar_dados,
        exige_confirmacao=exige_confirmacao,
        mensagem_confirmacao=MENSAGEM_CONFIRMACAO if exige_confirmacao else None,
        concurso_inicial=primeiro_corte,
        concurso_final=ultimo_concurso,
        concursos_novos=concursos_novos,
        substitui_geracao=substitui,
        divergencias_configuracao=divergencias,
        motivo=motivo,
    )


def simular_historico_frequencia(
    conexao: psycopg.Connection,
    configuracao: ConfiguracaoFrequencia,
    *,
    informar_progresso: Callable[[str, int, int], None] | None = None,
    cancelamento_solicitado: Callable[[], bool] | None = None,
) -> RelatorioSimulacaoHistoricoFrequencia:
    previa = preparar_operacao_historico_frequencia(
        conexao, configuracao, salvar_dados=False
    )
    inicio = perf_counter()
    with conexao.cursor() as cursor:
        resultados = _listar_resultados(cursor, configuracao.concurso_inicial)
        ativa = _buscar_geracao_ativa(cursor)
    motor = MotorFrequenciaAcumulada(configuracao)
    linhas = 0
    cortes: set[int] = set()
    total = len(resultados)
    somente_novos = previa.modo == "INCREMENTAL" and ativa is not None
    for indice, resultado in enumerate(resultados, start=1):
        if cancelamento_solicitado and cancelamento_solicitado():
            raise OperacaoFrequenciaCancelada()
        emitir = not somente_novos or resultado.numero_ap > ativa.concurso_final
        fotografias = motor.processar(resultado, emitir=emitir)
        linhas += len(fotografias)
        if fotografias:
            cortes.add(resultado.numero_ap)
        if informar_progresso:
            informar_progresso("Simulando sem salvar", indice, total)
    return RelatorioSimulacaoHistoricoFrequencia(
        previa=previa,
        fotografias_calculadas=len(cortes),
        linhas_calculadas=linhas,
        duracao_segundos=perf_counter() - inicio,
    )
