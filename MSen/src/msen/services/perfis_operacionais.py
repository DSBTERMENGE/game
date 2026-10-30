"""Reconciliação substitutiva dos perfis usados pelo algoritmo de seleção."""

from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal
import hashlib
import json

import psycopg

from msen.database import RepositorioResultados

from .analise_geometrica import recalcular_analises_geometricas
from .classificacao_padroes import recalcular_classificacoes_grupo_sequenciais
from .padroes import recalcular_padroes_iniciais
from .perfil_estatistico import PerfilEstatistico, calcular_perfil_estatistico
from .perfis_geometricos import calcular_perfis_geometricos


@dataclass(frozen=True, slots=True)
class RelatorioPerfisOperacionais:
    quantidade_resultados: int
    assinatura_conjunto_resultados: str
    perfis_estatisticos: int
    perfis_geometricos: int
    padroes_atualizados: int
    classificacoes_sequenciais: int
    calculado_em: datetime


def marcar_perfis_operacionais_desatualizados(conexao: psycopg.Connection) -> None:
    """Persiste o bloqueio antes de iniciar uma atualização potencialmente longa."""

    if not isinstance(conexao, psycopg.Connection):
        raise TypeError("A atualização exige uma conexão Psycopg válida.")
    with conexao.transaction():
        with conexao.cursor() as cursor:
            cursor.execute(
                "UPDATE estado_algoritmo_selecao SET atualizado = FALSE, "
                "motivo = 'NOVOS_RESULTADOS_AGUARDANDO_PERFIS', "
                "cobertura_confirmada_em = NULL, alterado_em = CURRENT_TIMESTAMP "
                "WHERE id_estado = 1"
            )


def _assinatura_resultados(resultados) -> str:
    linhas = []
    for item in resultados:
        resultado = item.resultado
        linhas.append({
            "id": item.id_resultado,
            "numero_ap": resultado.numero_ap,
            "data": resultado.data_resultado.isoformat(),
            "dezenas": resultado.resultados,
            "soma": resultado.soma_res,
            "media": str(resultado.media_aritmetica_res),
            "mediana": str(resultado.mediana_res),
            "desvio": str(resultado.desvio_padrao_media),
            "versao": resultado.versao_calculo,
        })
    serializado = json.dumps(linhas, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(serializado.encode("utf-8")).hexdigest()


def _gravar_perfil(
    cursor,
    *,
    codigo: str,
    categoria: str,
    quantidade_total: int,
    quantidade_com_valor: int,
    perfil: PerfilEstatistico | None,
) -> None:
    cursor.execute(
        "INSERT INTO perfis_operacionais_atuais "
        "(codigo, categoria, quantidade_resultados, quantidade_com_valor, "
        "quantidade_ausente, media, desvio_padrao_populacional, minimo, maximo, "
        "calculado_em) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, "
        "CURRENT_TIMESTAMP) ON CONFLICT (codigo) DO UPDATE SET "
        "categoria = EXCLUDED.categoria, "
        "quantidade_resultados = EXCLUDED.quantidade_resultados, "
        "quantidade_com_valor = EXCLUDED.quantidade_com_valor, "
        "quantidade_ausente = EXCLUDED.quantidade_ausente, media = EXCLUDED.media, "
        "desvio_padrao_populacional = EXCLUDED.desvio_padrao_populacional, "
        "minimo = EXCLUDED.minimo, maximo = EXCLUDED.maximo, "
        "calculado_em = EXCLUDED.calculado_em",
        (
            codigo, categoria, quantidade_total, quantidade_com_valor,
            quantidade_total - quantidade_com_valor,
            None if perfil is None else perfil.media,
            None if perfil is None else perfil.desvio_padrao_populacional,
            None if perfil is None else perfil.minimo,
            None if perfil is None else perfil.maximo,
        ),
    )


def atualizar_perfis_operacionais_atuais(
    conexao: psycopg.Connection,
) -> RelatorioPerfisOperacionais:
    """Substitui todos os perfis atuais usando todos os resultados válidos."""

    if not isinstance(conexao, psycopg.Connection):
        raise TypeError("A atualização exige uma conexão Psycopg válida.")
    with conexao.transaction():
        resultados = RepositorioResultados(conexao).listar(limite=10_000)
        if not resultados:
            raise ValueError("Os perfis operacionais exigem ao menos um resultado.")
        total = len(resultados)
        padroes = recalcular_padroes_iniciais(conexao)
        geometria = recalcular_analises_geometricas(conexao)
        classificacoes = recalcular_classificacoes_grupo_sequenciais(conexao)
        if padroes.resultados_analisados != total or geometria.resultados_analisados != total:
            raise RuntimeError("O recálculo não analisou todos os resultados atuais.")
        if any(item.total_sorteios != total for item in padroes.padroes):
            raise RuntimeError("Há padrão calculado com denominador desatualizado.")

        series = {
            "EST_SOMA": (item.resultado.soma_res for item in resultados),
            "EST_MEDIA": (item.resultado.media_aritmetica_res for item in resultados),
            "EST_MEDIANA": (item.resultado.mediana_res for item in resultados),
            "EST_DESVIO_PADRAO": (
                item.resultado.desvio_padrao_media for item in resultados
            ),
        }
        perfis_estatisticos = {
            codigo: calcular_perfil_estatistico(valores)
            for codigo, valores in series.items()
        }
        perfis_geometricos = calcular_perfis_geometricos(geometria.analises)
        assinatura = _assinatura_resultados(resultados)
        momento = datetime.now(timezone.utc)

        with conexao.cursor() as cursor:
            for codigo, perfil in perfis_estatisticos.items():
                _gravar_perfil(
                    cursor, codigo=codigo, categoria="ESTATISTICA",
                    quantidade_total=total, quantidade_com_valor=total, perfil=perfil,
                )
            codigos_geometricos = {
                "GEO_EXTENSAO_ABERTA": "GEO_EXTENSAO",
                "GEO_PERIMETRO_FECHADO": "GEO_PERIMETRO",
                "GEO_QUANTIDADE_REGIOES": "GEO_REGIOES",
                "GEO_AREA_TOTAL": "GEO_AREA",
                "GEO_CENTRO_GRAVIDADE_X": "GEO_CENTRO_X",
                "GEO_CENTRO_GRAVIDADE_Y": "GEO_CENTRO_Y",
            }
            for item in perfis_geometricos.parametros:
                _gravar_perfil(
                    cursor, codigo=codigos_geometricos[item.codigo],
                    categoria="GEOMETRIA", quantidade_total=total,
                    quantidade_com_valor=item.quantidade_com_valor, perfil=item.perfil,
                )
            cursor.execute(
                "DELETE FROM perfis_operacionais_atuais WHERE NOT (codigo = ANY(%s))",
                (list((*perfis_estatisticos.keys(), *codigos_geometricos.values())),),
            )
            cursor.execute(
                "UPDATE estado_algoritmo_selecao SET atualizado = FALSE, "
                "motivo = 'HOMOLOGACAO_OU_COBERTURA_PENDENTE', "
                "assinatura_conjunto_resultados = %s, quantidade_resultados = %s, "
                "perfis_atualizados_em = %s, alterado_em = %s WHERE id_estado = 1",
                (assinatura, total, momento, momento),
            )

    return RelatorioPerfisOperacionais(
        total, assinatura, len(perfis_estatisticos),
        len(perfis_geometricos.parametros), len(padroes.padroes),
        classificacoes.resultados_analisados, momento,
    )
