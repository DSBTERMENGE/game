"""Compara oráculo independente e analisador oficial nas amostras ativas."""

from collections import Counter
import hashlib
import inspect
import json
import sys

from dotenv import load_dotenv

from msen.config import carregar_configuracao_banco
from msen.database import abrir_conexao
from msen.validacao import criar_definicao_criterio_diagonal
from referencia_independente_diagonais import (
    calcular_referencia_categorias_diagonais,
)


def comparar() -> dict[str, object]:
    configuracao = carregar_configuracao_banco()
    if configuracao.nome != "games":
        raise RuntimeError("A comparação exige GAME_DB_NAME=games.")
    with abrir_conexao(configuracao) as conexao, conexao.cursor() as cursor:
        cursor.execute(
            "SELECT r.numero_ap, r.res_01, r.res_02, r.res_03, r.res_04, "
            "r.res_05, r.res_06 FROM amostras_validacao a "
            "JOIN resultados r USING (id_resultado) WHERE a.ativo ORDER BY a.ordem"
        )
        amostras = tuple(cursor.fetchall())
    if not amostras:
        raise AssertionError("Não existem amostras ativas para comparar.")

    oficial = criar_definicao_criterio_diagonal().funcao
    distribuicao: Counter[str] = Counter()
    divergencias = []
    for numero_ap, *dezenas in amostras:
        entrada = tuple(dezenas)
        esperado = calcular_referencia_categorias_diagonais(entrada)
        calculado = oficial(entrada)
        distribuicao[esperado] += 1
        if esperado != calculado:
            divergencias.append({
                "numero_ap": numero_ap,
                "dezenas": entrada,
                "referencia": esperado,
                "oficial": calculado,
            })
    if divergencias:
        raise AssertionError(f"Foram encontradas divergências: {divergencias[:5]!r}.")

    fonte = inspect.getsource(calcular_referencia_categorias_diagonais)
    return {
        "amostras_ativas": len(amostras),
        "divergencias": 0,
        "categorias_distintas": len(distribuicao),
        "distribuicao": dict(sorted(distribuicao.items())),
        "assinatura_referencia_sha256": hashlib.sha256(
            fonte.encode("utf-8")
        ).hexdigest(),
    }


def main() -> None:
    load_dotenv()
    if sys.argv[1:] != ["CONFIRMAR_LEITURA_GAMES"]:
        raise SystemExit(
            "Uso: comparar_referencia_independente_diagonal_games.py "
            "CONFIRMAR_LEITURA_GAMES"
        )
    print(json.dumps(comparar(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
