"""Valida segmentos e estatísticas do gráfico contra a geração ativa."""

from decimal import Decimal
from pathlib import Path

from dotenv import load_dotenv
import psycopg

from msen.api.frequencias import (
    _consultar_ocorrencias_reais,
    consultar_serie_frequencia,
)
from msen.config import carregar_configuracao_banco


def media(intervalos: list[int]) -> Decimal:
    return sum(map(Decimal, intervalos), Decimal(0)) / Decimal(len(intervalos))


def executar() -> None:
    load_dotenv(Path(__file__).resolve().parents[1] / ".env")
    config = carregar_configuracao_banco()
    with psycopg.connect(
        host=config.host, port=config.porta, dbname=config.nome,
        user=config.usuario, password=config.senha, sslmode=config.sslmode,
        connect_timeout=config.tempo_limite,
    ) as conexao:
        with conexao.cursor() as cursor:
            cursor.execute(
                "SELECT concurso_final FROM geracoes_frequencia_dezenas "
                "WHERE estado='ATIVA'"
            )
            concurso_final = cursor.fetchone()[0]
            for dezena in (8, 17):
                ocorrencias = _consultar_ocorrencias_reais(
                    cursor, dezena=dezena, tipo_evento="SIMPLES",
                    inicio=1, fim=concurso_final,
                )
                serie = consultar_serie_frequencia(
                    conexao, dezena=dezena, tipo_evento="SIMPLES",
                    concurso_inicial=500, concurso_final=concurso_final,
                )
                segmentos = serie["intervalos_individuais"]
                if not segmentos:
                    raise AssertionError(f"Dezena {dezena} não possui segmentos.")
                for item in segmentos:
                    if item["intervalo"] != (
                        item["numero_do_concurso"] - item["concurso_anterior"]
                    ):
                        raise AssertionError(f"Intervalo incorreto na dezena {dezena}.")
                    if not 500 <= item["concurso_inicial_visivel"] <= concurso_final:
                        raise AssertionError("Início visual fora do período.")
                    if not 500 <= item["concurso_final_visivel"] <= concurso_final:
                        raise AssertionError("Final visual fora do período.")
                primeiro = segmentos[0]
                if not (
                    primeiro["concurso_anterior"] < 500
                    <= primeiro["numero_do_concurso"]
                    and primeiro["concurso_inicial_visivel"] == 500
                ):
                    raise AssertionError(
                        f"Recorte inicial incorreto para a dezena {dezena}."
                    )
                intervalos_ate_500 = [
                    atual - anterior
                    for anterior, atual in zip(ocorrencias, ocorrencias[1:])
                    if atual <= 500
                ]
                media_api = Decimal(serie["pontos"][0]["media_intervalos"])
                if media_api != media(intervalos_ate_500).quantize(Decimal("0.000001")):
                    raise AssertionError(f"Média acumulada incorreta na dezena {dezena}.")
                valores = [item["intervalo"] for item in segmentos]
                faltantes = {1, 2, 3, 10}.difference(valores)
                if faltantes:
                    raise AssertionError(
                        f"Casos {sorted(faltantes)} ausentes na dezena {dezena}."
                    )
                if max(valores) <= 10:
                    raise AssertionError(f"Sem intervalo longo na dezena {dezena}.")
                if not any(a == b for a, b in zip(valores, valores[1:])):
                    raise AssertionError(
                        f"Sem intervalos consecutivos iguais na dezena {dezena}."
                    )
                print(
                    f"Dezena {dezena:02d}: {len(segmentos)} segmentos; "
                    f"primeiro {primeiro['concurso_anterior']}->"
                    f"{primeiro['numero_do_concurso']} recortado em 500; "
                    f"casos 1/2/3/10="
                    f"{[valores.count(n) for n in (1, 2, 3, 10)]}; "
                    f"iguais consecutivos="
                    f"{sum(a == b for a, b in zip(valores, valores[1:]))}; "
                    f"máximo {max(valores)}."
                )


if __name__ == "__main__":
    executar()
