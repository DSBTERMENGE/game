"""Ativa somente regras individuais aprovadas na amostra protegida."""

from __future__ import annotations

from dataclasses import replace

from msen.padroes import (
    detectar_mais_de_tres_dezenas_sequenciais,
    detectar_mais_de_tres_dezenas_na_mesma_coluna,
    detectar_tres_dezenas_sequenciais,
    detectar_tres_dezenas_na_mesma_coluna,
)

from .adaptadores import (
    AdaptadorMedidasEstatisticas,
    AdaptadorMedidasGeometricas,
    AdaptadorPadroesHistoricos,
)
from .configuracao import ConfiguracaoScreener
from .funil import RelatorioFunil, executar_funil
from .gerador import gerar_amostra
from .politicas import EvidenciaHistoricaPadrao, PoliticaPadraoAtiva
from .politicas_estatisticas import (
    PoliticaDesvioPadraoAtiva,
    PoliticaMediaAtiva,
    PoliticaMedianaAtiva,
)
from .politicas_geometricas import PoliticaExtensaoAtiva


DETECTORES_ATIVOS = {
    "PD_002": detectar_tres_dezenas_sequenciais,
    "PD_003": detectar_mais_de_tres_dezenas_sequenciais,
    "PD_005": detectar_tres_dezenas_na_mesma_coluna,
    "PD_006": detectar_mais_de_tres_dezenas_na_mesma_coluna,
}

ORDEM_ATIVA_PADRAO = (
    "PD_003",
    "PD_002",
    "PD_006",
    "PD_005",
    "EST_MEDIA_P01_P99",
    "EST_DESVIO_P01_P99",
    "EST_MEDIANA_P01_P99",
    "GEO_EXTENSAO_P01_P99",
)


def _criar_adaptador(configuracao: ConfiguracaoScreener, codigo: str):
    """Constrói o adaptador de uma regra histórica já autorizada."""

    regra = configuracao.regras.get(codigo)
    if regra is None or regra.modo != "ativo":
        raise ValueError(f"{codigo} não está configurado como regra ativa")
    criterio = replace(
        configuracao.criterios["padroes_historicos"],
        habilitado=True,
        tolerancias={
            "tolerancia_ocorrencia_percentual": regra.tolerancia_percentual
        },
    )
    evidencia = EvidenciaHistoricaPadrao(
        regra.codigo,
        regra.num_ocorrencias,
        regra.total_resultados,
        True,
        regra.reconciliacao,
    )
    return AdaptadorPadroesHistoricos(
        regra.codigo,
        criterio,
        PoliticaPadraoAtiva(DETECTORES_ATIVOS[codigo], evidencia),
    )


def _validar_contabilidade(
    configuracao: ConfiguracaoScreener, relatorio: RelatorioFunil
) -> None:
    """Confere o limite protegido e o fechamento contábil do funil."""

    if relatorio.total_recebido != configuracao.limite_combinacoes:
        raise RuntimeError("as regras ativas não receberam toda a amostra")
    if relatorio.total_recebido != (
        relatorio.total_aprovado + sum(relatorio.exclusoes_por_criterio.values())
    ):
        raise RuntimeError("a contabilidade das regras ativas não fecha")


def executar_pd003_ativo(configuracao: ConfiguracaoScreener) -> RelatorioFunil:
    """Executa PD_003 ativo somente nas 5.000 combinações da amostra validada."""

    if not isinstance(configuracao, ConfiguracaoScreener):
        raise TypeError("configuracao deve ser uma ConfiguracaoScreener validada")
    adaptador = _criar_adaptador(configuracao, "PD_003")
    relatorio = executar_funil(gerar_amostra(configuracao), (adaptador,))
    _validar_contabilidade(configuracao, relatorio)
    return relatorio


def criar_adaptadores_ativos(
    configuracao: ConfiguracaoScreener,
    ordem_filtros: tuple[str, ...] | None = None,
) -> tuple[object, ...]:
    """Constrói os oito adaptadores ativos na ordem solicitada."""

    if not isinstance(configuracao, ConfiguracaoScreener):
        raise TypeError("configuracao deve ser uma ConfiguracaoScreener validada")
    ordem = ("PD_003", "PD_002", "PD_006", "PD_005")
    adaptadores = [
        _criar_adaptador(configuracao, codigo) for codigo in ordem
    ]
    regra_media = configuracao.regras_estatisticas.get("EST_MEDIA_P01_P99")
    if regra_media is None or regra_media.modo != "ativo":
        raise ValueError("EST_MEDIA_P01_P99 não está configurada como regra ativa")
    criterio_media = replace(
        configuracao.criterios["medidas_estatisticas"],
        habilitado=True,
        tolerancias={
            "limite_inferior_media": regra_media.limite_inferior,
            "limite_superior_media": regra_media.limite_superior,
        },
    )
    adaptadores.append(
        AdaptadorMedidasEstatisticas(
            regra_media.codigo, criterio_media, PoliticaMediaAtiva()
        )
    )
    regra_desvio = configuracao.regras_estatisticas.get("EST_DESVIO_P01_P99")
    if regra_desvio is None or regra_desvio.modo != "ativo":
        raise ValueError("EST_DESVIO_P01_P99 não está configurada como regra ativa")
    criterio_desvio = replace(
        configuracao.criterios["medidas_estatisticas"],
        habilitado=True,
        tolerancias={
            "limite_inferior_desvio": regra_desvio.limite_inferior,
            "limite_superior_desvio": regra_desvio.limite_superior,
        },
    )
    adaptadores.append(
        AdaptadorMedidasEstatisticas(
            regra_desvio.codigo, criterio_desvio, PoliticaDesvioPadraoAtiva()
        )
    )
    regra_mediana = configuracao.regras_estatisticas.get("EST_MEDIANA_P01_P99")
    if regra_mediana is None or regra_mediana.modo != "ativo":
        raise ValueError("EST_MEDIANA_P01_P99 não está configurada como regra ativa")
    criterio_mediana = replace(
        configuracao.criterios["medidas_estatisticas"],
        habilitado=True,
        tolerancias={
            "limite_inferior_mediana": regra_mediana.limite_inferior,
            "limite_superior_mediana": regra_mediana.limite_superior,
        },
    )
    adaptadores.append(
        AdaptadorMedidasEstatisticas(
            regra_mediana.codigo, criterio_mediana, PoliticaMedianaAtiva()
        )
    )
    regra_extensao = configuracao.regras_geometricas.get("GEO_EXTENSAO_P01_P99")
    if regra_extensao is None or regra_extensao.modo != "ativo":
        raise ValueError("GEO_EXTENSAO_P01_P99 não está configurada como regra ativa")
    criterio_extensao = replace(
        configuracao.criterios["medidas_geometricas"],
        habilitado=True,
        tolerancias={
            "limite_inferior_extensao": regra_extensao.limite_inferior,
            "limite_superior_extensao": regra_extensao.limite_superior,
        },
    )
    adaptadores.append(
        AdaptadorMedidasGeometricas(
            regra_extensao.codigo, criterio_extensao, PoliticaExtensaoAtiva()
        )
    )
    ordem_solicitada = ORDEM_ATIVA_PADRAO if ordem_filtros is None else ordem_filtros
    if (
        not isinstance(ordem_solicitada, tuple)
        or len(ordem_solicitada) != len(ORDEM_ATIVA_PADRAO)
        or set(ordem_solicitada) != set(ORDEM_ATIVA_PADRAO)
    ):
        raise ValueError("ordem_filtros deve ser uma permutação dos oito filtros ativos")
    por_codigo = {adaptador.codigo: adaptador for adaptador in adaptadores}
    adaptadores = [por_codigo[codigo] for codigo in ordem_solicitada]
    return tuple(adaptadores)


def executar_padroes_ativos(
    configuracao: ConfiguracaoScreener,
    ordem_filtros: tuple[str, ...] | None = None,
) -> RelatorioFunil:
    """Executa os filtros autorizados na ordem indicada, apenas na amostra."""

    adaptadores = criar_adaptadores_ativos(configuracao, ordem_filtros)
    relatorio = executar_funil(gerar_amostra(configuracao), adaptadores)
    _validar_contabilidade(configuracao, relatorio)
    return relatorio
