"""Quadro contábil consolidado do funil extensível em três famílias."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP

from .contrato_extensivel import RelatorioFunilExtensivel
from .gerador import TOTAL_COMBINACOES


SEIS_CASAS = Decimal("0.000001")


class ErroQuadroConsolidado(ValueError):
    """Indica divergência contábil no relatório recebido."""

    def __init__(self, codigo: str, mensagem: str) -> None:
        super().__init__(mensagem)
        self.codigo = codigo


@dataclass(frozen=True, slots=True)
class LinhaFiltroConsolidada:
    """Efeito líquido de um filtro sobre o saldo que recebeu."""

    codigo: str
    nome: str
    ordem: int
    entrada: int
    avaliacoes: int
    exclusoes: int
    saldo: int
    percentual_total_inicial: Decimal
    percentual_saldo_recebido: Decimal


@dataclass(frozen=True, slots=True)
class LinhaFamiliaConsolidada:
    """Subtotal de uma família e suas linhas individuais."""

    codigo: str
    nome: str
    ordem: int
    entrada: int
    exclusoes: int
    saldo: int
    percentual_total_inicial: Decimal
    percentual_saldo_recebido: Decimal
    filtros: tuple[LinhaFiltroConsolidada, ...]


@dataclass(frozen=True, slots=True)
class QuadroConsolidado:
    """Visão única e reconciliada de toda a execução do screener."""

    tipo_escopo: str
    total_universo: int
    total_analisado: int
    total_excluido: int
    total_aprovado: int
    percentual_excluido: Decimal
    percentual_aprovado: Decimal
    familias: tuple[LinhaFamiliaConsolidada, ...]
    reconciliado: bool


def _percentual(quantidade: int, base: int) -> Decimal:
    if base == 0:
        return Decimal("0.000000")
    return (Decimal(quantidade) * Decimal(100) / Decimal(base)).quantize(
        SEIS_CASAS, rounding=ROUND_HALF_UP
    )


def criar_quadro_consolidado(
    relatorio: RelatorioFunilExtensivel,
    *,
    tipo_escopo: str,
    total_universo: int = TOTAL_COMBINACOES,
) -> QuadroConsolidado:
    """Valida todas as transições e monta o quadro sem recalcular filtros."""

    if not isinstance(relatorio, RelatorioFunilExtensivel):
        raise TypeError("relatorio deve ser RelatorioFunilExtensivel.")
    if tipo_escopo not in {"amostra", "integral"}:
        raise ErroQuadroConsolidado(
            "ESCOPO_INVALIDO", "O escopo deve ser amostra ou integral."
        )
    if isinstance(total_universo, bool) or not isinstance(total_universo, int):
        raise TypeError("total_universo deve ser inteiro.")
    if total_universo < 0 or relatorio.total_inicial > total_universo:
        raise ErroQuadroConsolidado(
            "UNIVERSO_INVALIDO", "O universo não pode ser menor que o total analisado."
        )
    if tipo_escopo == "integral" and relatorio.total_inicial != total_universo:
        raise ErroQuadroConsolidado(
            "INTEGRAL_INCOMPLETO", "O escopo integral deve analisar todo o universo."
        )
    if not relatorio.reconciliado:
        raise ErroQuadroConsolidado(
            "TOTAL_DIVERGENTE", "Total analisado não fecha com excluídas e aprovadas."
        )
    codigos_familias = tuple(item.codigo_familia for item in relatorio.familias)
    if codigos_familias != ("ESTATISTICA", "GEOMETRIA", "PADROES"):
        raise ErroQuadroConsolidado(
            "FAMILIAS_DIVERGENTES",
            "O quadro exige estatística, geometria e padrões nesta ordem.",
        )

    saldo_global = relatorio.total_inicial
    familias: list[LinhaFamiliaConsolidada] = []
    for familia in relatorio.familias:
        if familia.entrada != saldo_global:
            raise ErroQuadroConsolidado(
                "ENTRADA_FAMILIA_DIVERGENTE",
                "A entrada da família não coincide com o saldo anterior.",
            )
        saldo_filtro = familia.entrada
        filtros: list[LinhaFiltroConsolidada] = []
        for filtro in familia.filtros:
            if filtro.avaliacoes != saldo_filtro:
                raise ErroQuadroConsolidado(
                    "AVALIACOES_DIVERGENTES",
                    "O filtro não avaliou exatamente o saldo que recebeu.",
                )
            esperado = saldo_filtro - filtro.exclusoes
            if filtro.exclusoes < 0 or filtro.saldo != esperado:
                raise ErroQuadroConsolidado(
                    "SALDO_FILTRO_DIVERGENTE", "O saldo do filtro não reconcilia."
                )
            percentual_inicial = _percentual(filtro.exclusoes, relatorio.total_inicial)
            percentual_recebido = _percentual(filtro.exclusoes, saldo_filtro)
            if (
                filtro.percentual_total_inicial != percentual_inicial
                or filtro.percentual_saldo_recebido != percentual_recebido
            ):
                raise ErroQuadroConsolidado(
                    "PERCENTUAL_FILTRO_DIVERGENTE",
                    "Os percentuais do filtro não reconciliam com suas contagens.",
                )
            filtros.append(
                LinhaFiltroConsolidada(
                    filtro.codigo_filtro, filtro.nome_filtro, filtro.ordem,
                    saldo_filtro, filtro.avaliacoes, filtro.exclusoes, filtro.saldo,
                    percentual_inicial, percentual_recebido,
                )
            )
            saldo_filtro = filtro.saldo
        exclusoes_familia = familia.entrada - saldo_filtro
        if (
            familia.exclusoes != exclusoes_familia
            or familia.saldo != saldo_filtro
            or sum(item.exclusoes for item in filtros) != familia.exclusoes
        ):
            raise ErroQuadroConsolidado(
                "SUBTOTAL_FAMILIA_DIVERGENTE", "O subtotal da família não reconcilia."
            )
        percentual_inicial = _percentual(familia.exclusoes, relatorio.total_inicial)
        percentual_recebido = _percentual(familia.exclusoes, familia.entrada)
        if (
            familia.percentual_total_inicial != percentual_inicial
            or familia.percentual_saldo_recebido != percentual_recebido
        ):
            raise ErroQuadroConsolidado(
                "PERCENTUAL_FAMILIA_DIVERGENTE",
                "Os percentuais da família não reconciliam com seu subtotal.",
            )
        familias.append(
            LinhaFamiliaConsolidada(
                familia.codigo_familia, familia.nome_familia, familia.ordem,
                familia.entrada, familia.exclusoes, familia.saldo,
                percentual_inicial, percentual_recebido, tuple(filtros),
            )
        )
        saldo_global = familia.saldo
    if saldo_global != relatorio.total_aprovado:
        raise ErroQuadroConsolidado(
            "SALDO_FINAL_DIVERGENTE", "O último saldo difere do total aprovado."
        )
    return QuadroConsolidado(
        tipo_escopo,
        total_universo,
        relatorio.total_inicial,
        relatorio.total_excluido,
        relatorio.total_aprovado,
        _percentual(relatorio.total_excluido, relatorio.total_inicial),
        _percentual(relatorio.total_aprovado, relatorio.total_inicial),
        tuple(familias),
        True,
    )


def serializar_quadro_consolidado(quadro: QuadroConsolidado) -> dict[str, object]:
    """Produz dados simples para a futura API e interface expansível."""

    if not isinstance(quadro, QuadroConsolidado):
        raise TypeError("quadro deve ser QuadroConsolidado.")
    return {
        "escopo": {
            "tipo": quadro.tipo_escopo,
            "total_universo": quadro.total_universo,
            "total_analisado": quadro.total_analisado,
            "processamento_integral": quadro.total_analisado == quadro.total_universo,
        },
        "resumo": {
            "total_analisado": quadro.total_analisado,
            "total_excluido": quadro.total_excluido,
            "percentual_excluido": format(quadro.percentual_excluido, "f"),
            "total_aprovado": quadro.total_aprovado,
            "percentual_aprovado": format(quadro.percentual_aprovado, "f"),
            "reconciliado": quadro.reconciliado,
        },
        "familias": [
            {
                "codigo": familia.codigo,
                "nome": familia.nome,
                "ordem": familia.ordem,
                "entrada": familia.entrada,
                "exclusoes": familia.exclusoes,
                "percentual_total_inicial": format(
                    familia.percentual_total_inicial, "f"
                ),
                "percentual_saldo_recebido": format(
                    familia.percentual_saldo_recebido, "f"
                ),
                "saldo": familia.saldo,
                "filtros": [
                    {
                        "codigo": filtro.codigo,
                        "nome": filtro.nome,
                        "ordem": filtro.ordem,
                        "entrada": filtro.entrada,
                        "avaliacoes": filtro.avaliacoes,
                        "exclusoes": filtro.exclusoes,
                        "percentual_total_inicial": format(
                            filtro.percentual_total_inicial, "f"
                        ),
                        "percentual_saldo_recebido": format(
                            filtro.percentual_saldo_recebido, "f"
                        ),
                        "saldo": filtro.saldo,
                    }
                    for filtro in familia.filtros
                ],
            }
            for familia in quadro.familias
        ],
        "fechamento": {
            "equacao": "total_analisado = total_excluido + total_aprovado",
            "lado_esquerdo": quadro.total_analisado,
            "lado_direito": quadro.total_excluido + quadro.total_aprovado,
            "valido": quadro.reconciliado,
        },
    }
