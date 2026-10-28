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
    classificar_sequenciais_para_funil,
    criar_adaptadores_ativos,
    criar_familia_estatistica,
    criar_familia_geometrica,
    criar_familia_padroes,
    criar_fotografia_configuracao,
    criar_grupo_padroes_fotografado,
    criar_quadro_consolidado,
    envelopar_fotografia,
    executar_funil,
    executar_funil_extensivel,
    gerar_amostra,
    serializar_quadro_consolidado,
)
from msen.screener.configuracao import carregar_configuracao_screener

from .distribuicoes import calcular_distribuicoes_no_banco
from .perfis_padroes import calcular_perfil_no_banco


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


def _grupo_fotografado(perfil):
    if (
        perfil.total_resultados <= 0
        or perfil.numero_ap_inicial is None
        or perfil.numero_ap_final is None
        or perfil.data_inicial is None
        or perfil.data_final is None
    ):
        raise ErroEnsaioExtensivel(
            "PERFIL_PADROES_VAZIO", "O perfil histórico PG_001 está vazio."
        )
    return criar_grupo_padroes_fotografado(
        grupo_cod=perfil.grupo_cod,
        limite_raridade=perfil.limite_raridade_percentual,
        operador=perfil.operador_raridade,
        numero_ap_inicial=perfil.numero_ap_inicial,
        numero_ap_final=perfil.numero_ap_final,
        data_inicial=perfil.data_inicial,
        data_final=perfil.data_final,
        denominador=perfil.total_resultados,
        frequencias=tuple(
            FrequenciaPadraoFotografada(
                item.padrao_cod, item.quantidade, item.percentual_total
            )
            for item in perfil.classes
        ),
    )


def gerar_quadro_screener_extensivel() -> dict[str, object]:
    """Executa exatamente 5.000 combinações e compara com o funil anterior."""

    raiz = Path(__file__).resolve().parents[3]
    configuracao = carregar_configuracao_screener(
        raiz / "config" / "screener.toml", raiz / "config" / "screener.local.toml"
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
    perfil_padroes = calcular_perfil_no_banco(Decimal(10), None, None)
    grupo = _grupo_fotografado(perfil_padroes)

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
    familia_padroes = criar_familia_padroes(
        grupos_fotografados=(grupo,),
        classificadores={"PG_001": classificar_sequenciais_para_funil},
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
        "PAD_PG_001": {
            "limite_raridade": grupo.limite_raridade,
            "operador": grupo.operador,
            "padroes_excludentes": grupo.padroes_excludentes,
        },
    }
    parametros["GEO_CENTRO_GRAVIDADE"].update({
        "limite_inferior_y": faixas_geo["faixa_centro_y"].limite_inferior,
        "limite_superior_y": faixas_geo["faixa_centro_y"].limite_superior,
    })
    fotografia = criar_fotografia_configuracao(
        familias=familias,
        parametros_filtros=parametros,
        grupos_padroes=(grupo,),
        versoes_calculo={
            "estatistica": 1,
            "geometria": 1,
            "PG_001": max(perfil_padroes.versoes_calculo, default=1),
        },
        modo="amostra",
        semente=configuracao.semente,
        limite_combinacoes=configuracao.limite_combinacoes,
    )
    envelope = envelopar_fotografia(fotografia)
    amostra = gerar_amostra(configuracao)

    inicio = perf_counter()
    relatorio_novo = executar_funil_extensivel(amostra, familias)
    duracao = perf_counter() - inicio
    quadro = criar_quadro_consolidado(relatorio_novo, tipo_escopo="amostra")
    dados = serializar_quadro_consolidado(quadro)

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
                "padrões novos: classificação exclusiva do PG_001 com raridade < 10%",
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
