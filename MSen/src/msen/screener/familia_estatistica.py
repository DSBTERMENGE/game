"""Família estatística do funil extensível, sem duplicar soma e média."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from msen.calculos import (
    calcular_desvio_padrao_media,
    calcular_media_aritmetica,
    calcular_mediana,
    calcular_soma,
)
from msen.modelos import ResultadoEntrada

from .contrato_extensivel import DecisaoFiltro, DefinicaoFamilia, DefinicaoFiltro
from .gerador import Combinacao


class ErroFamiliaEstatistica(ValueError):
    """Indica uma faixa estatística inválida ou ambígua."""

    def __init__(self, codigo: str, mensagem: str) -> None:
        super().__init__(mensagem)
        self.codigo = codigo


@dataclass(frozen=True, slots=True)
class FaixaEstatistica:
    """Intervalo fechado: os dois limites pertencem à faixa aceita."""

    limite_inferior: Decimal
    limite_superior: Decimal

    @classmethod
    def criar(
        cls, limite_inferior: Decimal | int | str, limite_superior: Decimal | int | str
    ) -> FaixaEstatistica:
        """Converte valores exatos e recusa limites invertidos ou não finitos."""

        try:
            inferior = Decimal(limite_inferior)
            superior = Decimal(limite_superior)
        except Exception as erro:
            raise ErroFamiliaEstatistica(
                "LIMITE_INVALIDO", "Os limites devem ser números decimais exatos."
            ) from erro
        if not inferior.is_finite() or not superior.is_finite():
            raise ErroFamiliaEstatistica(
                "LIMITE_INVALIDO", "Os limites devem ser finitos."
            )
        if inferior > superior:
            raise ErroFamiliaEstatistica(
                "FAIXA_INVERTIDA", "O limite inferior não pode superar o superior."
            )
        return cls(inferior, superior)

    def contem(self, valor: Decimal | int) -> bool:
        """Aceita valores nos limites e em qualquer ponto entre eles."""

        decimal = valor if isinstance(valor, Decimal) else Decimal(valor)
        return self.limite_inferior <= decimal <= self.limite_superior


def _resultado_validado(combinacao: Combinacao) -> ResultadoEntrada:
    """Adapta a combinação ao modelo usado pelas funções oficiais de cálculo."""

    return ResultadoEntrada.criar(
        data_resultado=date(2000, 1, 1), numero_ap=1, resultados=combinacao
    )


def _decisao(
    codigo: str, nome_valor: str, valor: Decimal | int, faixa: FaixaEstatistica
) -> DecisaoFiltro:
    aprovada = faixa.contem(valor)
    return DecisaoFiltro.criar(
        codigo_filtro=codigo,
        aprovada=aprovada,
        motivo="DENTRO_DA_FAIXA" if aprovada else "FORA_DA_FAIXA",
        evidencias={
            nome_valor: format(valor, "f") if isinstance(valor, Decimal) else valor,
            "limite_inferior": format(faixa.limite_inferior, "f"),
            "limite_superior": format(faixa.limite_superior, "f"),
            "intervalo": "fechado",
        },
    )


def criar_familia_estatistica(
    *,
    faixa_soma: FaixaEstatistica,
    faixa_mediana: FaixaEstatistica,
    faixa_desvio_padrao: FaixaEstatistica,
    ordem: int = 1,
) -> DefinicaoFamilia:
    """Monta os filtros estatísticos na ordem e com exclusões líquidas.

    Soma e média formam um único filtro porque `média = soma / 6`. A decisão é
    tomada pela faixa da soma e a média equivalente é registrada como evidência,
    impedindo que a mesma condição seja contabilizada duas vezes.
    """

    faixas = (faixa_soma, faixa_mediana, faixa_desvio_padrao)
    if any(not isinstance(item, FaixaEstatistica) for item in faixas):
        raise TypeError("Todas as faixas devem ser FaixaEstatistica.")

    def avaliar_soma_media(combinacao: Combinacao) -> DecisaoFiltro:
        resultado = _resultado_validado(combinacao)
        soma = calcular_soma(resultado)
        media = calcular_media_aritmetica(resultado)
        decisao = _decisao("EST_SOMA_MEDIA", "soma", soma, faixa_soma)
        evidencias = dict(decisao.evidencias)
        evidencias.update({
            "media_equivalente": format(media, "f"),
            "limite_inferior_media_equivalente": format(
                faixa_soma.limite_inferior / Decimal(6), "f"
            ),
            "limite_superior_media_equivalente": format(
                faixa_soma.limite_superior / Decimal(6), "f"
            ),
            "relacao": "media = soma / 6",
            "contabilizacao": "unica",
        })
        return DecisaoFiltro.criar(
            codigo_filtro=decisao.codigo_filtro,
            aprovada=decisao.aprovada,
            motivo=decisao.motivo,
            evidencias=evidencias,
        )

    def avaliar_mediana(combinacao: Combinacao) -> DecisaoFiltro:
        valor = calcular_mediana(_resultado_validado(combinacao))
        return _decisao("EST_MEDIANA", "mediana", valor, faixa_mediana)

    def avaliar_desvio(combinacao: Combinacao) -> DecisaoFiltro:
        valor = calcular_desvio_padrao_media(_resultado_validado(combinacao))
        return _decisao(
            "EST_DESVIO_PADRAO", "desvio_padrao_populacional", valor,
            faixa_desvio_padrao,
        )

    return DefinicaoFamilia(
        "ESTATISTICA",
        "Valores estatísticos",
        ordem,
        (
            DefinicaoFiltro("EST_SOMA_MEDIA", "Soma e média", 1, avaliar_soma_media),
            DefinicaoFiltro("EST_MEDIANA", "Mediana", 2, avaliar_mediana),
            DefinicaoFiltro(
                "EST_DESVIO_PADRAO", "Desvio-padrão populacional", 3, avaliar_desvio
            ),
        ),
    )
