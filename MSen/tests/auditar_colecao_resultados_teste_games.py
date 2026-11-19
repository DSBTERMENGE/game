"""Audita, sem escrita, a coleção fixa gravada no banco games."""

from collections import Counter
import json

from dotenv import load_dotenv

from msen.config import carregar_configuracao_banco
from msen.database import abrir_conexao
from msen.validacao import chave_canonica


def main() -> None:
    load_dotenv()
    configuracao = carregar_configuracao_banco()
    if configuracao.nome != "games":
        raise RuntimeError("A auditoria exige GAME_DB_NAME=games.")

    with abrir_conexao(configuracao) as conexao, conexao.cursor() as cursor:
        cursor.execute(
            "SELECT id_resultado_teste,res_01,res_02,res_03,res_04,res_05,res_06 "
            "FROM resultados_teste ORDER BY id_resultado_teste"
        )
        linhas = tuple(cursor.fetchall())

    combinacoes = tuple(tuple(linha[1:]) for linha in linhas)
    ids = tuple(linha[0] for linha in linhas)
    invalidas = tuple(
        combinacao for combinacao in combinacoes
        if len(set(combinacao)) != 6
        or any(dezena < 1 or dezena > 60 for dezena in combinacao)
    )
    chaves = tuple(chave_canonica(item) for item in combinacoes)
    repeticoes = len(chaves) - len(set(chaves))
    frequencias = Counter(dezena for item in combinacoes for dezena in item)
    faltantes = tuple(dezena for dezena in range(1, 61) if dezena not in frequencias)
    ordenadas = sum(item == tuple(sorted(item)) for item in combinacoes)

    if len(linhas) != 1_000:
        raise RuntimeError(f"Quantidade divergente: {len(linhas)}")
    if ids != tuple(range(ids[0], ids[0] + 1_000)):
        raise RuntimeError("Os identificadores da coleção não são contínuos.")
    if invalidas:
        raise RuntimeError(f"Combinações inválidas encontradas: {len(invalidas)}")
    if repeticoes:
        raise RuntimeError(f"Repetições por permutação encontradas: {repeticoes}")
    if faltantes:
        raise RuntimeError(f"Dezenas ausentes na coleção: {faltantes!r}")

    print(json.dumps({
        "total_registros": len(linhas),
        "primeiro_id": ids[0],
        "ultimo_id": ids[-1],
        "combinacoes_invalidas": len(invalidas),
        "repeticoes_por_permutacao": repeticoes,
        "dezenas_ausentes": faltantes,
        "total_dezenas_observadas": sum(frequencias.values()),
        "frequencia_media": sum(frequencias.values()) / 60,
        "menor_frequencia": min(frequencias.values()),
        "maior_frequencia": max(frequencias.values()),
        "combinacoes_acidentalmente_ordenadas": ordenadas,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
