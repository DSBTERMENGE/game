"""Validação limitada da aplicação integral do Screener (etapa 29.5.5)."""

from __future__ import annotations

import ctypes
from itertools import islice
from json import dumps
from os import getpid
from pathlib import Path
from time import perf_counter
from unittest.mock import patch

from dotenv import load_dotenv

from msen.api import screener_extensivel_service as servico


load_dotenv(Path(__file__).resolve().parents[1] / ".env")


class _ContadoresMemoria(ctypes.Structure):
    _fields_ = [
        ("cb", ctypes.c_ulong),
        ("PageFaultCount", ctypes.c_ulong),
        ("PeakWorkingSetSize", ctypes.c_size_t),
        ("WorkingSetSize", ctypes.c_size_t),
        ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
        ("QuotaPagedPoolUsage", ctypes.c_size_t),
        ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
        ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
        ("PagefileUsage", ctypes.c_size_t),
        ("PeakPagefileUsage", ctypes.c_size_t),
    ]


def memoria_mib() -> tuple[float, float]:
    processo = ctypes.windll.kernel32.OpenProcess(0x0400 | 0x0010, False, getpid())
    if not processo:
        raise OSError("Não foi possível consultar a memória do processo.")
    try:
        dados = _ContadoresMemoria()
        dados.cb = ctypes.sizeof(dados)
        if not ctypes.windll.psapi.GetProcessMemoryInfo(
            processo, ctypes.byref(dados), dados.cb
        ):
            raise OSError("GetProcessMemoryInfo falhou.")
        divisor = 1024 * 1024
        return dados.WorkingSetSize / divisor, dados.PeakWorkingSetSize / divisor
    finally:
        ctypes.windll.kernel32.CloseHandle(processo)


def executar_volume(volume: int) -> dict[str, object]:
    criar_original = servico.criar_iterador_combinacoes
    consolidar_original = servico.criar_quadro_consolidado
    progresso: list[tuple[int, int]] = []

    def criar_limitado(configuracao, *, confirmacao_integral=None):
        return islice(
            criar_original(
                configuracao, confirmacao_integral=confirmacao_integral
            ),
            volume,
        )

    def consolidar_limitado(relatorio, *, tipo_escopo):
        return consolidar_original(
            relatorio, tipo_escopo=tipo_escopo, total_universo=volume
        )

    memoria_inicial, _ = memoria_mib()
    inicio = perf_counter()
    with (
        patch.object(servico, "TOTAL_COMBINACOES", volume),
        patch.object(servico, "criar_iterador_combinacoes", criar_limitado),
        patch.object(servico, "criar_quadro_consolidado", consolidar_limitado),
    ):
        dados = servico.gerar_quadro_screener_integral(
            informar_progresso=lambda _etapa, concluido, total: progresso.append(
                (concluido, total)
            )
        )
    duracao = perf_counter() - inicio
    memoria_final, memoria_pico = memoria_mib()
    resumo = dados["resumo"]
    return {
        "volume": volume,
        "analisadas": resumo["total_analisado"],
        "aprovadas": resumo["total_aprovado"],
        "excluidas": resumo["total_excluido"],
        "reconciliado": resumo["reconciliado"],
        "duracao_segundos": round(duracao, 3),
        "combinacoes_por_segundo": round(volume / duracao, 1),
        "memoria_inicial_mib": round(memoria_inicial, 2),
        "memoria_final_mib": round(memoria_final, 2),
        "memoria_pico_processo_mib": round(memoria_pico, 2),
        "eventos_progresso": len(progresso),
        "ultimo_progresso": progresso[-1] if progresso else None,
    }


def validar_cancelamento() -> dict[str, object]:
    ultimo = 0
    cancelado = False

    def progresso(_etapa: str, concluido: int, _total: int) -> None:
        nonlocal ultimo, cancelado
        ultimo = concluido
        if concluido >= 10_000:
            cancelado = True

    inicio = perf_counter()
    try:
        servico.gerar_quadro_screener_integral(
            informar_progresso=progresso,
            cancelado=lambda: cancelado,
        )
    except InterruptedError:
        return {
            "cancelamento_reconhecido": True,
            "ultimo_progresso": ultimo,
            "duracao_segundos": round(perf_counter() - inicio, 3),
        }
    raise AssertionError("A solicitação de cancelamento não interrompeu o processo.")


if __name__ == "__main__":
    resultados = [executar_volume(volume) for volume in (10_000, 20_000, 50_000)]
    cancelamento = validar_cancelamento()
    media_taxa = sum(item["combinacoes_por_segundo"] for item in resultados) / len(resultados)
    estimativa = servico.TOTAL_COMBINACOES / media_taxa
    print(dumps({
        "volumes": resultados,
        "cancelamento": cancelamento,
        "taxa_media_combinacoes_por_segundo": round(media_taxa, 1),
        "estimativa_integral_segundos": round(estimativa, 1),
        "estimativa_integral_horas": round(estimativa / 3600, 2),
    }, ensure_ascii=False, indent=2))
