"""Contrato do disparo do Screener pela página Seleção de dezenas."""

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation


class ErroSolicitacaoScreenerSelecao(ValueError):
    """Indica um dado inválido antes do início do processamento."""

    codigo = "SOLICITACAO_SCREENER_INVALIDA"


@dataclass(frozen=True, slots=True)
class SolicitacaoScreenerSelecao:
    """Dados confirmados pelo usuário para iniciar o Screener.

    Este objeto apenas valida e transporta o comando. Ele não consulta o
    banco, não gera combinações e não executa filtros.
    """

    id_alvo: int
    quantidade_maxima_jogos: int
    valor_unitario_centavos: int
    limite_raridade: Decimal

    @classmethod
    def criar(
        cls,
        *,
        id_alvo: object,
        quantidade_maxima_jogos: object,
        valor_unitario_centavos: object,
        limite_raridade: object,
    ) -> "SolicitacaoScreenerSelecao":
        if type(id_alvo) is not int or id_alvo <= 0:
            raise ErroSolicitacaoScreenerSelecao("id_alvo deve ser inteiro positivo.")
        if (
            type(quantidade_maxima_jogos) is not int
            or not 1 <= quantidade_maxima_jogos <= 50_063_860
        ):
            raise ErroSolicitacaoScreenerSelecao(
                "quantidade_maxima_jogos deve ficar entre 1 e 50.063.860."
            )
        if type(valor_unitario_centavos) is not int or valor_unitario_centavos <= 0:
            raise ErroSolicitacaoScreenerSelecao(
                "valor_unitario_centavos deve ser inteiro positivo."
            )
        try:
            limite = Decimal(str(limite_raridade))
        except (InvalidOperation, ValueError):
            raise ErroSolicitacaoScreenerSelecao(
                "limite_raridade deve ser numérico."
            ) from None
        if not limite.is_finite() or not Decimal("0") <= limite <= Decimal("100"):
            raise ErroSolicitacaoScreenerSelecao(
                "limite_raridade deve ficar entre 0 e 100."
            )
        return cls(
            id_alvo=id_alvo,
            quantidade_maxima_jogos=quantidade_maxima_jogos,
            valor_unitario_centavos=valor_unitario_centavos,
            limite_raridade=limite,
        )
