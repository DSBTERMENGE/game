"""Orquestra o ensaio protegido do novo screener sem persistir dados."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from pathlib import Path
from time import perf_counter

from msen.screener import (
    FaixaEstatistica,
    FaixaGeometrica,
    FrequenciaPadraoFotografada,
    criar_adaptadores_ativos,
    criar_familia_estatistica,
    criar_familia_detectores_raros,
    criar_familia_geometrica,
    criar_fotografia_configuracao,
    criar_grupo_padroes_fotografado,
    criar_quadro_consolidado,
    envelopar_fotografia,
    executar_funil,
    executar_funil_extensivel,
    gerar_amostra,
    serializar_quadro_consolidado,
)
from msen.screener.configuracao import (
    carregar_configuracao_screener,
    validar_limite_raridade,
)
from msen.padroes import criar_registro_detectores_aprovados
from msen.services.selecao_padroes import SelecaoPadroesRaros

from .distribuicoes import calcular_distribuicoes_no_banco
from .perfis_padroes import (
    calcular_perfil_no_banco,
    selecionar_padroes_raros_no_banco,
)


class ErroEnsaioExtensivel(RuntimeError):
    """Indica ausência ou inconsistência de uma entrada necessária ao ensaio."""

    def __init__(self, codigo: str, mensagem: str) -> None:
        super().__init__(mensagem)
        self.codigo = codigo


def _perfil_por_codigo(distribuicoes: dict[str, object], codigo: str) -> dict[str, object]:
    item = next(
        (valor for valor in distribuicoes["parametros"] if valor["codigo"] == codigo),
        None,
    )
    if item is None or item.get("perfil") is None and item.get("media") is None:
        raise ErroEnsaioExtensivel(
            "PERFIL_AUSENTE", f"O perfil {codigo} não está disponível."
        )
    return item


def _faixa(distribuicoes: dict[str, object], codigo: str) -> tuple[Decimal, Decimal]:
    item = _perfil_por_codigo(distribuicoes, codigo)
    faixa = item["faixa"]
    return Decimal(faixa["limite_inferior"]), Decimal(faixa["limite_superior"])


def _grupos_raros_fotografados(perfil, selecao: SelecaoPadroesRaros):
    """Organiza a seleção SQL nos três grupos conceituais fotografados."""

    if (
        perfil.total_resultados <= 0
        or perfil.numero_ap_inicial is None
        or perfil.numero_ap_final is None
        or perfil.data_inicial is None
        or perfil.data_final is None
    ):
        raise ErroEnsaioExtensivel(
            "PERFIL_PADROES_VAZIO", "O perfil histórico de padrões está vazio."
        )
    if not selecao.padroes:
        return ()
    por_grupo: dict[str, list] = {}
    for padrao in selecao.padroes:
        if padrao.grupo_cod not in {"PG_001", "PG_002", "PG_003"}:
            raise ErroEnsaioExtensivel(
                "GRUPO_PADRAO_INVALIDO", "Um padrão raro pertence a grupo não suportado."
            )
        por_grupo.setdefault(padrao.grupo_cod, []).append(padrao)
    grupos = []
    for grupo_cod, padroes in sorted(por_grupo.items()):
        grupos.append(criar_grupo_padroes_fotografado(
            grupo_cod=grupo_cod,
            limite_raridade=selecao.limite_percentual,
            operador=selecao.operador,
            numero_ap_inicial=perfil.numero_ap_inicial,
            numero_ap_final=perfil.numero_ap_final,
            data_inicial=perfil.data_inicial,
            data_final=perfil.data_final,
            denominador=selecao.total_sorteios,
            frequencias=tuple(
                FrequenciaPadraoFotografada(
                    item.padrao_cod, item.num_oco, item.percentual_ocorrencia
                )
                for item in padroes
            ),
        ))
    return tuple(grupos)


def _detalhar_padroes(
    *, padroes, grupos_fotografados, familia_serializada, limite, operador
) -> dict[str, object]:
    """Monta e reconcilia o relatório por padrão e grupo sem reexecutar filtros."""

    filtros = {item["codigo"].removeprefix("PAD_"): item for item in familia_serializada["filtros"]}
    saldo_grupo = familia_serializada["entrada"]
    grupos = []
    for grupo_cod in sorted({item.grupo_cod for item in padroes}):
        itens = tuple(item for item in padroes if item.grupo_cod == grupo_cod)
        if not itens:
            raise ErroEnsaioExtensivel(
                "GRUPO_SEM_PADROES", f"O grupo {grupo_cod} não possui padrões aprovados."
            )
        entrada_grupo = saldo_grupo
        linhas = []
        for item in itens:
            filtro = filtros.get(item.padrao_cod)
            if filtro is None:
                raise ErroEnsaioExtensivel(
                    "PADRAO_SELECIONADO_NAO_APLICADO",
                    "Um padrão retornado pela consulta não foi aplicado no funil.",
                )
            if filtro["entrada"] != saldo_grupo:
                raise ErroEnsaioExtensivel(
                    "ENTRADA_PADRAO_DIVERGENTE", "A entrada do padrão não reconcilia."
                )
            saldo_grupo = filtro["saldo"]
            linhas.append({
                "padrao_cod": item.padrao_cod,
                "padrao_nome": item.padrao_nome,
                "num_ocorrencias": item.num_oco,
                "total_sorteios": item.total_sorteios,
                "percentual_ocorrencia": format(item.percentual_ocorrencia, "f"),
                "limite_percentual": format(limite, "f"),
                "operador": operador,
                "estado": "APLICADO_RARO",
                "avaliacoes": filtro["avaliacoes"],
                "correspondencias": filtro["exclusoes"],
                "exclusoes": filtro["exclusoes"],
                "saldo": filtro["saldo"],
            })
        exclusoes = entrada_grupo - saldo_grupo
        grupos.append({
            "grupo_cod": grupo_cod,
            "grupo_nome": itens[0].grupo_nome,
            "entrada": entrada_grupo,
            "exclusoes": exclusoes,
            "saldo": saldo_grupo,
            "reconciliado": entrada_grupo == exclusoes + saldo_grupo,
            "padroes": linhas,
        })
    total_exclusoes = sum(item["exclusoes"] for item in grupos)
    valido = (
        all(item["reconciliado"] for item in grupos)
        and total_exclusoes == familia_serializada["exclusoes"]
        and saldo_grupo == familia_serializada["saldo"]
    )
    if not valido:
        raise ErroEnsaioExtensivel(
            "DETALHAMENTO_DIVERGENTE", "O detalhamento dos padrões não reconcilia."
        )
    return {
        "limite_percentual": format(limite, "f"),
        "operador": operador,
        "grupos": grupos,
        "fechamento": {
            "entrada": familia_serializada["entrada"],
            "exclusoes": total_exclusoes,
            "saldo": saldo_grupo,
            "valido": valido,
        },
    }


def gerar_quadro_screener_extensivel(
    limite_raridade: Decimal | int | str | None = None,
) -> dict[str, object]:
    """Executa exatamente 5.000 combinações e compara com o funil anterior."""

    raiz = Path(__file__).resolve().parents[3]
    configuracao = carregar_configuracao_screener(
        raiz / "config" / "screener.toml", raiz / "config" / "screener.local.toml"
    )
    limite_efetivo = (
        configuracao.limite_raridade_percentual
        if limite_raridade is None
        else validar_limite_raridade(limite_raridade)
    )
    if (
        configuracao.modo != "amostra"
        or configuracao.limite_combinacoes != 5_000
        or configuracao.confirmacao_processamento_integral
    ):
        raise ErroEnsaioExtensivel(
            "PROTECAO_INTEGRAL_INVALIDA",
            "O novo screener exige amostra de 5.000 e processamento integral bloqueado.",
        )

    distribuicoes = calcular_distribuicoes_no_banco(
        None, None, 10, "desvio_padrao", Decimal(1), Decimal(1)
    )
    perfil_padroes = calcular_perfil_no_banco(
        limite_efetivo, None, None
    )
    selecao_padroes = selecionar_padroes_raros_no_banco(
        limite_efetivo,
        perfil_padroes.total_resultados,
    )
    grupos_padroes = _grupos_raros_fotografados(perfil_padroes, selecao_padroes)

    soma = _faixa(distribuicoes, "EST_SOMA")
    mediana = _faixa(distribuicoes, "EST_MEDIANA")
    desvio = _faixa(distribuicoes, "EST_DESVIO_PADRAO")
    familia_estatistica = criar_familia_estatistica(
        faixa_soma=FaixaEstatistica.criar(*soma),
        faixa_mediana=FaixaEstatistica.criar(*mediana),
        faixa_desvio_padrao=FaixaEstatistica.criar(*desvio),
    )
    codigos_geo = {
        "faixa_extensao": "GEO_EXTENSAO_ABERTA",
        "faixa_perimetro": "GEO_PERIMETRO_FECHADO",
        "faixa_area": "GEO_AREA_TOTAL",
        "faixa_quantidade_regioes": "GEO_QUANTIDADE_REGIOES",
        "faixa_centro_x": "GEO_CENTRO_GRAVIDADE_X",
        "faixa_centro_y": "GEO_CENTRO_GRAVIDADE_Y",
    }
    faixas_geo = {
        nome: FaixaGeometrica.criar(*_faixa(distribuicoes, codigo))
        for nome, codigo in codigos_geo.items()
    }
    familia_geometrica = criar_familia_geometrica(
        **faixas_geo, politica_centro_ausente="excluir"
    )
    familia_padroes = criar_familia_detectores_raros(
        grupos_fotografados=grupos_padroes,
        registro=criar_registro_detectores_aprovados(),
    )
    familias = (familia_estatistica, familia_geometrica, familia_padroes)

    parametros = {
        "EST_SOMA_MEDIA": {"limite_inferior_soma": soma[0], "limite_superior_soma": soma[1]},
        "EST_MEDIANA": {"limite_inferior": mediana[0], "limite_superior": mediana[1]},
        "EST_DESVIO_PADRAO": {"limite_inferior": desvio[0], "limite_superior": desvio[1]},
        **{
            filtro.codigo: {
                "limite_inferior": faixa.limite_inferior,
                "limite_superior": faixa.limite_superior,
                **({"politica_centro_ausente": "excluir"} if filtro.codigo == "GEO_CENTRO_GRAVIDADE" else {}),
            }
            for filtro, faixa in zip(
                familia_geometrica.filtros,
                (
                    faixas_geo["faixa_extensao"], faixas_geo["faixa_perimetro"],
                    faixas_geo["faixa_area"], faixas_geo["faixa_quantidade_regioes"],
                    faixas_geo["faixa_centro_x"],
                ),
            )
        },
        **{
            f"PAD_{codigo}": {
                "grupo_cod": grupo.grupo_cod,
                "limite_raridade": grupo.limite_raridade,
                "operador": grupo.operador,
                "padrao_cod": codigo,
            }
            for grupo in grupos_padroes
            for codigo in grupo.padroes_excludentes
        },
    }
    parametros["GEO_CENTRO_GRAVIDADE"].update({
        "limite_inferior_y": faixas_geo["faixa_centro_y"].limite_inferior,
        "limite_superior_y": faixas_geo["faixa_centro_y"].limite_superior,
    })
    fotografia = criar_fotografia_configuracao(
        familias=familias,
        parametros_filtros=parametros,
        grupos_padroes=grupos_padroes,
        versoes_calculo={
            "estatistica": 1,
            "geometria": 1,
            **{
                grupo.grupo_cod: max(perfil_padroes.versoes_calculo, default=1)
                for grupo in grupos_padroes
            },
        },
        modo="amostra",
        semente=configuracao.semente,
        limite_combinacoes=configuracao.limite_combinacoes,
        data_fotografia=date.today(),
    )
    envelope = envelopar_fotografia(fotografia)
    amostra = gerar_amostra(configuracao)

    inicio = perf_counter()
    relatorio_novo = executar_funil_extensivel(amostra, familias)
    duracao = perf_counter() - inicio
    quadro = criar_quadro_consolidado(relatorio_novo, tipo_escopo="amostra")
    dados = serializar_quadro_consolidado(quadro)
    familia_padroes_serializada = next(
        item for item in dados["familias"] if item["codigo"] == "PADROES"
    )
    dados["detalhes_padroes"] = _detalhar_padroes(
        padroes=selecao_padroes.padroes,
        grupos_fotografados=grupos_padroes,
        familia_serializada=familia_padroes_serializada,
        limite=limite_efetivo,
        operador="<",
    )
    dados["configuracao_raridade"] = {
        "limite_percentual": format(limite_efetivo, "f"),
        "operador": "<",
        "padroes_selecionados": [
            item.padrao_cod for item in selecao_padroes.padroes
        ],
    }

    relatorio_anterior = executar_funil(
        amostra, criar_adaptadores_ativos(configuracao)
    )
    dados.update({
        "duracao_segundos": duracao,
        "fotografia": {
            "checksum_sha256": envelope.checksum_sha256,
            "conteudo_json": envelope.conteudo_json,
        },
        "comparacao": {
            "mesma_amostra": True,
            "semente": configuracao.semente,
            "anterior": {
                "total_aprovado": relatorio_anterior.total_aprovado,
                "total_excluido": relatorio_anterior.total_recebido - relatorio_anterior.total_aprovado,
            },
            "novo": {
                "total_aprovado": relatorio_novo.total_aprovado,
                "total_excluido": relatorio_novo.total_excluido,
            },
            "diferenca_aprovadas": relatorio_novo.total_aprovado - relatorio_anterior.total_aprovado,
            "motivos_divergencia": [
                "ordem nova: estatística, geometria e grupos de padrões",
                "faixas novas: média histórica ± 1 desvio-padrão para todas as medidas",
                "geometria nova: cinco filtros, contra apenas extensão no funil anterior",
                "padrões novos: detectores selecionados de PG_001, PG_002 e PG_003 "
                "com incidência histórica "
                f"< {format(limite_efetivo, 'f')}%",
            ],
        },
        "protecao": {
            "limite_combinacoes": 5_000,
            "processamento_integral_bloqueado": True,
            "confirmacao_processamento_integral": False,
        },
        "aviso": "Ensaio experimental de 5.000; processamento integral bloqueado.",
    })
    return dados
