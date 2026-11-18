"""Monta filtros e referências do Screener sem transportar funções."""

from decimal import Decimal


CHAVES_POR_GRUPO = {
    "estatisticos": frozenset({"soma", "media", "mediana", "desvio_padrao"}),
    "geometricos": frozenset({
        "extensao", "perimetro", "quantidade_regioes", "area_total",
        "centro_gravidade_x", "centro_gravidade_y",
    }),
    "padroes": frozenset({
        "duas_sequenciais", "tres_sequenciais", "mais_de_tres_sequenciais",
        "duas_mesma_coluna", "tres_mesma_coluna",
        "mais_de_tres_mesma_coluna", "duas_mesma_linha",
        "tres_mesma_linha", "mais_de_tres_mesma_linha", "duas_linhas",
        "diagonais",
    }),
}


class ErroDicionarioFiltrosScreener(ValueError):
    """Indica referência ausente, duplicada ou incompatível."""

    codigo = "DICIONARIO_FILTROS_INVALIDO"


def montar_dicionario_filtros(
    *,
    estado_referencias: dict[str, object],
    limite_raridade: Decimal | int | str,
    filtros: list[dict[str, object]] | tuple[dict[str, object], ...],
) -> dict[str, object]:
    """Organiza a consulta histórica no formato aceito pela orquestradora.

    Cada item consultado informa apenas identidade, chave explícita, forma de
    comparação e referência. Nomes e objetos de função são proibidos.
    """

    if estado_referencias.get("atualizado") is not True:
        raise ErroDicionarioFiltrosScreener("As referências não estão atualizadas.")
    quantidade = estado_referencias.get("quantidade_resultados")
    if type(quantidade) is not int or quantidade <= 0:
        raise ErroDicionarioFiltrosScreener("A quantidade de resultados é inválida.")

    grupos: dict[str, dict[str, dict[str, object]]] = {
        nome: {} for nome in CHAVES_POR_GRUPO
    }
    for bruto in filtros:
        if not isinstance(bruto, dict):
            raise ErroDicionarioFiltrosScreener("Cada filtro consultado deve ser um dicionário.")
        if "funcao" in bruto or "funcao_python" in bruto or "funcao_detectora" in bruto:
            raise ErroDicionarioFiltrosScreener("O dicionário não aceita nome ou objeto de função.")
        grupo = bruto.get("grupo")
        chave = bruto.get("chave")
        if grupo not in CHAVES_POR_GRUPO or chave not in CHAVES_POR_GRUPO[grupo]:
            raise ErroDicionarioFiltrosScreener("O filtro não possui grupo e chave reconhecidos.")
        if chave in grupos[grupo]:
            raise ErroDicionarioFiltrosScreener(f"O filtro {chave} está duplicado.")
        grupos[grupo][chave] = {
            campo: bruto[campo]
            for campo in (
                "id_filtro", "id_grupo", "nome_filtro", "tipo_resultado",
                "metodo_comparacao", "referencia",
            )
        }

    return {
        "controle": {
            "atualizado": True,
            "quantidade_resultados": quantidade,
            "limite_raridade": limite_raridade,
        },
        **grupos,
    }
