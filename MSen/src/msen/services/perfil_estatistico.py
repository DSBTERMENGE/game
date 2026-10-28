"""Perfil estatístico genérico para qualquer parâmetro numérico histórico."""

from __future__ import annotations

from collections import Counter
from collections.abc import Iterable
from dataclasses import dataclass
from decimal import Decimal, localcontext


SEIS_CASAS = Decimal("0.000001")
CEM = Decimal(100)


class ErroPerfilEstatistico(ValueError):
    """Informa uma entrada previsivelmente inválida no perfil estatístico."""

    def __init__(self, codigo: str, mensagem: str) -> None:
        super().__init__(mensagem)
        self.codigo = codigo


@dataclass(frozen=True, slots=True)
class PontoDistribuicao:
    """Frequência observada de um valor na distribuição empírica."""

    valor: Decimal
    frequencia: int
    percentual: Decimal


@dataclass(frozen=True, slots=True)
class PerfilEstatistico:
    """Resumo imutável de uma série numérica não vazia."""

    quantidade: int
    media: Decimal
    desvio_padrao_populacional: Decimal
    minimo: Decimal
    maximo: Decimal
    distribuicao: tuple[PontoDistribuicao, ...]


@dataclass(frozen=True, slots=True)
class FaixaPerfil:
    """Limites inclusivos produzidos a partir de um perfil histórico."""

    metodo: str
    limite_inferior: Decimal
    limite_superior: Decimal
    parametro_inferior: Decimal
    parametro_superior: Decimal

    def contem(self, valor: int | Decimal) -> bool:
        """Informa se um valor finito está dentro da faixa, inclusive limites."""

        normalizado = _como_decimal(valor, nome="valor")
        return self.limite_inferior <= normalizado <= self.limite_superior


def _como_decimal(valor: int | Decimal, *, nome: str) -> Decimal:
    if isinstance(valor, bool) or not isinstance(valor, (int, Decimal)):
        raise TypeError(f"{nome} deve ser int ou Decimal.")
    convertido = valor if isinstance(valor, Decimal) else Decimal(valor)
    if not convertido.is_finite():
        raise ErroPerfilEstatistico(
            "VALOR_NAO_FINITO", f"{nome} deve ser um número finito."
        )
    return convertido


def _validar_parametro_nao_negativo(valor: int | Decimal, *, nome: str) -> Decimal:
    convertido = _como_decimal(valor, nome=nome)
    if convertido < 0:
        raise ErroPerfilEstatistico(
            "PARAMETRO_NEGATIVO", f"{nome} não pode ser negativo."
        )
    return convertido


def calcular_perfil_estatistico(
    valores: Iterable[int | Decimal],
) -> PerfilEstatistico:
    """Calcula centro, dispersão, extremos e distribuição empírica.

    O desvio é populacional porque a série recebida representa toda a janela
    histórica escolhida, não uma estimativa amostral dela.
    """

    try:
        normalizados = tuple(_como_decimal(valor, nome="valor") for valor in valores)
    except TypeError as erro:
        if "iterable" in str(erro):
            raise TypeError("Os valores do perfil devem ser iteráveis.") from erro
        raise
    if not normalizados:
        raise ErroPerfilEstatistico(
            "SERIE_VAZIA", "O perfil exige ao menos um valor."
        )

    with localcontext() as contexto:
        contexto.prec = 50
        quantidade = len(normalizados)
        divisor = Decimal(quantidade)
        media = sum(normalizados, start=Decimal(0)) / divisor
        variancia = (
            sum(
                ((valor - media) ** 2 for valor in normalizados),
                start=Decimal(0),
            )
            / divisor
        )
        desvio = variancia.sqrt()
        contagens = Counter(normalizados)
        distribuicao = tuple(
            PontoDistribuicao(
                valor=valor,
                frequencia=frequencia,
                percentual=(Decimal(frequencia) * CEM / divisor).quantize(SEIS_CASAS),
            )
            for valor, frequencia in sorted(contagens.items())
        )
        return PerfilEstatistico(
            quantidade=quantidade,
            media=media,
            desvio_padrao_populacional=desvio,
            minimo=min(normalizados),
            maximo=max(normalizados),
            distribuicao=distribuicao,
        )


def calcular_faixa_percentual_media(
    perfil: PerfilEstatistico,
    *,
    percentual_inferior: int | Decimal,
    percentual_superior: int | Decimal,
) -> FaixaPerfil:
    """Cria margens percentuais independentes abaixo e acima da média.

    A margem usa o valor absoluto da média, mantendo a ordem dos limites mesmo
    para séries negativas. Percentuais maiores que 100 são válidos para estudos.
    """

    if not isinstance(perfil, PerfilEstatistico):
        raise TypeError("A faixa exige um PerfilEstatistico.")
    inferior = _validar_parametro_nao_negativo(
        percentual_inferior, nome="percentual_inferior"
    )
    superior = _validar_parametro_nao_negativo(
        percentual_superior, nome="percentual_superior"
    )
    referencia = abs(perfil.media)
    return FaixaPerfil(
        metodo="percentual_media",
        limite_inferior=perfil.media - (referencia * inferior / CEM),
        limite_superior=perfil.media + (referencia * superior / CEM),
        parametro_inferior=inferior,
        parametro_superior=superior,
    )


def calcular_faixa_desvio_padrao(
    perfil: PerfilEstatistico,
    *,
    multiplicador_inferior: int | Decimal,
    multiplicador_superior: int | Decimal,
) -> FaixaPerfil:
    """Cria margens independentes em desvios-padrão abaixo e acima da média."""

    if not isinstance(perfil, PerfilEstatistico):
        raise TypeError("A faixa exige um PerfilEstatistico.")
    inferior = _validar_parametro_nao_negativo(
        multiplicador_inferior, nome="multiplicador_inferior"
    )
    superior = _validar_parametro_nao_negativo(
        multiplicador_superior, nome="multiplicador_superior"
    )
    return FaixaPerfil(
        metodo="desvio_padrao",
        limite_inferior=perfil.media - perfil.desvio_padrao_populacional * inferior,
        limite_superior=perfil.media + perfil.desvio_padrao_populacional * superior,
        parametro_inferior=inferior,
        parametro_superior=superior,
    )
