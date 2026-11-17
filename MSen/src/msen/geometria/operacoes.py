"""Operações geométricas exatas compartilhadas pelos detectores de padrões."""

from fractions import Fraction

from .caminho import PontoGeometrico, SegmentoGeometrico


VetorGeometrico = tuple[Fraction, Fraction]


def calcular_vetor(
    origem: PontoGeometrico, destino: PontoGeometrico
) -> VetorGeometrico:
    """Retorna o vetor exato orientado da origem para o destino."""

    _validar_ponto(origem)
    _validar_ponto(destino)
    return destino.x - origem.x, destino.y - origem.y


def calcular_distancia_quadrada(
    primeiro: PontoGeometrico, segundo: PontoGeometrico
) -> Fraction:
    """Calcula a distância euclidiana ao quadrado sem extrair raiz."""

    delta_x, delta_y = calcular_vetor(primeiro, segundo)
    return delta_x * delta_x + delta_y * delta_y


def calcular_produto_vetorial(
    origem: PontoGeometrico,
    primeiro: PontoGeometrico,
    segundo: PontoGeometrico,
) -> Fraction:
    """Calcula o produto vetorial dos vetores origem-primeiro e origem-segundo."""

    primeiro_x, primeiro_y = calcular_vetor(origem, primeiro)
    segundo_x, segundo_y = calcular_vetor(origem, segundo)
    return primeiro_x * segundo_y - primeiro_y * segundo_x


def calcular_produto_escalar(
    origem: PontoGeometrico,
    primeiro: PontoGeometrico,
    segundo: PontoGeometrico,
) -> Fraction:
    """Calcula o produto escalar dos vetores origem-primeiro e origem-segundo."""

    primeiro_x, primeiro_y = calcular_vetor(origem, primeiro)
    segundo_x, segundo_y = calcular_vetor(origem, segundo)
    return primeiro_x * segundo_x + primeiro_y * segundo_y


def sao_colineares(
    primeiro: PontoGeometrico,
    segundo: PontoGeometrico,
    terceiro: PontoGeometrico,
) -> bool:
    """Informa se os três pontos pertencem à mesma reta."""

    return calcular_produto_vetorial(primeiro, segundo, terceiro) == 0


def sao_paralelos(
    primeiro: SegmentoGeometrico, segundo: SegmentoGeometrico
) -> bool:
    """Informa se dois segmentos não degenerados possuem direções paralelas."""

    primeiro_x, primeiro_y = _vetor_do_segmento(primeiro)
    segundo_x, segundo_y = _vetor_do_segmento(segundo)
    return primeiro_x * segundo_y - primeiro_y * segundo_x == 0


def sao_perpendiculares(
    primeiro: SegmentoGeometrico, segundo: SegmentoGeometrico
) -> bool:
    """Informa se dois segmentos não degenerados possuem direções ortogonais."""

    primeiro_x, primeiro_y = _vetor_do_segmento(primeiro)
    segundo_x, segundo_y = _vetor_do_segmento(segundo)
    return primeiro_x * segundo_x + primeiro_y * segundo_y == 0


def ponto_pertence_ao_segmento(
    ponto: PontoGeometrico, segmento: SegmentoGeometrico
) -> bool:
    """Informa se um ponto pertence ao trecho fechado de um segmento."""

    _validar_ponto(ponto)
    _validar_segmento(segmento)
    if not sao_colineares(segmento.inicio, segmento.fim, ponto):
        return False
    return (
        min(segmento.inicio.x, segmento.fim.x)
        <= ponto.x
        <= max(segmento.inicio.x, segmento.fim.x)
        and min(segmento.inicio.y, segmento.fim.y)
        <= ponto.y
        <= max(segmento.inicio.y, segmento.fim.y)
    )


def _validar_ponto(ponto: PontoGeometrico) -> None:
    if not isinstance(ponto, PontoGeometrico):
        raise TypeError("A operação geométrica exige pontos geométricos.")


def _validar_segmento(segmento: SegmentoGeometrico) -> None:
    if not isinstance(segmento, SegmentoGeometrico):
        raise TypeError("A operação geométrica exige segmentos geométricos.")
    if segmento.inicio == segmento.fim:
        raise ValueError("Um segmento geométrico não pode ter comprimento zero.")


def _vetor_do_segmento(segmento: SegmentoGeometrico) -> VetorGeometrico:
    _validar_segmento(segmento)
    return calcular_vetor(segmento.inicio, segmento.fim)
