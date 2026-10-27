"""Mede 5.000 combinações e extrapola sem executar o universo completo."""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from sys import getsizeof
from time import perf_counter

from msen.geometria.medidas import calcular_area_e_centro_gravidade
from msen.screener import (
    carregar_configuracao_screener,
    criar_iterador_combinacoes,
    estimar_capacidade,
    gerar_amostra,
)


def _medir(funcao):
    """Executa uma função e devolve resultado e duração monotônica."""

    inicio = perf_counter()
    resultado = funcao()
    return resultado, perf_counter() - inicio


def main() -> None:
    """Imprime medições locais e projeções lineares em JSON."""

    raiz = Path(__file__).resolve().parents[1]
    configuracao = carregar_configuracao_screener(raiz / "config" / "screener.toml")
    amostra, tempo_amostra = _medir(lambda: gerar_amostra(configuracao))
    _, tempo_lexico = _medir(lambda: tuple(criar_iterador_combinacoes(configuracao)))
    _, tempo_geometria = _medir(
        lambda: tuple(calcular_area_e_centro_gravidade(item) for item in amostra)
    )

    bytes_python = getsizeof(amostra) + sum(getsizeof(item) for item in amostra)
    bytes_csv = sum(
        len(",".join(f"{dezena:02d}" for dezena in item).encode("ascii")) + 1
        for item in amostra
    )
    dados = {
        "tamanho_amostra": len(amostra),
        "tempos_amostra_segundos": {
            "geracao_aleatoria": tempo_amostra,
            "iteracao_lexicografica": tempo_lexico,
            "geometria_completa": tempo_geometria,
        },
        "projecoes": {
            "iteracao_lexicografica": asdict(
                estimar_capacidade(len(amostra), tempo_lexico)
            ),
            "geometria_completa": asdict(
                estimar_capacidade(len(amostra), tempo_geometria)
            ),
            "memoria_python": estimar_capacidade(
                len(amostra), 1.0, bytes_python
            ).bytes_universo,
            "arquivo_csv": estimar_capacidade(
                len(amostra), 1.0, bytes_csv
            ).bytes_universo,
            "binario_seis_bytes": 50_063_860 * 6,
        },
    }
    print(json.dumps(dados, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
