"""Executa a faixa experimental da extensão em duas amostras sombra."""

from dataclasses import asdict, replace
import json
from pathlib import Path

from msen.screener import (
    AdaptadorMedidasGeometricas,
    PoliticaExtensaoSombra,
    carregar_configuracao_screener,
    gerar_amostra,
    simular_modo_sombra,
)


def executar_extensao_sombra(semente: int, configuracao):
    """Simula a faixa P01/P99 da extensão sem excluir combinações."""

    config = replace(configuracao, semente=semente)
    criterio = replace(
        configuracao.criterios["medidas_geometricas"],
        habilitado=True,
        tolerancias={
            "limite_inferior_extensao": 8.650282,
            "limite_superior_extensao": 32.300058,
        },
    )
    adaptador = AdaptadorMedidasGeometricas(
        "GEO_EXTENSAO_P01_P99", criterio, PoliticaExtensaoSombra()
    )
    return simular_modo_sombra(
        gerar_amostra(config), adaptador, semente=semente
    )


def main() -> None:
    """Imprime as duas simulações reproduzíveis da extensão."""

    raiz = Path(__file__).resolve().parents[1]
    config = carregar_configuracao_screener(raiz / "config" / "screener.toml")
    resultados = [
        executar_extensao_sombra(semente, config) for semente in (20261027, 42)
    ]
    print(json.dumps([asdict(item) for item in resultados], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
