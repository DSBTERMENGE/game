"""Reconcilia e simula os padrões históricos acima da tolerância de 3%."""

from __future__ import annotations

from dataclasses import asdict, replace
import json
from pathlib import Path

from dotenv import load_dotenv

from msen.config import carregar_configuracao_banco
from msen.database import abrir_conexao
from msen.modelos import ResultadoEntrada
from msen.padroes import (
    calcular_estatistica_padrao,
    detectar_duas_dezenas_na_mesma_coluna,
    detectar_duas_dezenas_na_mesma_linha,
    detectar_duas_dezenas_sequenciais,
    detectar_tres_dezenas_na_mesma_linha,
)
from msen.screener import (
    AdaptadorPadroesHistoricos,
    EvidenciaHistoricaPadrao,
    PoliticaPadraoSombra,
    carregar_configuracao_screener,
    gerar_amostra,
    simular_modo_sombra,
)


DETECTORES = {
    "PD_001": detectar_duas_dezenas_sequenciais,
    "PD_004": detectar_duas_dezenas_na_mesma_coluna,
    "PD_007": detectar_duas_dezenas_na_mesma_linha,
    "PD_008": detectar_tres_dezenas_na_mesma_linha,
}


def reconciliar_padroes(resultados, persistidos):
    """Recalcula cada padrão e informa se coincide com o banco."""

    saida = {}
    for codigo, detector in DETECTORES.items():
        calculado = calcular_estatistica_padrao(codigo, detector, resultados)
        valores = (
            calculado.num_oco,
            calculado.intervalo_medio,
            calculado.desv_padrao,
        )
        saida[codigo] = {
            "calculado": [str(item) for item in valores],
            "persistido": [str(item) for item in persistidos[codigo]],
            "reconciliado": valores == persistidos[codigo],
        }
    return saida


def simular_padroes(semente, configuracao, ocorrencias):
    """Conta detecções e decisões sombra dos quatro padrões na mesma amostra."""

    config = replace(configuracao, semente=semente)
    amostra = gerar_amostra(config)
    saida = {}
    for codigo, detector in DETECTORES.items():
        criterio = replace(
            configuracao.criterios["padroes_historicos"],
            habilitado=True,
            tolerancias={"tolerancia_ocorrencia_percentual": 3.0},
        )
        adaptador = AdaptadorPadroesHistoricos(
            codigo,
            criterio,
            PoliticaPadraoSombra(
                detector,
                EvidenciaHistoricaPadrao(
                    codigo,
                    ocorrencias[codigo],
                    3069,
                    True,
                    f"{codigo}:3069:2026-10-27",
                ),
            ),
        )
        simulacao = simular_modo_sombra(amostra, adaptador, semente=semente)
        dados = asdict(simulacao)
        dados["total_detectado_bruto"] = sum(detector(item) for item in amostra)
        saida[codigo] = dados
    return saida


def main() -> None:
    """Lê o banco sem escrever e imprime reconciliação e simulações."""

    load_dotenv()
    with abrir_conexao(carregar_configuracao_banco()) as conexao:
        with conexao.cursor() as cursor:
            cursor.execute(
                "SELECT data_resultado, numero_ap, res_01, res_02, res_03, "
                "res_04, res_05, res_06 FROM resultados ORDER BY numero_ap"
            )
            resultados = tuple(ResultadoEntrada(*linha) for linha in cursor.fetchall())
            cursor.execute(
                "SELECT padrao_cod, num_oco, intervalo_medio, desv_padrao FROM "
                "padroes_subgrupo WHERE padrao_cod = ANY(%s)",
                (list(DETECTORES),),
            )
            persistidos = {linha[0]: linha[1:] for linha in cursor.fetchall()}

    ocorrencias = {codigo: valores[0] for codigo, valores in persistidos.items()}
    raiz = Path(__file__).resolve().parents[1]
    config = carregar_configuracao_screener(raiz / "config" / "screener.toml")
    saida = {
        "total_resultados": len(resultados),
        "reconciliacao": reconciliar_padroes(resultados, persistidos),
        "simulacoes": {
            str(semente): simular_padroes(semente, config, ocorrencias)
            for semente in (20261027, 42)
        },
    }
    print(json.dumps(saida, ensure_ascii=False, indent=2))
    if not all(item["reconciliado"] for item in saida["reconciliacao"].values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
