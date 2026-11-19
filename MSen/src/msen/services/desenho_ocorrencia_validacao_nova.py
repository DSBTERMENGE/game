"""Contrato visual das ocorrências exibidas no painel 10 por 6."""

from collections import Counter, defaultdict
from dataclasses import asdict, dataclass

import psycopg

from msen.padroes import (
    calcular_categorias_diagonais,
    detectar_dezenas_em_duas_linhas,
    detectar_dezenas_em_uma_linha_e_uma_coluna,
    detectar_duas_dezenas_na_mesma_coluna,
    detectar_duas_dezenas_na_mesma_linha,
    detectar_duas_dezenas_sequenciais,
    detectar_mais_de_tres_dezenas_na_mesma_coluna,
    detectar_mais_de_tres_dezenas_na_mesma_linha,
    detectar_mais_de_tres_dezenas_sequenciais,
    detectar_tres_dezenas_na_mesma_coluna,
    detectar_tres_dezenas_na_mesma_linha,
    detectar_tres_dezenas_sequenciais,
    resolver_funcao_detectora,
)
from msen.validacao import chave_canonica


@dataclass(frozen=True, slots=True)
class SegmentoPainelValidacao:
    tipo: str
    x1: float
    y1: float
    x2: float
    y2: float


@dataclass(frozen=True, slots=True)
class DesenhoOcorrenciaValidacao:
    dezenas_marcadas: tuple[int, ...]
    segmentos: tuple[SegmentoPainelValidacao, ...]

    def como_dict(self) -> dict[str, object]:
        return {
            "dezenas_marcadas": list(self.dezenas_marcadas),
            "segmentos": [asdict(item) for item in self.segmentos],
        }


def _ponto(dezena: int) -> tuple[float, float]:
    return ((dezena - 1) % 10 + 0.5, (dezena - 1) // 10 + 0.5)


def _horizontal(linha: int) -> SegmentoPainelValidacao:
    y = linha - 0.5
    return SegmentoPainelValidacao("horizontal", 0.0, y, 10.0, y)


def _vertical(coluna: int) -> SegmentoPainelValidacao:
    x = coluna - 0.5
    return SegmentoPainelValidacao("vertical", x, 0.0, x, 6.0)


def _maior_sequencia(valores) -> int:
    ordenados = sorted(set(valores))
    maior = atual = 1
    for anterior, valor in zip(ordenados, ordenados[1:]):
        atual = atual + 1 if valor == anterior + 1 else 1
        maior = max(maior, atual)
    return maior


def _segmentos_sequenciais(dezenas) -> tuple[SegmentoPainelValidacao, ...]:
    ordenadas = sorted(dezenas)
    return tuple(
        SegmentoPainelValidacao("sequencial", *_ponto(a), *_ponto(b))
        for a, b in zip(ordenadas, ordenadas[1:])
        if b == a + 1
    )


def _segmento_diagonal(tipo: str, constante: float) -> SegmentoPainelValidacao:
    pontos = []
    if tipo == "diagonal_passo_11":
        candidatos = ((0.0, constante), (10.0, 10.0 + constante),
                      (-constante, 0.0), (6.0 - constante, 6.0))
    else:
        candidatos = ((0.0, constante), (10.0, constante - 10.0),
                      (constante, 0.0), (constante - 6.0, 6.0))
    for ponto in candidatos:
        if 0 <= ponto[0] <= 10 and 0 <= ponto[1] <= 6 and ponto not in pontos:
            pontos.append(ponto)
    return SegmentoPainelValidacao(tipo, *pontos[0], *pontos[1])


def construir_desenho_ocorrencia_validacao(
    detector,
    combinacao: tuple[int, ...],
) -> DesenhoOcorrenciaValidacao:
    """Traduz a evidência detectada em círculos e linhas de borda a borda."""

    dezenas = chave_canonica(combinacao)
    pontos = tuple((dezena, (dezena - 1) // 10 + 1, (dezena - 1) % 10 + 1)
                   for dezena in dezenas)
    segmentos: tuple[SegmentoPainelValidacao, ...]

    sequenciais = {
        detectar_duas_dezenas_sequenciais,
        detectar_tres_dezenas_sequenciais,
        detectar_mais_de_tres_dezenas_sequenciais,
    }
    linhas = {
        detectar_duas_dezenas_na_mesma_linha: 2,
        detectar_tres_dezenas_na_mesma_linha: 3,
        detectar_mais_de_tres_dezenas_na_mesma_linha: 4,
    }
    colunas = {
        detectar_duas_dezenas_na_mesma_coluna: 2,
        detectar_tres_dezenas_na_mesma_coluna: 3,
        detectar_mais_de_tres_dezenas_na_mesma_coluna: 4,
    }
    if detector in sequenciais:
        segmentos = _segmentos_sequenciais(dezenas)
    elif detector in linhas:
        minimo = linhas[detector]
        contagem = Counter(linha for _dezena, linha, _coluna in pontos)
        segmentos = tuple(_horizontal(linha) for linha, total in sorted(contagem.items())
                          if total >= minimo)
    elif detector in colunas:
        minimo = colunas[detector]
        por_coluna = defaultdict(list)
        for _dezena, linha, coluna in pontos:
            por_coluna[coluna].append(linha)
        segmentos = tuple(_vertical(coluna) for coluna, valores in sorted(por_coluna.items())
                          if _maior_sequencia(valores) >= minimo)
    elif detector is detectar_dezenas_em_duas_linhas:
        segmentos = tuple(_horizontal(linha) for linha in sorted({p[1] for p in pontos}))
    elif detector is detectar_dezenas_em_uma_linha_e_uma_coluna:
        testemunha = next(
            (linha, coluna)
            for linha in sorted({p[1] for p in pontos})
            for coluna in sorted({p[2] for p in pontos})
            if all(l == linha or c == coluna for _d, l, c in pontos)
            and any(l == linha and c != coluna for _d, l, c in pontos)
            and any(c == coluna and l != linha for _d, l, c in pontos)
        )
        segmentos = (_horizontal(testemunha[0]), _vertical(testemunha[1]))
    elif detector is calcular_categorias_diagonais:
        por_11 = Counter(coluna - linha for _d, linha, coluna in pontos)
        por_9 = Counter(coluna + linha for _d, linha, coluna in pontos)
        segmentos = tuple(
            _segmento_diagonal("diagonal_passo_11", -constante)
            for constante, total in sorted(por_11.items()) if total >= 2
        ) + tuple(
            _segmento_diagonal("diagonal_passo_9", constante - 1)
            for constante, total in sorted(por_9.items()) if total >= 2
        )
    else:
        raise ValueError("O filtro ainda não possui representação visual definida.")

    return DesenhoOcorrenciaValidacao(dezenas, segmentos)


def carregar_desenho_ocorrencia_validacao(
    conexao: psycopg.Connection,
    id_filtro: int,
    combinacao: tuple[int, ...],
) -> DesenhoOcorrenciaValidacao:
    """Resolve internamente o detector por ID e devolve somente o contrato visual."""

    if not isinstance(conexao, psycopg.Connection):
        raise TypeError("O desenho exige uma conexão Psycopg válida.")
    with conexao.transaction(), conexao.cursor() as cursor:
        cursor.execute(
            "SELECT funcao_detectora FROM padroes_subgrupo WHERE id_padrao=%s",
            (id_filtro,),
        )
        linha = cursor.fetchone()
    if linha is None:
        raise ValueError("O filtro da ocorrência não foi encontrado.")
    detector = resolver_funcao_detectora(linha[0])
    return construir_desenho_ocorrencia_validacao(detector, combinacao)
