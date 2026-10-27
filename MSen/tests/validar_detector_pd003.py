"""Gera uma saída auditável dos casos aprovados para o detector PD_003."""

from __future__ import annotations

import json

from msen.padroes import detectar_mais_de_tres_dezenas_sequenciais


CASOS_BOOLEANOS = (
    ("A1", (1, 2, 3, 4, 20, 40), True, "bloco de quatro"),
    ("A2", (10, 11, 12, 13, 14, 60), True, "bloco de cinco"),
    ("A3", (25, 26, 27, 28, 29, 30), True, "bloco de seis"),
    ("A4", (40, 4, 2, 20, 3, 1), True, "ordem de entrada não interfere"),
    ("A5", (9, 10, 11, 12, 30, 50), True, "sequência atravessa 10/11"),
    ("A6", (10, 20, 21, 22, 23, 24), True, "bloco no meio"),
    ("A7", (1, 2, 3, 4, 50, 51), True, "bloco de quatro e par adicional"),
    ("A8", (20, 40, 57, 58, 59, 60), True, "bloco no limite superior"),
    ("N1", (10, 25, 26, 27, 50, 58), False, "maior bloco de três"),
    ("N2", (1, 2, 3, 20, 21, 22), False, "dois blocos de três"),
    ("N3", (1, 2, 10, 11, 30, 50), False, "dois blocos de dois"),
    ("N4", (1, 2, 3, 10, 11, 30), False, "trinca e par separados"),
    ("N5", (1, 10, 20, 30, 40, 60), False, "nenhum bloco consecutivo"),
    ("N6", (1, 2, 3, 58, 59, 60), False, "60/01 não é circular"),
)

CASOS_INVALIDOS = (
    ("E1", (1, 2, 3, 4, 4, 20), ValueError, "dezena repetida"),
    ("E2", (0, 1, 2, 3, 4, 5), ValueError, "dezena abaixo de 01"),
    ("E3", (1, 2, 3, 4, 5, 61), ValueError, "dezena acima de 60"),
    ("E4", (1, 2, 3, 4, 5), ValueError, "quantidade diferente de seis"),
    ("E5", (1, 2, 3, 4, 5, "06"), TypeError, "dezena não inteira"),
    ("E6", (True, 2, 3, 4, 5, 6), TypeError, "booleano não é dezena"),
)


def avaliar_casos_pd003() -> list[dict[str, object]]:
    """Executa os vinte casos e devolve esperado, obtido, motivo e conformidade."""

    saida: list[dict[str, object]] = []
    for codigo, dezenas, esperado, motivo in CASOS_BOOLEANOS:
        obtido = detectar_mais_de_tres_dezenas_sequenciais(dezenas)
        saida.append(
            {
                "caso": codigo,
                "dezenas": list(dezenas),
                "esperado": esperado,
                "obtido": obtido,
                "motivo": motivo,
                "conforme": obtido is esperado,
            }
        )
    for codigo, dezenas, erro_esperado, motivo in CASOS_INVALIDOS:
        try:
            detectar_mais_de_tres_dezenas_sequenciais(dezenas)
        except (TypeError, ValueError) as erro:
            obtido = type(erro).__name__
        else:
            obtido = "sem erro"
        saida.append(
            {
                "caso": codigo,
                "dezenas": list(dezenas),
                "esperado": erro_esperado.__name__,
                "obtido": obtido,
                "motivo": motivo,
                "conforme": obtido == erro_esperado.__name__,
            }
        )
    return saida


def main() -> None:
    """Imprime a validação completa em JSON e falha se houver divergência."""

    casos = avaliar_casos_pd003()
    resumo = {
        "criterio": "PD_003",
        "total": len(casos),
        "conformes": sum(item["conforme"] is True for item in casos),
        "divergentes": sum(item["conforme"] is False for item in casos),
        "casos": casos,
    }
    print(json.dumps(resumo, ensure_ascii=False, indent=2))
    if resumo["divergentes"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
