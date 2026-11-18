"""Contrato dos dois dicionários entregues ao orquestrador do Screener."""

from collections.abc import Iterable
from decimal import Decimal, InvalidOperation


GRUPOS_FILTROS = ("estatisticos", "geometricos", "padroes")
TIPOS_RESULTADO = frozenset({"BOOLEANO", "NUMERICO", "CATEGORICO"})
METODOS_COMPARACAO = frozenset({"FAIXA", "RARIDADE"})


class ErroPacoteScreener(ValueError):
    """Indica que o pacote não atende ao contrato do orquestrador."""


def _validar_combinacao(combinacao) -> tuple[int, ...]:
    if not isinstance(combinacao, (tuple, list)):
        raise ErroPacoteScreener("Cada combinação deve ser uma lista ou tupla.")
    if len(combinacao) != 6:
        raise ErroPacoteScreener("Cada combinação deve possuir seis dezenas.")
    if any(type(dezena) is not int or not 1 <= dezena <= 60 for dezena in combinacao):
        raise ErroPacoteScreener("As dezenas devem ser inteiros entre 1 e 60.")
    if len(set(combinacao)) != 6:
        raise ErroPacoteScreener("Uma combinação não pode repetir dezenas.")
    return tuple(sorted(combinacao))


def _validar_filtro(filtro: dict) -> dict:
    if not isinstance(filtro, dict):
        raise ErroPacoteScreener("Cada filtro deve ser um dicionário.")
    obrigatorios = {
        "id_filtro", "id_grupo", "nome_filtro", "tipo_resultado",
        "metodo_comparacao", "referencia",
    }
    if not obrigatorios.issubset(filtro):
        raise ErroPacoteScreener("Um filtro não possui todos os campos obrigatórios.")
    if type(filtro["id_filtro"]) is not int or filtro["id_filtro"] <= 0:
        raise ErroPacoteScreener("id_filtro deve ser inteiro positivo.")
    if filtro["id_grupo"] is not None and (
        type(filtro["id_grupo"]) is not int or filtro["id_grupo"] <= 0
    ):
        raise ErroPacoteScreener("id_grupo deve ser inteiro positivo ou nulo.")
    if not isinstance(filtro["nome_filtro"], str) or not filtro["nome_filtro"].strip():
        raise ErroPacoteScreener("nome_filtro deve ser preenchido.")
    if filtro["tipo_resultado"] not in TIPOS_RESULTADO:
        raise ErroPacoteScreener("tipo_resultado não é reconhecido.")
    if filtro["metodo_comparacao"] not in METODOS_COMPARACAO:
        raise ErroPacoteScreener("metodo_comparacao não é reconhecido.")
    return {**filtro, "nome_filtro": filtro["nome_filtro"].strip()}


def _validar_limite(valor) -> Decimal:
    try:
        limite = Decimal(str(valor))
    except (InvalidOperation, ValueError):
        raise ErroPacoteScreener("O limite de raridade é inválido.") from None
    if not limite.is_finite() or not Decimal(0) <= limite <= Decimal(100):
        raise ErroPacoteScreener("O limite de raridade deve ficar entre 0 e 100.")
    return limite


def _validar_itens(itens: Iterable) -> Iterable[tuple[int, ...]]:
    for item in itens:
        yield _validar_combinacao(item)


def validar_entradas_screener(
    combinacoes: dict, filtros: dict
) -> tuple[dict, dict]:
    """Valida os dicionários de combinações e filtros com suas referências."""

    if not isinstance(combinacoes, dict) or not {"origem", "itens"}.issubset(combinacoes):
        raise ErroPacoteScreener("O dicionário de combinações é inválido.")
    if not isinstance(combinacoes["origem"], str) or not combinacoes["origem"].strip():
        raise ErroPacoteScreener("A origem das combinações deve ser informada.")
    if "quantidade_combinacoes" not in combinacoes:
        raise ErroPacoteScreener("A quantidade de combinações deve ser informada.")
    if (
        type(combinacoes["quantidade_combinacoes"]) is not int
        or combinacoes["quantidade_combinacoes"] <= 0
    ):
        raise ErroPacoteScreener("Informe ao menos uma combinação.")
    if not isinstance(combinacoes["itens"], Iterable):
        raise ErroPacoteScreener("As combinações devem formar um iterável.")

    if not isinstance(filtros, dict) or set(filtros) != {
        "controle", *GRUPOS_FILTROS
    }:
        raise ErroPacoteScreener("Os três grupos de filtros são obrigatórios.")
    controle = filtros["controle"]
    if not isinstance(controle, dict) or set(controle) != {
        "atualizado", "quantidade_resultados", "limite_raridade"
    }:
        raise ErroPacoteScreener("O controle dos filtros é inválido.")
    if controle["atualizado"] is not True:
        raise ErroPacoteScreener("As referências dos filtros não estão atualizadas.")
    if (
        type(controle["quantidade_resultados"]) is not int
        or controle["quantidade_resultados"] <= 0
    ):
        raise ErroPacoteScreener("A referência exige resultados históricos.")
    grupos: dict[str, dict[str, dict]] = {}
    ids: list[int] = []
    for grupo in GRUPOS_FILTROS:
        if not isinstance(filtros[grupo], dict):
            raise ErroPacoteScreener("Cada grupo de filtros deve ser um dicionário.")
        if any(not isinstance(chave, str) or not chave.strip() for chave in filtros[grupo]):
            raise ErroPacoteScreener("Cada filtro deve possuir uma chave textual.")
        grupos[grupo] = {
            chave: _validar_filtro(item) for chave, item in filtros[grupo].items()
        }
        ids.extend(item["id_filtro"] for item in grupos[grupo].values())
    if len(ids) != len(set(ids)):
        raise ErroPacoteScreener("id_filtro não pode aparecer mais de uma vez.")

    combinacoes_normalizadas = {
        **combinacoes,
        "origem": combinacoes["origem"].strip(),
        "itens": _validar_itens(combinacoes["itens"]),
    }
    filtros_normalizados = {
        "controle": {
            **controle,
            "limite_raridade": _validar_limite(controle["limite_raridade"]),
        },
        **grupos,
    }
    return combinacoes_normalizadas, filtros_normalizados
