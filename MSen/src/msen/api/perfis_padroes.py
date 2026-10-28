"""API somente leitura dos perfis históricos dos grupos de padrões."""

from datetime import date
from decimal import Decimal, InvalidOperation
import re
from typing import Callable

import psycopg
from flask import Blueprint, current_app, jsonify, request

from msen.config import ErroConfiguracaoBanco, carregar_configuracao_banco
from msen.database import ErroConexaoBanco, abrir_conexao
from msen.services import (
    ErroRecalculoClassificacao,
    PerfilClassificacaoGrupo,
    calcular_perfil_grupo_sequenciais,
)


perfis_padroes_api = Blueprint("perfis_padroes_api", __name__)
FORMATO_GRUPO = re.compile(r"PG_[0-9]{3,}")
PARAMETROS_PERMITIDOS = frozenset(
    {"limite_raridade", "numero_ap_ate", "data_ate"}
)


class ErroEntradaPerfil(ValueError):
    """Representa um parâmetro inválido sem expor detalhes internos."""

    def __init__(self, codigo: str, mensagem: str) -> None:
        super().__init__(mensagem)
        self.codigo = codigo


def calcular_perfil_no_banco(
    limite: Decimal, numero_ap_ate: int | None, data_ate: date | None
) -> PerfilClassificacaoGrupo:
    """Abre conexão curta e calcula um perfil sem alterar o catálogo global."""

    with abrir_conexao(carregar_configuracao_banco()) as conexao:
        return calcular_perfil_grupo_sequenciais(
            conexao,
            limite_raridade_percentual=limite,
            numero_ap_ate=numero_ap_ate,
            data_ate=data_ate,
            sincronizar_catalogo=False,
        )


def _erro(codigo: str, mensagem: str, status: int):
    return jsonify(erro={"codigo": codigo, "mensagem": mensagem}), status


def _parametros() -> tuple[Decimal, int | None, date | None]:
    """Valida limite e um único corte histórico inclusivo."""

    desconhecidos = set(request.args).difference(PARAMETROS_PERMITIDOS)
    if desconhecidos:
        raise ErroEntradaPerfil(
            "PARAMETRO_DESCONHECIDO", "A consulta contém parâmetro não reconhecido."
        )
    texto_limite = request.args.get("limite_raridade", "10")
    try:
        limite = Decimal(texto_limite)
    except (InvalidOperation, ValueError):
        raise ErroEntradaPerfil(
            "LIMITE_INVALIDO", "O limite de raridade deve ser numérico."
        ) from None
    if not limite.is_finite() or not Decimal(0) <= limite <= Decimal(100):
        raise ErroEntradaPerfil(
            "LIMITE_INVALIDO", "O limite de raridade deve estar entre 0 e 100."
        )

    texto_numero = request.args.get("numero_ap_ate")
    texto_data = request.args.get("data_ate")
    if texto_numero is not None and texto_data is not None:
        raise ErroEntradaPerfil(
            "CORTES_CONFLITANTES", "Informe concurso ou data de corte, não ambos."
        )
    numero_ap_ate = None
    if texto_numero is not None:
        try:
            numero_ap_ate = int(texto_numero)
        except ValueError:
            raise ErroEntradaPerfil(
                "CONCURSO_INVALIDO", "O concurso de corte deve ser inteiro positivo."
            ) from None
        if numero_ap_ate <= 0 or str(numero_ap_ate) != texto_numero:
            raise ErroEntradaPerfil(
                "CONCURSO_INVALIDO", "O concurso de corte deve ser inteiro positivo."
            )
    data_ate = None
    if texto_data is not None:
        try:
            data_ate = date.fromisoformat(texto_data)
        except ValueError:
            raise ErroEntradaPerfil(
                "DATA_INVALIDA", "A data de corte deve seguir AAAA-MM-DD."
            ) from None
    return limite, numero_ap_ate, data_ate


def _decimal(valor: Decimal | None) -> str | None:
    return None if valor is None else format(valor, "f")


def serializar_perfil(perfil: PerfilClassificacaoGrupo) -> dict[str, object]:
    """Converte o perfil imutável no contrato JSON público."""

    sem_correspondencia = next(
        item.quantidade for item in perfil.classes if item.padrao_cod is None
    )
    return {
        "grupo_cod": perfil.grupo_cod,
        "amostra": {
            "total_resultados": perfil.total_resultados,
            "total_classificados": perfil.total_classificados,
            "sem_correspondencia": sem_correspondencia,
            "numero_ap_inicial": perfil.numero_ap_inicial,
            "numero_ap_final": perfil.numero_ap_final,
            "data_inicial": (
                None if perfil.data_inicial is None else perfil.data_inicial.isoformat()
            ),
            "data_final": None if perfil.data_final is None else perfil.data_final.isoformat(),
        },
        "raridade": {
            "limite_percentual": _decimal(perfil.limite_raridade_percentual),
            "operador": perfil.operador_raridade,
            "padroes_indicados": list(perfil.padroes_raros),
            "ativa_no_screener": False,
        },
        "versoes_calculo": list(perfil.versoes_calculo),
        "classes": [
            {
                "padrao_cod": item.padrao_cod,
                "estado": (
                    "SEM_CORRESPONDENCIA"
                    if item.padrao_cod is None
                    else "PADRAO_IDENTIFICADO"
                ),
                "quantidade": item.quantidade,
                "percentual_total": _decimal(item.percentual_total),
                "percentual_classificados": _decimal(item.percentual_classificados),
                "intervalo_medio": _decimal(item.intervalo_medio),
                "desvio_padrao": _decimal(item.desvio_padrao),
                "raro": item.raro,
            }
            for item in perfil.classes
        ],
    }


@perfis_padroes_api.get("/api/grupos-padroes/<grupo_cod>/perfil")
def obter_perfil(grupo_cod: str):
    """Retorna o perfil completo ou limitado por um corte histórico inclusivo."""

    try:
        if FORMATO_GRUPO.fullmatch(grupo_cod) is None:
            raise ErroEntradaPerfil(
                "GRUPO_INVALIDO", "O grupo deve seguir o formato PG_001."
            )
        if grupo_cod != "PG_001":
            return _erro(
                "GRUPO_NAO_IMPLEMENTADO", "O classificador do grupo não está disponível.", 404
            )
        limite, numero_ap_ate, data_ate = _parametros()
        servico: Callable[..., PerfilClassificacaoGrupo] = current_app.config[
            "CALCULAR_PERFIL_PADROES"
        ]
        perfil = servico(limite, numero_ap_ate, data_ate)
    except ErroEntradaPerfil as erro:
        return _erro(erro.codigo, str(erro), 400)
    except ErroRecalculoClassificacao as erro:
        return _erro(erro.codigo, "O perfil histórico ainda não está disponível.", 409)
    except (ErroConfiguracaoBanco, ErroConexaoBanco, psycopg.Error):
        return _erro(
            "BANCO_INDISPONIVEL", "Não foi possível consultar o perfil histórico.", 503
        )
    return jsonify(perfil=serializar_perfil(perfil))
