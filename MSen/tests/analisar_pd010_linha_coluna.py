"""Mede o detector PD_010 no histórico e numa amostra reproduzível."""

from random import Random

from dotenv import load_dotenv

from msen.api.resultados import listar_resultados_do_banco
from msen.padroes import detectar_dezenas_em_uma_linha_e_uma_coluna


SEMENTE = 20261027
TAMANHO_AMOSTRA = 30_000


def gerar_amostra() -> tuple[tuple[int, ...], ...]:
    aleatorio = Random(SEMENTE)
    vistos: set[tuple[int, ...]] = set()
    amostra: list[tuple[int, ...]] = []
    while len(amostra) < TAMANHO_AMOSTRA:
        combinacao = tuple(sorted(aleatorio.sample(range(1, 61), 6)))
        if combinacao not in vistos:
            vistos.add(combinacao)
            amostra.append(combinacao)
    return tuple(amostra)


def resumir(nome: str, combinacoes) -> None:
    combinacoes = tuple(combinacoes)
    ocorrencias = tuple(
        item for item in combinacoes
        if detectar_dezenas_em_uma_linha_e_uma_coluna(item)
    )
    percentual = len(ocorrencias) * 100 / len(combinacoes)
    print(nome, len(combinacoes), len(ocorrencias), f"{percentual:.6f}%")
    print("EXEMPLOS", ocorrencias[:10])


if __name__ == "__main__":
    load_dotenv()
    resultados = (
        item.resultado.resultados for item in listar_resultados_do_banco()
    )
    resumir("HISTORICO", resultados)
    resumir("AMOSTRA", gerar_amostra())
