"""Simula PD_009 e separa detecção bruta de marcação pela política."""

from dataclasses import asdict, replace
import json
from pathlib import Path

from msen.padroes import detectar_mais_de_tres_dezenas_na_mesma_linha
from msen.screener import (
    AdaptadorPadroesHistoricos,
    EvidenciaHistoricaPadrao,
    PoliticaPadraoSombra,
    carregar_configuracao_screener,
    gerar_amostra,
    simular_modo_sombra,
)


def executar_pd009_sombra(semente: int, configuracao):
    """Retorna simulação e quantidade detectada antes da política de 3%."""

    config = replace(configuracao, semente=semente)
    amostra = gerar_amostra(config)
    total_detectado = sum(
        detectar_mais_de_tres_dezenas_na_mesma_linha(item) for item in amostra
    )
    criterio = replace(
        configuracao.criterios["padroes_historicos"],
        habilitado=True,
        tolerancias={"tolerancia_ocorrencia_percentual": 3.0},
    )
    adaptador = AdaptadorPadroesHistoricos(
        "PD_009",
        criterio,
        PoliticaPadraoSombra(
            detectar_mais_de_tres_dezenas_na_mesma_linha,
            EvidenciaHistoricaPadrao(
                "PD_009", 93, 3069, True, "PD_009:3069:2026-10-27"
            ),
        ),
    )
    simulacao = simular_modo_sombra(amostra, adaptador, semente=semente)
    return simulacao, total_detectado


def main() -> None:
    """Imprime detecções e decisões das duas sementes de controle."""

    raiz = Path(__file__).resolve().parents[1]
    config = carregar_configuracao_screener(raiz / "config" / "screener.toml")
    saida = []
    for semente in (20261027, 42):
        simulacao, detectadas = executar_pd009_sombra(semente, config)
        item = asdict(simulacao)
        item["total_detectado_bruto"] = detectadas
        saida.append(item)
    print(json.dumps(saida, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
