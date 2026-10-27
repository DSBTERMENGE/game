"""Executa a faixa experimental da média em sombra em duas amostras."""

from dataclasses import asdict, replace
import json
from pathlib import Path

from msen.screener import (
    AdaptadorMedidasEstatisticas,
    PoliticaMediaSombra,
    carregar_configuracao_screener,
    gerar_amostra,
    simular_modo_sombra,
)


def executar_media_sombra(semente: int, configuracao):
    """Simula a faixa P01/P99 aprovada para teste sem excluir."""

    config = replace(configuracao, semente=semente)
    criterio = replace(
        configuracao.criterios["medidas_estatisticas"],
        habilitado=True,
        tolerancias={
            "limite_inferior_media": 15.0,
            "limite_superior_media": 45.886666,
        },
    )
    adaptador = AdaptadorMedidasEstatisticas(
        "EST_MEDIA_P01_P99", criterio, PoliticaMediaSombra()
    )
    return simular_modo_sombra(
        gerar_amostra(config), adaptador, semente=semente
    )


def main() -> None:
    """Imprime as duas simulações reproduzíveis da média."""

    raiz = Path(__file__).resolve().parents[1]
    config = carregar_configuracao_screener(raiz / "config" / "screener.toml")
    resultados = [executar_media_sombra(semente, config) for semente in (20261027, 42)]
    print(json.dumps([asdict(item) for item in resultados], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
