"""Mede assinaturas diagonais nos resultados históricos sem alterar o banco."""

from collections import Counter, defaultdict
import json

from dotenv import load_dotenv

from analisar_assinaturas_diagonais_amostra import ASSINATURAS_POSSIVEIS
from msen.config import carregar_configuracao_banco
from msen.database import abrir_conexao
from msen.padroes.diagonais import analisar_assinaturas_diagonais


def analisar_resultados() -> dict[str, object]:
    """Lê todos os resultados e calcula incidências por concurso e referência."""

    configuracao = carregar_configuracao_banco()
    with abrir_conexao(configuracao) as conexao, conexao.cursor() as cursor:
        cursor.execute(
            "SELECT numero_ap, res_01, res_02, res_03, res_04, res_05, res_06 "
            "FROM resultados ORDER BY numero_ap"
        )
        resultados = tuple(cursor.fetchall())

    total = len(resultados)
    incidencias: Counter[str] = Counter()
    por_posicao = {posicao: Counter() for posicao in range(2, 6)}
    exemplos: dict[str, list[int]] = defaultdict(list)
    sem_referencia_longa = 0
    referencias_elegiveis = 0

    for linha in resultados:
        numero_ap = linha[0]
        analise = analisar_assinaturas_diagonais(tuple(linha[1:]))
        if analise.sem_referencia_longa:
            sem_referencia_longa += 1
        codigos_do_resultado = {
            assinatura.codigo for assinatura in analise.assinaturas
        }
        incidencias.update(codigos_do_resultado)
        for codigo in codigos_do_resultado:
            if len(exemplos[codigo]) < 5:
                exemplos[codigo].append(numero_ap)
        for referencia in analise.referencias:
            if referencia.assinatura is None:
                continue
            referencias_elegiveis += 1
            por_posicao[referencia.posicao][referencia.assinatura.codigo] += 1

    def percentual(ocorrencias: int, denominador: int = total) -> float:
        if denominador == 0:
            return 0.0
        return round(ocorrencias * 100 / denominador, 6)

    distribuicao = [
        {
            "assinatura": assinatura,
            "ocorrencias": incidencias[assinatura],
            "percentual_resultados": percentual(incidencias[assinatura]),
            "exemplos_numero_ap": exemplos[assinatura],
        }
        for assinatura in sorted(
            ASSINATURAS_POSSIVEIS,
            key=lambda item: (incidencias[item], item),
        )
    ]
    diagnostico_posicoes = {
        f"P{posicao}": {
            "referencias_elegiveis": sum(contagens.values()),
            "assinaturas": [
                {
                    "assinatura": assinatura,
                    "ocorrencias": contagens[assinatura],
                }
                for assinatura in sorted(
                    ASSINATURAS_POSSIVEIS,
                    key=lambda item: (contagens[item], item),
                )
            ],
        }
        for posicao, contagens in por_posicao.items()
    }
    return {
        "total_resultados": total,
        "primeiro_numero_ap": None if not resultados else resultados[0][0],
        "ultimo_numero_ap": None if not resultados else resultados[-1][0],
        "sem_referencia_longa": {
            "ocorrencias": sem_referencia_longa,
            "percentual_resultados": percentual(sem_referencia_longa),
        },
        "referencias_elegiveis": referencias_elegiveis,
        "distribuicao_por_resultado": distribuicao,
        "diagnostico_por_posicao": diagnostico_posicoes,
    }


def main() -> None:
    load_dotenv()
    print(json.dumps(analisar_resultados(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
