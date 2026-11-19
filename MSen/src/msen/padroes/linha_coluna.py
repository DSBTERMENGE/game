"""Detector do padrão combinado de uma linha horizontal e uma coluna."""

from .entrada import validar_dezenas


CODIGO_UMA_LINHA_UMA_COLUNA = "PD_010"


def _posicao(dezena: int) -> tuple[int, int]:
    """Retorna linha e coluna na matriz de seis linhas por dez colunas."""

    return ((dezena - 1) // 10 + 1, (dezena - 1) % 10 + 1)


def detectar_dezenas_em_uma_linha_e_uma_coluna(
    dezenas: tuple[int, ...],
) -> bool:
    """Detecta seis dezenas cobertas pela união de uma linha e uma coluna.

    A interseção dos eixos pode estar ocupada ou vazia. Para não confundir o
    padrão com seis dezenas em uma única linha ou coluna, deve existir ao
    menos uma dezena exclusivamente no braço horizontal e outra
    exclusivamente no braço vertical.

    ``True`` identifica o padrão raro e determina a exclusão da combinação
    quando o detector estiver integrado ao funil do Screener.
    """

    pontos = tuple(_posicao(dezena) for dezena in validar_dezenas(dezenas))
    linhas = {linha for linha, _coluna in pontos}
    colunas = {coluna for _linha, coluna in pontos}

    for linha_escolhida in linhas:
        for coluna_escolhida in colunas:
            cobertas = all(
                linha == linha_escolhida or coluna == coluna_escolhida
                for linha, coluna in pontos
            )
            possui_braco_horizontal = any(
                linha == linha_escolhida and coluna != coluna_escolhida
                for linha, coluna in pontos
            )
            possui_braco_vertical = any(
                coluna == coluna_escolhida and linha != linha_escolhida
                for linha, coluna in pontos
            )
            if cobertas and possui_braco_horizontal and possui_braco_vertical:
                return True
    return False
