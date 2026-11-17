"""Decisão categórica diagonal baseada numa fotografia histórica."""

from dataclasses import dataclass
from decimal import Decimal

from msen.padroes import (
    CATEGORIA_SEM_REFERENCIA_LONGA,
    FotografiaHistoricaDiagonal,
    analisar_assinaturas_diagonais,
)

from .configuracao import validar_limite_raridade
from .contrato_extensivel import DecisaoFiltro, DefinicaoFamilia, DefinicaoFiltro
from .gerador import Combinacao


CODIGO_FILTRO_DIAGONAL = "PAD_PG_004"


@dataclass(frozen=True, slots=True)
class ComparacaoCategoriaDiagonal:
    """Compara uma categoria calculada com a fotografia e o limite."""

    codigo: str
    encontrada: bool
    ocorrencias: int
    denominador: int
    percentual: Decimal
    limite: Decimal
    rara: bool


def _categorias_da_combinacao(combinacao: Combinacao) -> tuple[str, ...]:
    analise = analisar_assinaturas_diagonais(combinacao)
    if analise.sem_referencia_longa:
        return (CATEGORIA_SEM_REFERENCIA_LONGA,)
    return tuple(item.codigo for item in analise.assinaturas)


def avaliar_filtro_diagonal(
    combinacao: Combinacao,
    fotografia: FotografiaHistoricaDiagonal,
    limite_raridade: Decimal | int | float | str,
) -> DecisaoFiltro:
    """Produz uma única decisão a partir de todas as categorias calculadas."""

    if not isinstance(fotografia, FotografiaHistoricaDiagonal):
        raise TypeError("fotografia deve ser uma FotografiaHistoricaDiagonal.")
    limite = validar_limite_raridade(limite_raridade)
    categorias = _categorias_da_combinacao(combinacao)
    comparacoes: list[ComparacaoCategoriaDiagonal] = []
    for codigo in categorias:
        try:
            incidencia = fotografia.obter(codigo)
        except KeyError:
            encontrada = False
            ocorrencias = 0
            percentual = Decimal("0.000000")
        else:
            encontrada = True
            ocorrencias = incidencia.ocorrencias
            percentual = incidencia.percentual
        comparacoes.append(
            ComparacaoCategoriaDiagonal(
                codigo=codigo,
                encontrada=encontrada,
                ocorrencias=ocorrencias,
                denominador=fotografia.total_resultados,
                percentual=percentual,
                limite=limite,
                rara=not encontrada or percentual < limite,
            )
        )

    finais = tuple(comparacoes)
    raras = tuple(item.codigo for item in finais if item.rara)
    return DecisaoFiltro.criar(
        codigo_filtro=CODIGO_FILTRO_DIAGONAL,
        aprovada=not raras,
        motivo=(
            "ARRANJO_DIAGONAL_RARO"
            if raras
            else "ARRANJOS_DIAGONAIS_ACEITOS"
        ),
        evidencias={
            "grupo_cod": "PG_004",
            "padrao_cod": "PD_013",
            "categorias": categorias,
            "categorias_raras": raras,
            "comparacoes": finais,
            "limite_raridade": format(limite, "f"),
            "denominador_historico": fotografia.total_resultados,
            "identificacao_carga": fotografia.identificacao_carga,
            "versao_calculo": fotografia.versao_calculo,
        },
    )


def acrescentar_filtro_diagonal(
    familia_padroes: DefinicaoFamilia,
    fotografia: FotografiaHistoricaDiagonal,
    limite_raridade: Decimal | int | float | str,
) -> DefinicaoFamilia:
    """Acrescenta uma única avaliação diagonal ao fim da família de padrões."""

    if not isinstance(familia_padroes, DefinicaoFamilia):
        raise TypeError("familia_padroes deve ser uma DefinicaoFamilia.")
    if familia_padroes.codigo != "PADROES":
        raise ValueError("O filtro diagonal pertence à família PADROES.")
    if not isinstance(fotografia, FotografiaHistoricaDiagonal):
        raise TypeError("fotografia deve ser uma FotografiaHistoricaDiagonal.")
    limite = validar_limite_raridade(limite_raridade)
    if any(
        filtro.codigo == CODIGO_FILTRO_DIAGONAL
        for filtro in familia_padroes.filtros
    ):
        raise ValueError("O filtro diagonal já pertence à família.")

    def avaliar(combinacao: Combinacao) -> DecisaoFiltro:
        return avaliar_filtro_diagonal(combinacao, fotografia, limite)

    ordem = max((filtro.ordem for filtro in familia_padroes.filtros), default=0) + 1
    diagonal = DefinicaoFiltro(
        CODIGO_FILTRO_DIAGONAL,
        "PG_004 · Arranjos diagonais",
        ordem,
        avaliar,
    )
    return DefinicaoFamilia(
        familia_padroes.codigo,
        familia_padroes.nome,
        familia_padroes.ordem,
        (*familia_padroes.filtros, diagonal),
    )
