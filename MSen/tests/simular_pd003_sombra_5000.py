"""Executa duas amostras PD_003 em sombra sem persistir nem excluir."""

from __future__ import annotations

from dataclasses import asdict, replace
import json
from pathlib import Path

from msen.padroes import detectar_mais_de_tres_dezenas_sequenciais
from msen.screener import (
    AdaptadorPadroesHistoricos,
    EvidenciaHistoricaPadrao,
    PoliticaPadraoSombra,
    carregar_configuracao_screener,
    gerar_amostra,
    simular_modo_sombra,
)


def _executar(semente: int, configuracao):
    """Gera uma amostra e simula PD_003 com a hipótese não aprovada de 3%."""

    configuracao_semente = replace(configuracao, semente=semente)
    configuracao_criterio = replace(
        configuracao.criterios["padroes_historicos"],
        habilitado=True,
        tolerancias={"tolerancia_ocorrencia_percentual": 3.0},
    )
    evidencia = EvidenciaHistoricaPadrao(
        "PD_003", 5, 3069, True, "PD_003:3069:2026-10-27"
    )
    adaptador = AdaptadorPadroesHistoricos(
        "PD_003",
        configuracao_criterio,
        PoliticaPadraoSombra(
            detectar_mais_de_tres_dezenas_sequenciais, evidencia
        ),
    )
    return simular_modo_sombra(
        gerar_amostra(configuracao_semente), adaptador, semente=semente
    )


def main() -> None:
    """Imprime resultados reproduzíveis para as sementes padrão e alternativa."""

    raiz = Path(__file__).resolve().parents[1]
    configuracao = carregar_configuracao_screener(raiz / "config" / "screener.toml")
    resultados = [_executar(semente, configuracao) for semente in (20261027, 42)]
    print(json.dumps([asdict(item) for item in resultados], ensure_ascii=False, indent=2))
    if any(item.total_aprovado_real != 5_000 or item.total_excluido_real != 0 for item in resultados):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
