"""Analisa a média aritmética histórica e amostral sem definir exclusões."""

from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
import json
from pathlib import Path
from statistics import mean, median, pstdev

from dotenv import load_dotenv

from msen.config import carregar_configuracao_banco
from msen.database import abrir_conexao
from msen.screener import carregar_configuracao_screener, gerar_amostra


SEIS_CASAS = Decimal("0.000001")


def _percentil(valores: tuple[Decimal, ...], percentual: Decimal) -> Decimal:
    """Calcula percentil linear entre posições de uma sequência ordenada."""

    ordenados = tuple(sorted(valores))
    posicao = Decimal(len(ordenados) - 1) * percentual
    inferior = int(posicao)
    superior = min(inferior + 1, len(ordenados) - 1)
    fracao = posicao - Decimal(inferior)
    return ordenados[inferior] + (ordenados[superior] - ordenados[inferior]) * fracao


def resumir_distribuicao(valores) -> dict[str, str | int]:
    """Resume quantidade, centro, dispersão e percentis de valores decimais."""

    fixos = tuple(Decimal(valor) for valor in valores)
    if not fixos:
        raise ValueError("A distribuição não pode estar vazia.")
    resumo: dict[str, str | int] = {"quantidade": len(fixos)}
    medidas = {
        "minimo": min(fixos),
        "p01": _percentil(fixos, Decimal("0.01")),
        "p05": _percentil(fixos, Decimal("0.05")),
        "p10": _percentil(fixos, Decimal("0.10")),
        "media_das_medias": mean(fixos),
        "mediana_das_medias": median(fixos),
        "p90": _percentil(fixos, Decimal("0.90")),
        "p95": _percentil(fixos, Decimal("0.95")),
        "p99": _percentil(fixos, Decimal("0.99")),
        "maximo": max(fixos),
        "desvio_padrao_populacional": pstdev(fixos),
    }
    resumo.update(
        (nome, str(valor.quantize(SEIS_CASAS, rounding=ROUND_HALF_UP)))
        for nome, valor in medidas.items()
    )
    return resumo


def main() -> None:
    """Compara a distribuição histórica com a amostra reproduzível de 5.000."""

    load_dotenv()
    with abrir_conexao(carregar_configuracao_banco()) as conexao:
        with conexao.cursor() as cursor:
            cursor.execute(
                "SELECT media_aritmetica_res FROM resultados ORDER BY numero_ap"
            )
            historicas = tuple(linha[0] for linha in cursor.fetchall())

    raiz = Path(__file__).resolve().parents[1]
    config = carregar_configuracao_screener(raiz / "config" / "screener.toml")
    amostrais = tuple(
        (Decimal(sum(combinacao)) / Decimal(6)).quantize(
            SEIS_CASAS, rounding=ROUND_HALF_UP
        )
        for combinacao in gerar_amostra(config)
    )
    media_historica = mean(historicas)
    limite_inferior_exemplo = media_historica * Decimal("0.80")
    limite_superior_exemplo = media_historica * Decimal("1.20")
    fora_exemplo_historico = sum(
        valor < limite_inferior_exemplo or valor > limite_superior_exemplo
        for valor in historicas
    )
    fora_exemplo_amostra = sum(
        valor < limite_inferior_exemplo or valor > limite_superior_exemplo
        for valor in amostrais
    )
    limite_p01 = _percentil(historicas, Decimal("0.01"))
    limite_p99 = _percentil(historicas, Decimal("0.99"))
    fora_percentis_historico = sum(
        valor < limite_p01 or valor > limite_p99 for valor in historicas
    )
    fora_percentis_amostra = sum(
        valor < limite_p01 or valor > limite_p99 for valor in amostrais
    )
    saida = {
        "historico": resumir_distribuicao(historicas),
        "amostra_5000": resumir_distribuicao(amostrais),
        "exemplo_nao_aprovado_mais_menos_20": {
            "limite_inferior": str(limite_inferior_exemplo.quantize(SEIS_CASAS)),
            "limite_superior": str(limite_superior_exemplo.quantize(SEIS_CASAS)),
            "historicos_fora": fora_exemplo_historico,
            "amostrais_fora": fora_exemplo_amostra,
        },
        "candidato_nao_aprovado_p01_p99": {
            "limite_inferior": str(limite_p01.quantize(SEIS_CASAS)),
            "limite_superior": str(limite_p99.quantize(SEIS_CASAS)),
            "historicos_fora": fora_percentis_historico,
            "percentual_historico_fora": str(
                (Decimal(fora_percentis_historico) * Decimal(100) / Decimal(len(historicas)))
                .quantize(SEIS_CASAS)
            ),
            "amostrais_fora": fora_percentis_amostra,
        },
    }
    print(json.dumps(saida, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
