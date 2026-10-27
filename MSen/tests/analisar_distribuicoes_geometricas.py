"""Lê e resume as distribuições geométricas do database local games."""

from decimal import Decimal
import json
import sys

from dotenv import load_dotenv

from msen.config import carregar_configuracao_banco
from msen.database import abrir_conexao


MEDIDAS = (
    "extensao_aberta",
    "perimetro_fechado",
    "area_total",
    "centro_gravidade_x",
    "centro_gravidade_y",
)


def _texto(valor: Decimal | None) -> str | None:
    return None if valor is None else format(valor, "f")


def analisar() -> dict[str, object]:
    """Calcula medidas descritivas sem modificar o histórico local.

    Returns:
        Quantidade, distribuições contínuas e frequência por número de regiões.

    Regra:
        A consulta recusa qualquer destino diferente do database `games`.
    """

    configuracao = carregar_configuracao_banco()
    if configuracao.nome != "games":
        raise RuntimeError("A análise histórica exige GAME_DB_NAME=games.")
    distribuicoes: dict[str, dict[str, str | None]] = {}
    with abrir_conexao(configuracao) as conexao:
        with conexao.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM analise_geometrica_resultado")
            quantidade = cursor.fetchone()[0]
            for coluna in MEDIDAS:
                cursor.execute(
                    f"SELECT MIN({coluna}), MAX({coluna}), AVG({coluna}), "
                    f"PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY {coluna}), "
                    f"STDDEV_POP({coluna}) FROM analise_geometrica_resultado"
                )
                minimo, maximo, media, mediana, desvio = cursor.fetchone()
                distribuicoes[coluna] = {
                    "minimo": _texto(minimo),
                    "maximo": _texto(maximo),
                    "media": _texto(media),
                    "mediana": _texto(mediana),
                    "desvio_padrao_populacional": _texto(desvio),
                }
            cursor.execute(
                "SELECT quantidade_regioes, COUNT(*) "
                "FROM analise_geometrica_resultado "
                "GROUP BY quantidade_regioes ORDER BY quantidade_regioes"
            )
            regioes = {
                str(quantidade_regioes): ocorrencias
                for quantidade_regioes, ocorrencias in cursor.fetchall()
            }
    if quantidade != 3069 or sum(regioes.values()) != quantidade:
        raise RuntimeError("A distribuição não cobre integralmente os 3.069 resultados.")
    return {
        "resultados": quantidade,
        "medidas": distribuicoes,
        "quantidade_regioes": regioes,
    }


def main() -> None:
    """Exige confirmação de leitura do banco local antes de gerar o resumo."""

    load_dotenv()
    if sys.argv[1:] != ["CONFIRMAR_LEITURA_GAMES"]:
        raise SystemExit(
            "Uso: analisar_distribuicoes_geometricas.py CONFIRMAR_LEITURA_GAMES"
        )
    print(json.dumps(analisar(), ensure_ascii=False))


if __name__ == "__main__":
    main()
