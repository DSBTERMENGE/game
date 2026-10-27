"""Analisa a extensão do caminho aberto sem definir exclusões."""

from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
import json
from pathlib import Path
from statistics import mean
import sys

from dotenv import load_dotenv

from msen.config import carregar_configuracao_banco
from msen.database import abrir_conexao
from msen.geometria import calcular_extensao_aberta
from msen.screener import carregar_configuracao_screener, gerar_amostra

sys.path.insert(0, str(Path(__file__).resolve().parent))
from analisar_media_aritmetica import SEIS_CASAS, _percentil, resumir_distribuicao


DOZE_CASAS = Decimal("0.000000000001")


def main() -> None:
    """Compara a extensão histórica com a amostra reproduzível de 5.000."""

    load_dotenv()
    with abrir_conexao(carregar_configuracao_banco()) as conexao:
        with conexao.cursor() as cursor:
            cursor.execute(
                "SELECT extensao_aberta FROM analise_geometrica_resultado "
                "ORDER BY id_resultado"
            )
            historicas = tuple(linha[0] for linha in cursor.fetchall())

    raiz = Path(__file__).resolve().parents[1]
    config = carregar_configuracao_screener(raiz / "config" / "screener.toml")
    amostrais = tuple(
        calcular_extensao_aberta(combinacao).quantize(
            DOZE_CASAS, rounding=ROUND_HALF_UP
        )
        for combinacao in gerar_amostra(config)
    )
    limite_p01 = _percentil(historicas, Decimal("0.01")).quantize(
        SEIS_CASAS, rounding=ROUND_HALF_UP
    )
    limite_p99 = _percentil(historicas, Decimal("0.99")).quantize(
        SEIS_CASAS, rounding=ROUND_HALF_UP
    )
    historicos_abaixo = sum(valor < limite_p01 for valor in historicas)
    historicos_acima = sum(valor > limite_p99 for valor in historicas)
    amostrais_abaixo = sum(valor < limite_p01 for valor in amostrais)
    amostrais_acima = sum(valor > limite_p99 for valor in amostrais)

    centro = mean(historicas)
    exemplo_inferior = centro * Decimal("0.80")
    exemplo_superior = centro * Decimal("1.20")
    saida = {
        "historico": resumir_distribuicao(historicas),
        "amostra_5000": resumir_distribuicao(amostrais),
        "exemplo_nao_aprovado_mais_menos_20": {
            "limite_inferior": str(exemplo_inferior.quantize(SEIS_CASAS)),
            "limite_superior": str(exemplo_superior.quantize(SEIS_CASAS)),
            "historicos_fora": sum(
                valor < exemplo_inferior or valor > exemplo_superior
                for valor in historicas
            ),
            "amostrais_fora": sum(
                valor < exemplo_inferior or valor > exemplo_superior
                for valor in amostrais
            ),
        },
        "candidato_nao_aprovado_p01_p99": {
            "limite_inferior": str(limite_p01.quantize(SEIS_CASAS)),
            "limite_superior": str(limite_p99.quantize(SEIS_CASAS)),
            "historicos_abaixo": historicos_abaixo,
            "historicos_acima": historicos_acima,
            "historicos_fora": historicos_abaixo + historicos_acima,
            "percentual_historico_fora": str(
                (
                    Decimal(historicos_abaixo + historicos_acima)
                    * Decimal(100)
                    / Decimal(len(historicas))
                ).quantize(SEIS_CASAS)
            ),
            "amostrais_abaixo": amostrais_abaixo,
            "amostrais_acima": amostrais_acima,
            "amostrais_fora": amostrais_abaixo + amostrais_acima,
        },
    }
    print(json.dumps(saida, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
