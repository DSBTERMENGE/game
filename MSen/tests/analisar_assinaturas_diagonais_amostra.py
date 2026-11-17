"""Estima a incidência das assinaturas diagonais em combinações únicas."""

from collections import Counter
import json
import random
import sys
from time import perf_counter

from msen.padroes.diagonais import analisar_assinaturas_diagonais


SEMENTE_PADRAO = 20261117
TAMANHO_PADRAO = 30_000
ASSINATURAS_POSSIVEIS = tuple(
    f"{direita}D{esquerda}E"
    for direita in range(6)
    for esquerda in range(6 - direita)
)


def gerar_combinacoes_unicas(
    quantidade: int, semente: int
) -> tuple[tuple[int, ...], ...]:
    """Gera uma amostra uniforme reproduzível sem combinações repetidas."""

    if isinstance(quantidade, bool) or not isinstance(quantidade, int):
        raise TypeError("A quantidade da amostra deve ser um número inteiro.")
    if quantidade <= 0:
        raise ValueError("A quantidade da amostra deve ser positiva.")
    gerador = random.Random(semente)
    combinacoes: set[tuple[int, ...]] = set()
    while len(combinacoes) < quantidade:
        combinacoes.add(tuple(sorted(gerador.sample(range(1, 61), 6))))
    return tuple(sorted(combinacoes))


def analisar_amostra(
    quantidade: int = TAMANHO_PADRAO,
    semente: int = SEMENTE_PADRAO,
) -> dict[str, object]:
    """Calcula incidências por combinação e diagnósticos por posição."""

    inicio = perf_counter()
    combinacoes = gerar_combinacoes_unicas(quantidade, semente)
    incidencias: Counter[str] = Counter()
    incidencias_por_posicao = {
        posicao: Counter() for posicao in range(2, 6)
    }
    sem_referencia_longa = 0

    for combinacao in combinacoes:
        analise = analisar_assinaturas_diagonais(combinacao)
        if analise.sem_referencia_longa:
            sem_referencia_longa += 1
        incidencias.update(assinatura.codigo for assinatura in analise.assinaturas)
        for referencia in analise.referencias:
            if referencia.assinatura is not None:
                incidencias_por_posicao[referencia.posicao][
                    referencia.assinatura.codigo
                ] += 1

    def percentual(ocorrencias: int) -> float:
        return round(ocorrencias * 100 / quantidade, 6)

    distribuicao = [
        {
            "assinatura": assinatura,
            "ocorrencias": ocorrencias,
            "percentual": percentual(ocorrencias),
        }
        for assinatura, ocorrencias in sorted(
            (
                (assinatura, incidencias[assinatura])
                for assinatura in ASSINATURAS_POSSIVEIS
            ),
            key=lambda item: (item[1], item[0]),
        )
    ]
    posicoes = {
        f"P{posicao}": [
            {
                "assinatura": assinatura,
                "ocorrencias": ocorrencias,
                "percentual": percentual(ocorrencias),
            }
            for assinatura, ocorrencias in sorted(
                contagens.items(), key=lambda item: (item[1], item[0])
            )
        ]
        for posicao, contagens in incidencias_por_posicao.items()
    }
    return {
        "semente": semente,
        "tamanho_amostra": quantidade,
        "combinacoes_unicas": len(combinacoes),
        "sem_referencia_longa": {
            "ocorrencias": sem_referencia_longa,
            "percentual": percentual(sem_referencia_longa),
        },
        "distribuicao_por_combinacao": distribuicao,
        "diagnostico_por_posicao": posicoes,
        "tempo_segundos": round(perf_counter() - inicio, 6),
    }


def main() -> None:
    quantidade = TAMANHO_PADRAO if len(sys.argv) < 2 else int(sys.argv[1])
    semente = SEMENTE_PADRAO if len(sys.argv) < 3 else int(sys.argv[2])
    print(
        json.dumps(
            analisar_amostra(quantidade, semente),
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
