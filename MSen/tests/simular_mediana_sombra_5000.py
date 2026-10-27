"""Executa a faixa experimental da mediana em sombra em duas amostras."""

from dataclasses import asdict, replace
import json
from pathlib import Path

from msen.screener import (
    AdaptadorMedidasEstatisticas,
    PoliticaMedianaSombra,
    carregar_configuracao_screener,
    gerar_amostra,
    simular_modo_sombra,
)


def executar_mediana_sombra(semente: int, configuracao):
    """Simula a faixa P01/P99 da mediana sem excluir combinações."""

    config = replace(configuracao, semente=semente)
    criterio = replace(
        configuracao.criterios["medidas_estatisticas"],
        habilitado=True,
        tolerancias={
            "limite_inferior_mediana": 10.5,
            "limite_superior_mediana": 50.5,
        },
    )
    adaptador = AdaptadorMedidasEstatisticas(
        "EST_MEDIANA_P01_P99", criterio, PoliticaMedianaSombra()
    )
    return simular_modo_sombra(
        gerar_amostra(config), adaptador, semente=semente
    )


def main() -> None:
    """Imprime as duas simulações reproduzíveis da mediana."""

    raiz = Path(__file__).resolve().parents[1]
    config = carregar_configuracao_screener(raiz / "config" / "screener.toml")
    resultados = [
        executar_mediana_sombra(semente, config) for semente in (20261027, 42)
    ]
    print(json.dumps([asdict(item) for item in resultados], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
