"""Histograma e curva normal de referência para um perfil estatístico."""

from dataclasses import dataclass
from decimal import Decimal, localcontext

from .perfil_estatistico import PerfilEstatistico


CEM = Decimal(100)
PI = Decimal("3.1415926535897932384626433832795028841971693993751")


@dataclass(frozen=True, slots=True)
class ClasseHistograma:
    """Classe fechada à esquerda; a última também inclui o limite superior."""

    limite_inferior: Decimal
    limite_superior: Decimal
    frequencia: int
    percentual: Decimal


@dataclass(frozen=True, slots=True)
class PontoCurvaNormal:
    """Ponto de uma densidade normal usada somente como referência visual."""

    x: Decimal
    densidade: Decimal


@dataclass(frozen=True, slots=True)
class DistribuicaoVisual:
    """Dados reproduzíveis para desenhar histograma e referência normal."""

    classes: tuple[ClasseHistograma, ...]
    curva_normal: tuple[PontoCurvaNormal, ...]
    curva_normal_disponivel: bool


def construir_distribuicao_visual(
    perfil: PerfilEstatistico, *, quantidade_classes: int
) -> DistribuicaoVisual:
    """Agrupa a distribuição real e calcula a normal nos centros das classes."""

    if not isinstance(perfil, PerfilEstatistico):
        raise TypeError("A distribuição exige um PerfilEstatistico.")
    if (
        isinstance(quantidade_classes, bool)
        or not isinstance(quantidade_classes, int)
        or not 1 <= quantidade_classes <= 50
    ):
        raise ValueError("A quantidade de classes deve estar entre 1 e 50.")

    if perfil.minimo == perfil.maximo:
        classes = (
            ClasseHistograma(
                perfil.minimo, perfil.maximo, perfil.quantidade, Decimal("100.000000")
            ),
        )
    else:
        largura = (perfil.maximo - perfil.minimo) / Decimal(quantidade_classes)
        frequencias = [0] * quantidade_classes
        for ponto in perfil.distribuicao:
            indice = int((ponto.valor - perfil.minimo) / largura)
            indice = min(indice, quantidade_classes - 1)
            frequencias[indice] += ponto.frequencia
        classes = tuple(
            ClasseHistograma(
                limite_inferior=perfil.minimo + largura * indice,
                limite_superior=(
                    perfil.maximo
                    if indice == quantidade_classes - 1
                    else perfil.minimo + largura * (indice + 1)
                ),
                frequencia=frequencia,
                percentual=(
                    Decimal(frequencia) * CEM / Decimal(perfil.quantidade)
                ).quantize(Decimal("0.000001")),
            )
            for indice, frequencia in enumerate(frequencias)
        )

    if perfil.desvio_padrao_populacional == 0:
        return DistribuicaoVisual(classes, (), False)

    with localcontext() as contexto:
        contexto.prec = 50
        desvio = perfil.desvio_padrao_populacional
        normalizador = desvio * (Decimal(2) * PI).sqrt()
        curva = tuple(
            PontoCurvaNormal(
                x=(classe.limite_inferior + classe.limite_superior) / Decimal(2),
                densidade=(
                    -Decimal("0.5")
                    * (
                        (
                            (classe.limite_inferior + classe.limite_superior)
                            / Decimal(2)
                            - perfil.media
                        )
                        / desvio
                    )
                    ** 2
                ).exp()
                / normalizador,
            )
            for classe in classes
        )
    return DistribuicaoVisual(classes, curva, True)
