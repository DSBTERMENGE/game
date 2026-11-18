"""Orquestradora central e explícita dos três membros do Screener."""

from datetime import date
from decimal import Decimal, InvalidOperation

from msen.calculos import (
    calcular_desvio_padrao_media, calcular_media_aritmetica,
    calcular_mediana, calcular_soma,
)
from msen.geometria import calcular_extensao_aberta, calcular_perimetro_fechado
from msen.modelos import ResultadoEntrada
from msen.padroes import (
    calcular_categorias_diagonais, detectar_dezenas_em_duas_linhas,
    detectar_duas_dezenas_na_mesma_coluna,
    detectar_duas_dezenas_na_mesma_linha,
    detectar_duas_dezenas_sequenciais,
    detectar_mais_de_tres_dezenas_na_mesma_coluna,
    detectar_mais_de_tres_dezenas_na_mesma_linha,
    detectar_mais_de_tres_dezenas_sequenciais,
    detectar_tres_dezenas_na_mesma_coluna,
    detectar_tres_dezenas_na_mesma_linha,
    detectar_tres_dezenas_sequenciais,
)
from msen.validacao.criterios import (
    calcular_area_total, calcular_centro_gravidade_x,
    calcular_centro_gravidade_y, calcular_quantidade_regioes,
)

from .pacote import ErroPacoteScreener, validar_entradas_screener


def _decimal(valor, *, campo: str) -> Decimal:
    try:
        convertido = Decimal(str(valor))
    except (InvalidOperation, ValueError):
        raise ErroPacoteScreener(f"{campo} deve ser numérico.") from None
    if not convertido.is_finite():
        raise ErroPacoteScreener(f"{campo} deve ser finito.")
    return convertido


def _comparar_com_referencia(
    *, valor, filtro: dict, limite_raridade: Decimal
) -> tuple[bool, Decimal | None]:
    """Compara o valor calculado usando a referência contida no filtro."""

    referencia = filtro["referencia"]
    metodo = filtro["metodo_comparacao"]
    if metodo == "FAIXA":
        if valor is None:
            return False, None
        if not isinstance(referencia, dict) or not {
            "limite_inferior", "limite_superior"
        }.issubset(referencia):
            raise ErroPacoteScreener(
                f"O filtro {filtro['nome_filtro']} não possui faixa completa."
            )
        calculado = _decimal(valor, campo="valor calculado")
        inferior = _decimal(referencia["limite_inferior"], campo="limite inferior")
        superior = _decimal(referencia["limite_superior"], campo="limite superior")
        if inferior > superior:
            raise ErroPacoteScreener("O limite inferior não pode superar o superior.")
        return inferior <= calculado <= superior, None
    if metodo == "RARIDADE":
        if not isinstance(referencia, dict):
            raise ErroPacoteScreener(
                f"O filtro {filtro['nome_filtro']} não possui tabela de percentuais."
            )
        percentual = _decimal(
            referencia.get(valor, 0), campo="percentual histórico"
        )
        return percentual >= limite_raridade, percentual
    raise ErroPacoteScreener(f"Método de comparação não implementado: {metodo}.")


def _avaliar(*, combinacao, membro, filtro, valor, limite):
    """Retorna os dados da exclusão ou ``None`` quando o filtro aprova."""
    passou, percentual = _comparar_com_referencia(
        valor=valor, filtro=filtro, limite_raridade=limite
    )
    if passou:
        return None
    return {
        "combinacao": combinacao, "membro": membro,
        "id_filtro": filtro["id_filtro"], "nome_filtro": filtro["nome_filtro"],
        "valor": valor, "percentual": percentual,
    }


def _entrada_estatistica(combinacao):
    return ResultadoEntrada.criar(
        data_resultado=date(2000, 1, 1), numero_ap=1, resultados=combinacao
    )


# ORQUESTRADORA CENTRAL DO SCREENER
# Recebe as combinações e os filtros completos, conduz cada combinação pelos
# membros Estatístico, Geométrico e Padrões e conserva somente as aprovadas.
def orquestrar_aplicacao_screener(
    dicionario_combinacoes: dict,
    dicionario_filtros: dict,
    *,
    limite_aprovadas: int | None = None,
) -> dict[str, object]:
    """Aplica o funil completo a uma ou várias combinações.

    Esta é a função orquestradora central. Ela controla o laço exterior das
    combinações e, para cada combinação, executa em ordem os três membros
    internos do Screener: Estatístico, Geométrico e Padrões. A primeira
    reprovação interrompe a combinação; somente quem passa por todos os
    filtros é incluído na relação final de aprovadas.
    """

    if limite_aprovadas is not None and (
        type(limite_aprovadas) is not int or limite_aprovadas <= 0
    ):
        raise ErroPacoteScreener("limite_aprovadas deve ser inteiro positivo.")
    combinacoes, filtros = validar_entradas_screener(
        dicionario_combinacoes, dicionario_filtros
    )
    limite = filtros["controle"]["limite_raridade"]
    aprovadas: list[tuple[int, ...]] = []
    exclusoes: list[dict[str, object]] = []
    total_analisado = 0

    for combinacao in combinacoes["itens"]:
        total_analisado += 1
        estatisticos = filtros["estatisticos"]
        geometricos = filtros["geometricos"]
        padroes = filtros["padroes"]
        exclusao = None

        # MEMBRO 1 — FILTROS ESTATÍSTICOS
        entrada = _entrada_estatistica(combinacao)
        if "soma" in estatisticos:
            exclusao = _avaliar(combinacao=combinacao, membro="ESTATISTICO", filtro=estatisticos["soma"], valor=calcular_soma(entrada), limite=limite)
        if exclusao is None and "media" in estatisticos:
            exclusao = _avaliar(combinacao=combinacao, membro="ESTATISTICO", filtro=estatisticos["media"], valor=calcular_media_aritmetica(entrada), limite=limite)
        if exclusao is None and "mediana" in estatisticos:
            exclusao = _avaliar(combinacao=combinacao, membro="ESTATISTICO", filtro=estatisticos["mediana"], valor=calcular_mediana(entrada), limite=limite)
        if exclusao is None and "desvio_padrao" in estatisticos:
            exclusao = _avaliar(combinacao=combinacao, membro="ESTATISTICO", filtro=estatisticos["desvio_padrao"], valor=calcular_desvio_padrao_media(entrada), limite=limite)
        if exclusao is not None:
            exclusoes.append(exclusao)
            continue

        # MEMBRO 2 — FILTROS GEOMÉTRICOS
        if "extensao" in geometricos:
            exclusao = _avaliar(combinacao=combinacao, membro="GEOMETRICO", filtro=geometricos["extensao"], valor=calcular_extensao_aberta(combinacao), limite=limite)
        if exclusao is None and "perimetro" in geometricos:
            exclusao = _avaliar(combinacao=combinacao, membro="GEOMETRICO", filtro=geometricos["perimetro"], valor=calcular_perimetro_fechado(combinacao), limite=limite)
        if exclusao is None and "quantidade_regioes" in geometricos:
            exclusao = _avaliar(combinacao=combinacao, membro="GEOMETRICO", filtro=geometricos["quantidade_regioes"], valor=calcular_quantidade_regioes(combinacao), limite=limite)
        if exclusao is None and "area_total" in geometricos:
            exclusao = _avaliar(combinacao=combinacao, membro="GEOMETRICO", filtro=geometricos["area_total"], valor=calcular_area_total(combinacao), limite=limite)
        if exclusao is None and "centro_gravidade_x" in geometricos:
            exclusao = _avaliar(combinacao=combinacao, membro="GEOMETRICO", filtro=geometricos["centro_gravidade_x"], valor=calcular_centro_gravidade_x(combinacao), limite=limite)
        if exclusao is None and "centro_gravidade_y" in geometricos:
            exclusao = _avaliar(combinacao=combinacao, membro="GEOMETRICO", filtro=geometricos["centro_gravidade_y"], valor=calcular_centro_gravidade_y(combinacao), limite=limite)
        if exclusao is not None:
            exclusoes.append(exclusao)
            continue

        # MEMBRO 3 — FILTROS DE PADRÕES
        if "duas_sequenciais" in padroes:
            exclusao = _avaliar(combinacao=combinacao, membro="PADRAO", filtro=padroes["duas_sequenciais"], valor=detectar_duas_dezenas_sequenciais(combinacao), limite=limite)
        if exclusao is None and "tres_sequenciais" in padroes:
            exclusao = _avaliar(combinacao=combinacao, membro="PADRAO", filtro=padroes["tres_sequenciais"], valor=detectar_tres_dezenas_sequenciais(combinacao), limite=limite)
        if exclusao is None and "mais_de_tres_sequenciais" in padroes:
            exclusao = _avaliar(combinacao=combinacao, membro="PADRAO", filtro=padroes["mais_de_tres_sequenciais"], valor=detectar_mais_de_tres_dezenas_sequenciais(combinacao), limite=limite)
        if exclusao is None and "duas_mesma_coluna" in padroes:
            exclusao = _avaliar(combinacao=combinacao, membro="PADRAO", filtro=padroes["duas_mesma_coluna"], valor=detectar_duas_dezenas_na_mesma_coluna(combinacao), limite=limite)
        if exclusao is None and "tres_mesma_coluna" in padroes:
            exclusao = _avaliar(combinacao=combinacao, membro="PADRAO", filtro=padroes["tres_mesma_coluna"], valor=detectar_tres_dezenas_na_mesma_coluna(combinacao), limite=limite)
        if exclusao is None and "mais_de_tres_mesma_coluna" in padroes:
            exclusao = _avaliar(combinacao=combinacao, membro="PADRAO", filtro=padroes["mais_de_tres_mesma_coluna"], valor=detectar_mais_de_tres_dezenas_na_mesma_coluna(combinacao), limite=limite)
        if exclusao is None and "duas_mesma_linha" in padroes:
            exclusao = _avaliar(combinacao=combinacao, membro="PADRAO", filtro=padroes["duas_mesma_linha"], valor=detectar_duas_dezenas_na_mesma_linha(combinacao), limite=limite)
        if exclusao is None and "tres_mesma_linha" in padroes:
            exclusao = _avaliar(combinacao=combinacao, membro="PADRAO", filtro=padroes["tres_mesma_linha"], valor=detectar_tres_dezenas_na_mesma_linha(combinacao), limite=limite)
        if exclusao is None and "mais_de_tres_mesma_linha" in padroes:
            exclusao = _avaliar(combinacao=combinacao, membro="PADRAO", filtro=padroes["mais_de_tres_mesma_linha"], valor=detectar_mais_de_tres_dezenas_na_mesma_linha(combinacao), limite=limite)
        if exclusao is None and "duas_linhas" in padroes:
            exclusao = _avaliar(combinacao=combinacao, membro="PADRAO", filtro=padroes["duas_linhas"], valor=detectar_dezenas_em_duas_linhas(combinacao), limite=limite)
        if exclusao is None and "diagonais" in padroes:
            exclusao = _avaliar(combinacao=combinacao, membro="PADRAO", filtro=padroes["diagonais"], valor=calcular_categorias_diagonais(combinacao), limite=limite)
        if exclusao is not None:
            exclusoes.append(exclusao)
            continue

        aprovadas.append(combinacao)
        if limite_aprovadas is not None and len(aprovadas) >= limite_aprovadas:
            break

    esperado = combinacoes["quantidade_combinacoes"]
    interrompido = total_analisado < esperado and (
        limite_aprovadas is not None and len(aprovadas) >= limite_aprovadas
    )
    if total_analisado != esperado and not interrompido:
        raise ErroPacoteScreener(
            "A quantidade declarada de combinações diverge do iterador recebido."
        )
    return {
        "total_recebido": total_analisado,
        "total_aprovado": len(aprovadas),
        "total_excluido": len(exclusoes),
        "total_universo": esperado,
        "interrompido_por_limite": interrompido,
        "combinacoes_aprovadas": tuple(aprovadas),
        "exclusoes": tuple(exclusoes),
    }
