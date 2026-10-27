"""Executa duas amostras PD_006 em sombra sem persistir nem excluir."""

from __future__ import annotations

from dataclasses import asdict, replace
import json
from pathlib import Path

from msen.padroes import detectar_mais_de_tres_dezenas_na_mesma_coluna
from msen.screener import (
    AdaptadorPadroesHistoricos,
    EvidenciaHistoricaPadrao,
    PoliticaPadraoSombra,
    carregar_configuracao_screener,
    gerar_amostra,
    simular_modo_sombra,
)


def executar_pd006_sombra(semente: int, configuracao):
    """Simula PD_006 com tolerância de 3%, sem excluir combinações."""

    configuracao_semente = replace(configuracao, semente=semente)
    criterio = replace(
        configuracao.criterios["padroes_historicos"],
        habilitado=True,
        tolerancias={"tolerancia_ocorrencia_percentual": 3.0},
    )
    evidencia = EvidenciaHistoricaPadrao(
        "PD_006", 4, 3069, True, "PD_006:3069:2026-10-27"
    )
    adaptador = AdaptadorPadroesHistoricos(
        "PD_006",
        criterio,
        PoliticaPadraoSombra(
            detectar_mais_de_tres_dezenas_na_mesma_coluna, evidencia
        ),
    )
    return simular_modo_sombra(
        gerar_amostra(configuracao_semente), adaptador, semente=semente
    )


def main() -> None:
    """Imprime as simulações reproduzíveis das duas sementes de controle."""

    raiz = Path(__file__).resolve().parents[1]
    configuracao = carregar_configuracao_screener(raiz / "config" / "screener.toml")
    resultados = [
        executar_pd006_sombra(semente, configuracao)
        for semente in (20261027, 42)
    ]
    print(json.dumps([asdict(item) for item in resultados], ensure_ascii=False, indent=2))
    if any(
        item.total_aprovado_real != 5_000 or item.total_excluido_real != 0
        for item in resultados
    ):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
