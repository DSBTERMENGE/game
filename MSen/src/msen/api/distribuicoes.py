"""API somente leitura dos perfis e distribuições históricas."""

from datetime import date
from decimal import Decimal, InvalidOperation
from typing import Callable

import psycopg
from flask import Blueprint, current_app, jsonify, request

from msen.config import ErroConfiguracaoBanco, carregar_configuracao_banco
from msen.database import ErroConexaoBanco, abrir_conexao
from msen.services import (
    ErroPerfilEstatistico,
    PerfilEstatistico,
    calcular_faixa_desvio_padrao,
    calcular_faixa_percentual_media,
    calcular_perfil_estatistico,
    construir_distribuicao_visual,
)


distribuicoes_api = Blueprint("distribuicoes_api", __name__)
PARAMETROS = frozenset(
    {
        "numero_ap_antes_de", "data_antes_de", "classes", "metodo_faixa",
        "margem_inferior", "margem_superior",
    }
)


class ErroDistribuicoes(ValueError):
    """Erro previsível da consulta das distribuições."""

    def __init__(self, codigo: str, mensagem: str) -> None:
        super().__init__(mensagem)
        self.codigo = codigo


def _decimal_texto(valor: Decimal) -> str:
    return format(valor, "f")


def _perfil_json(
    codigo: str,
    perfil: PerfilEstatistico,
    *,
    classes: int,
    metodo_faixa: str,
    margem_inferior: Decimal,
    margem_superior: Decimal,
) -> dict[str, object]:
    visual = construir_distribuicao_visual(perfil, quantidade_classes=classes)
    faixa = (
        calcular_faixa_desvio_padrao(
            perfil,
            multiplicador_inferior=margem_inferior,
            multiplicador_superior=margem_superior,
        )
        if metodo_faixa == "desvio_padrao"
        else calcular_faixa_percentual_media(
            perfil,
            percentual_inferior=margem_inferior,
            percentual_superior=margem_superior,
        )
    )
    return {
        "codigo": codigo,
        "quantidade": perfil.quantidade,
        "media": _decimal_texto(perfil.media),
        "desvio_padrao_populacional": _decimal_texto(
            perfil.desvio_padrao_populacional
        ),
        "minimo": _decimal_texto(perfil.minimo),
        "maximo": _decimal_texto(perfil.maximo),
        "faixa": {
            "metodo": faixa.metodo,
            "margem_inferior": _decimal_texto(faixa.parametro_inferior),
            "margem_superior": _decimal_texto(faixa.parametro_superior),
            "limite_inferior": _decimal_texto(faixa.limite_inferior),
            "limite_superior": _decimal_texto(faixa.limite_superior),
            "ativa_no_screener": False,
        },
        "histograma": [
            {
                "limite_inferior": _decimal_texto(item.limite_inferior),
                "limite_superior": _decimal_texto(item.limite_superior),
                "frequencia": item.frequencia,
                "percentual": _decimal_texto(item.percentual),
            }
            for item in visual.classes
        ],
        "curva_normal_referencia": {
            "disponivel": visual.curva_normal_disponivel,
            "pontos": [
                {"x": _decimal_texto(item.x), "densidade": _decimal_texto(item.densidade)}
                for item in visual.curva_normal
            ],
            "uso": "REFERENCIA_VISUAL",
        },
    }


def calcular_distribuicoes_no_banco(
    numero_ap_antes_de: int | None,
    data_antes_de: date | None,
    classes: int,
    metodo_faixa: str,
    margem_inferior: Decimal,
    margem_superior: Decimal,
) -> dict[str, object]:
    """Lê uma janela consistente e monta os dez perfis sem gravar dados."""

    filtros: list[str] = []
    parametros: list[object] = []
    if numero_ap_antes_de is not None:
        filtros.append("r.numero_ap < %s")
        parametros.append(numero_ap_antes_de)
    if data_antes_de is not None:
        filtros.append("r.data_resultado < %s")
        parametros.append(data_antes_de)
    where = "" if not filtros else " WHERE " + " AND ".join(filtros)
    sql = (
        "SELECT r.numero_ap, r.data_resultado, r.soma_res, "
        "r.media_aritmetica_res, r.mediana_res, r.desvio_padrao_media, "
        "g.id_resultado, g.extensao_aberta, g.perimetro_fechado, "
        "g.quantidade_regioes, g.area_total, g.centro_gravidade_x, "
        "g.centro_gravidade_y FROM resultados r LEFT JOIN "
        "analise_geometrica_resultado g ON g.id_resultado = r.id_resultado"
        f"{where} ORDER BY r.numero_ap"
    )
    with abrir_conexao(carregar_configuracao_banco()) as conexao:
        with conexao.cursor() as cursor:
            cursor.execute(sql, tuple(parametros))
            linhas = tuple(cursor.fetchall())
    if not linhas:
        raise ErroDistribuicoes(
            "JANELA_VAZIA", "A janela histórica não possui resultados."
        )
    if any(linha[6] is None for linha in linhas):
        raise ErroDistribuicoes(
            "GEOMETRIA_INCOMPLETA",
            "Nem todos os resultados da janela possuem análise geométrica.",
        )

    colunas = {
        "EST_SOMA": 2,
        "EST_MEDIA": 3,
        "EST_MEDIANA": 4,
        "EST_DESVIO_PADRAO": 5,
        "GEO_EXTENSAO_ABERTA": 7,
        "GEO_PERIMETRO_FECHADO": 8,
        "GEO_QUANTIDADE_REGIOES": 9,
        "GEO_AREA_TOTAL": 10,
        "GEO_CENTRO_GRAVIDADE_X": 11,
        "GEO_CENTRO_GRAVIDADE_Y": 12,
    }
    perfis = []
    for codigo, indice in colunas.items():
        valores = tuple(linha[indice] for linha in linhas if linha[indice] is not None)
        if not valores:
            perfis.append({
                "codigo": codigo,
                "quantidade": 0,
                "ausentes": len(linhas),
                "perfil": None,
            })
            continue
        serializado = _perfil_json(
            codigo,
            calcular_perfil_estatistico(valores),
            classes=classes,
            metodo_faixa=metodo_faixa,
            margem_inferior=margem_inferior,
            margem_superior=margem_superior,
        )
        serializado["ausentes"] = len(linhas) - len(valores)
        perfis.append(serializado)

    return {
        "janela": {
            "quantidade_resultados": len(linhas),
            "numero_ap_inicial": linhas[0][0],
            "numero_ap_final": linhas[-1][0],
            "data_inicial": linhas[0][1].isoformat(),
            "data_final": linhas[-1][1].isoformat(),
            "numero_ap_antes_de": numero_ap_antes_de,
            "data_antes_de": None if data_antes_de is None else data_antes_de.isoformat(),
            "corte_exclusivo": True,
        },
        "dependencias": {
            "soma_media": "EST_MEDIA = EST_SOMA / 6",
            "usar_como_filtros_independentes": False,
        },
        "parametros": perfis,
        "ativa_no_screener": False,
    }


def _ler_parametros() -> tuple[int | None, date | None, int, str, Decimal, Decimal]:
    desconhecidos = set(request.args).difference(PARAMETROS)
    if desconhecidos:
        raise ErroDistribuicoes(
            "PARAMETRO_DESCONHECIDO", "A consulta contém parâmetro não reconhecido."
        )
    texto_numero = request.args.get("numero_ap_antes_de")
    texto_data = request.args.get("data_antes_de")
    if texto_numero is not None and texto_data is not None:
        raise ErroDistribuicoes(
            "CORTES_CONFLITANTES", "Informe concurso ou data, não ambos."
        )
    numero = None
    if texto_numero is not None:
        try:
            numero = int(texto_numero)
        except ValueError:
            numero = 0
        if numero < 1 or str(numero) != texto_numero:
            raise ErroDistribuicoes(
                "CONCURSO_INVALIDO", "O concurso deve ser inteiro positivo."
            )
    data_corte = None
    if texto_data is not None:
        try:
            data_corte = date.fromisoformat(texto_data)
        except ValueError:
            raise ErroDistribuicoes(
                "DATA_INVALIDA", "A data deve seguir AAAA-MM-DD."
            ) from None
    try:
        classes = int(request.args.get("classes", "10"))
    except ValueError:
        classes = 0
    if not 1 <= classes <= 50 or str(classes) != request.args.get("classes", "10"):
        raise ErroDistribuicoes(
            "CLASSES_INVALIDAS", "A quantidade de classes deve estar entre 1 e 50."
        )
    metodo = request.args.get("metodo_faixa", "desvio_padrao")
    if metodo not in {"desvio_padrao", "percentual_media"}:
        raise ErroDistribuicoes("METODO_INVALIDO", "O método de faixa é inválido.")
    margens = []
    for nome, padrao in (("margem_inferior", "1"), ("margem_superior", "1")):
        try:
            valor = Decimal(request.args.get(nome, padrao))
        except InvalidOperation:
            valor = Decimal(-1)
        if not valor.is_finite() or valor < 0:
            raise ErroDistribuicoes("MARGEM_INVALIDA", "As margens devem ser não negativas.")
        margens.append(valor)
    return numero, data_corte, classes, metodo, margens[0], margens[1]


def _erro(codigo: str, mensagem: str, status: int):
    return jsonify(erro={"codigo": codigo, "mensagem": mensagem}), status


@distribuicoes_api.get("/api/perfis/distribuicoes")
def obter_distribuicoes():
    try:
        parametros = _ler_parametros()
        servico: Callable[..., dict[str, object]] = current_app.config[
            "CALCULAR_DISTRIBUICOES"
        ]
        return jsonify(distribuicoes=servico(*parametros))
    except ErroDistribuicoes as erro:
        status = 409 if erro.codigo == "GEOMETRIA_INCOMPLETA" else 400
        return _erro(erro.codigo, str(erro), status)
    except ErroPerfilEstatistico as erro:
        return _erro(erro.codigo, "Não foi possível calcular o perfil.", 409)
    except (ErroConfiguracaoBanco, ErroConexaoBanco, psycopg.Error):
        return _erro("BANCO_INDISPONIVEL", "Não foi possível consultar as distribuições.", 503)
