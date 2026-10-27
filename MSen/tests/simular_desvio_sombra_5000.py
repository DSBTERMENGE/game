"""Executa a faixa experimental do desvio em sombra em duas amostras."""

from dataclasses import asdict, replace
import json
from pathlib import Path

from msen.screener import (
    AdaptadorMedidasEstatisticas,
    PoliticaDesvioPadraoSombra,
    carregar_configuracao_screener,
    gerar_amostra,
    simular_modo_sombra,
)


def executar_desvio_sombra(semente: int, configuracao):
    """Simula a faixa P01/P99 do desvio sem excluir combinações."""

    config = replace(configuracao, semente=semente)
    criterio = replace(
        configuracao.criterios["medidas_estatisticas"],
        habilitado=True,
        tolerancias={
            "limite_inferior_desvio": 7.145546,
            "limite_superior_desvio": 22.774694,
        },
    )
    adaptador = AdaptadorMedidasEstatisticas(
        "EST_DESVIO_P01_P99", criterio, PoliticaDesvioPadraoSombra()
    )
    return simular_modo_sombra(
        gerar_amostra(config), adaptador, semente=semente
    )


def main() -> None:
    """Imprime as duas simulações reproduzíveis do desvio-padrão."""

    raiz = Path(__file__).resolve().parents[1]
    config = carregar_configuracao_screener(raiz / "config" / "screener.toml")
    resultados = [
        executar_desvio_sombra(semente, config) for semente in (20261027, 42)
    ]
    print(json.dumps([asdict(item) for item in resultados], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
