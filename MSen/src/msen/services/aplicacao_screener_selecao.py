"""Aplica a orquestradora às dezenas registradas para um concurso-alvo."""

from collections.abc import Callable
from decimal import Decimal

from msen.config import carregar_configuracao_banco
from msen.database import abrir_conexao
from msen.modelos import ResultadoEntrada
from msen.padroes import criar_fotografia_historica_diagonal
from msen.screener.orquestrador import orquestrar_aplicacao_screener

from .dicionario_filtros_screener_selecao import montar_dicionario_filtros
from .inicializacao_screener_selecao import criar_dicionario_combinacoes
from .combinacoes_selecao_dezenas import ErroCombinacoesSelecao
from .referencias_screener_selecao import verificar_referencias_atualizadas
from .solicitacao_screener_selecao import SolicitacaoScreenerSelecao


CHAVES_CRITERIOS = {
    "EST_SOMA": ("estatisticos", "soma"),
    "EST_MEDIA": ("estatisticos", "media"),
    "EST_MEDIANA": ("estatisticos", "mediana"),
    "EST_DESVIO_PADRAO": ("estatisticos", "desvio_padrao"),
    "GEO_EXTENSAO": ("geometricos", "extensao"),
    "GEO_PERIMETRO": ("geometricos", "perimetro"),
    "GEO_REGIOES": ("geometricos", "quantidade_regioes"),
    "GEO_AREA": ("geometricos", "area_total"),
    "GEO_CENTRO_X": ("geometricos", "centro_gravidade_x"),
    "GEO_CENTRO_Y": ("geometricos", "centro_gravidade_y"),
    "PAD_PD_001": ("padroes", "duas_sequenciais"),
    "PAD_PD_002": ("padroes", "tres_sequenciais"),
    "PAD_PD_003": ("padroes", "mais_de_tres_sequenciais"),
    "PAD_PD_004": ("padroes", "duas_mesma_coluna"),
    "PAD_PD_005": ("padroes", "tres_mesma_coluna"),
    "PAD_PD_006": ("padroes", "mais_de_tres_mesma_coluna"),
    "PAD_PD_007": ("padroes", "duas_mesma_linha"),
    "PAD_PD_008": ("padroes", "tres_mesma_linha"),
    "PAD_PD_009": ("padroes", "mais_de_tres_mesma_linha"),
    "PAD_PD_011": ("padroes", "duas_linhas"),
    "PAD_PG_004": ("padroes", "diagonais"),
}

CODIGO_PERFIL_POR_CRITERIO = {
    "EST_SOMA": "EST_SOMA",
    "EST_MEDIA": "EST_MEDIA",
    "EST_MEDIANA": "EST_MEDIANA",
    "EST_DESVIO_PADRAO": "EST_DESVIO_PADRAO",
    "GEO_EXTENSAO": "GEO_EXTENSAO_ABERTA",
    "GEO_PERIMETRO": "GEO_PERIMETRO_FECHADO",
    "GEO_REGIOES": "GEO_QUANTIDADE_REGIOES",
    "GEO_AREA": "GEO_AREA_TOTAL",
    "GEO_CENTRO_X": "GEO_CENTRO_GRAVIDADE_X",
    "GEO_CENTRO_Y": "GEO_CENTRO_GRAVIDADE_Y",
}


def carregar_dezenas_alvo_no_banco(id_alvo: int) -> tuple[int, ...]:
    """Lê somente as dezenas marcadas como retornadas para o alvo."""
    with abrir_conexao(carregar_configuracao_banco()) as conexao:
        with conexao.cursor() as cursor:
            cursor.execute(
                "SELECT dezena FROM avaliacoes_dezenas_pesquisa "
                "WHERE id_alvo_selecao=%s AND retornada ORDER BY posicao_ranking",
                (id_alvo,),
            )
            return tuple(linha[0] for linha in cursor.fetchall())


def _faixas_historicas() -> dict[str, dict[str, Decimal]]:
    """Reutiliza os dez perfis históricos já empregados pelo Screener atual."""
    from msen.api.distribuicoes import calcular_distribuicoes_no_banco

    distribuicoes = calcular_distribuicoes_no_banco(
        None, None, 10, "desvio_padrao", Decimal(1), Decimal(1)
    )
    return {
        item["codigo"]: {
            "limite_inferior": item["faixa"]["limite_inferior"],
            "limite_superior": item["faixa"]["limite_superior"],
        }
        for item in distribuicoes["parametros"]
    }


def carregar_filtros_referencias_no_banco(
    limite_raridade: Decimal,
) -> tuple[dict[str, object], ...]:
    """Consulta metadados e monta as referências sem ler campos de função."""
    from msen.api.resultados import listar_resultados_do_banco

    faixas = _faixas_historicas()
    resultados = listar_resultados_do_banco()
    entradas = tuple(ResultadoEntrada.criar(
        data_resultado=item.resultado.data_resultado,
        numero_ap=item.resultado.numero_ap,
        resultados=item.resultado.resultados,
    ) for item in resultados)
    diagonal = criar_fotografia_historica_diagonal(entradas)

    with abrir_conexao(carregar_configuracao_banco()) as conexao:
        with conexao.cursor() as cursor:
            cursor.execute(
                "SELECT padrao_cod, percentual_ocorrencia FROM padroes_subgrupo "
                "WHERE percentual_ocorrencia < %s AND total_sorteios IS NOT NULL "
                "ORDER BY id_padrao",
                (limite_raridade,),
            )
            percentual_por_codigo = {
                f"PAD_{codigo}": percentual for codigo, percentual in cursor.fetchall()
            }
            cursor.execute(
                "SELECT id_criterio, codigo, nome, id_grupo FROM criterios_validacao "
                "WHERE ativo AND estado='APROVADO' ORDER BY id_criterio"
            )
            criterios = cursor.fetchall()

    filtros = []
    for id_criterio, codigo, nome, id_grupo in criterios:
        destino = CHAVES_CRITERIOS.get(codigo)
        if destino is None:
            continue
        grupo, chave = destino
        if grupo != "padroes":
            referencia = faixas[CODIGO_PERFIL_POR_CRITERIO[codigo]]
            tipo = "NUMERICO"
            metodo = "FAIXA"
        elif codigo == "PAD_PG_004":
            referencia = {item.codigo: item.percentual for item in diagonal.incidencias}
            tipo = "CATEGORICO"
            metodo = "RARIDADE"
        else:
            percentual = percentual_por_codigo.get(codigo)
            if percentual is None:
                continue
            referencia = {True: percentual, False: Decimal(100) - percentual}
            tipo = "BOOLEANO"
            metodo = "RARIDADE"
        filtros.append({
            "grupo": grupo, "chave": chave, "id_filtro": id_criterio,
            "id_grupo": id_grupo, "nome_filtro": nome,
            "tipo_resultado": tipo, "metodo_comparacao": metodo,
            "referencia": referencia,
        })
    return tuple(filtros)


def aplicar_screener_selecao(
    solicitacao: SolicitacaoScreenerSelecao,
    *,
    verificar_referencias: Callable[[], dict[str, object]] = verificar_referencias_atualizadas,
    carregar_dezenas: Callable[[int], tuple[int, ...]] = carregar_dezenas_alvo_no_banco,
    carregar_filtros: Callable[[Decimal], tuple[dict[str, object], ...]] = carregar_filtros_referencias_no_banco,
    orquestrar: Callable[..., dict[str, object]] = orquestrar_aplicacao_screener,
) -> dict[str, object]:
    """Prepara os dois dicionários e entrega-os à orquestradora central."""
    if not isinstance(solicitacao, SolicitacaoScreenerSelecao):
        raise TypeError("A aplicação exige SolicitacaoScreenerSelecao.")
    estado = verificar_referencias()
    dezenas = carregar_dezenas(solicitacao.id_alvo)
    combinacoes = criar_dicionario_combinacoes(dezenas)
    if combinacoes["volume_elevado"]:
        raise ErroCombinacoesSelecao(
            "VOLUME_ELEVADO_SCREENER",
            "O volume bruto ultrapassa o limite seguro de 10.000 combinações.",
        )
    filtros = montar_dicionario_filtros(
        estado_referencias=estado,
        limite_raridade=solicitacao.limite_raridade,
        filtros=carregar_filtros(solicitacao.limite_raridade),
    )
    return orquestrar(
        combinacoes, filtros,
        limite_aprovadas=solicitacao.quantidade_maxima_jogos,
    )
