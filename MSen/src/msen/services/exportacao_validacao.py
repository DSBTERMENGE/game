"""Exporta a homologação em formatos reproduzíveis e inertes."""

from __future__ import annotations

import csv
import hashlib
import io
import json
from datetime import datetime, timezone
from typing import Iterable

from msen.config import carregar_configuracao_banco
from msen.database import abrir_conexao


COLUNAS = (
    "concurso", "dezenas", "criterio_codigo", "criterio_nome", "categoria",
    "funcao_python", "tipo_resultado", "precisao_decimal", "grupo_codigo",
    "grupo_nome", "esperado_estado", "esperado_valor", "esperado_subgrupo_codigo",
    "esperado_subgrupo_nome", "calculado_estado", "calculado_valor",
    "calculado_subgrupo_codigo", "calculado_subgrupo_nome", "aprovado", "diferenca",
    "assinatura_funcao", "assinatura_regra", "assinatura_executada",
    "referencia_origem", "referencia_revisor", "referencia_conferida_em", "calculado_em",
)


def _texto(valor) -> str | None:
    if valor is None:
        return None
    if isinstance(valor, datetime):
        return valor.isoformat()
    return str(valor).strip() if isinstance(valor, str) else str(valor)


def _identificador(registros: list[dict[str, object]]) -> str:
    canonico = json.dumps(registros, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonico.encode("utf-8")).hexdigest()


def montar_exportacao(linhas: Iterable[tuple], *, gerado_em: datetime | None = None) -> dict[str, object]:
    registros = []
    for linha in linhas:
        registro = {coluna: _texto(valor) for coluna, valor in zip(COLUNAS, linha, strict=True)}
        registro["dezenas"] = [int(numero) for numero in str(registro["dezenas"]).split(",")]
        registro["precisao_decimal"] = None if registro["precisao_decimal"] is None else int(registro["precisao_decimal"])
        registros.append(registro)
    identificador = _identificador(registros)
    momento = gerado_em or datetime.now(timezone.utc)
    return {
        "formato": "msen-validacao-auditoria",
        "versao_esquema": 1,
        "gerado_em": momento.isoformat(),
        "conjunto_referencias": {"algoritmo": "sha256", "identificador": identificador, "quantidade": len(registros)},
        "registros": registros,
    }


def validar_exportacao(dados: dict[str, object]) -> bool:
    if dados.get("formato") != "msen-validacao-auditoria" or dados.get("versao_esquema") != 1:
        return False
    registros = dados.get("registros")
    conjunto = dados.get("conjunto_referencias")
    return (
        isinstance(registros, list) and isinstance(conjunto, dict)
        and conjunto.get("quantidade") == len(registros)
        and conjunto.get("identificador") == _identificador(registros)
    )


def serializar_json(dados: dict[str, object]) -> str:
    return json.dumps(dados, ensure_ascii=False, sort_keys=True, indent=2) + "\n"


def _celula_csv(valor: object) -> str:
    if isinstance(valor, list):
        texto = " ".join(f"{int(numero):02d}" for numero in valor)
    elif valor is None:
        texto = ""
    else:
        texto = str(valor)
    if texto.startswith(("\t", "\r")) or texto.lstrip(" ").startswith(("=", "+", "-", "@")):
        return "'" + texto
    return texto


def serializar_csv(dados: dict[str, object]) -> str:
    saida = io.StringIO(newline="")
    campos = ("conjunto_referencias",) + COLUNAS
    escritor = csv.DictWriter(saida, fieldnames=campos, extrasaction="ignore", lineterminator="\r\n")
    escritor.writeheader()
    identificador = dados["conjunto_referencias"]["identificador"]
    for registro in dados["registros"]:
        linha = {campo: _celula_csv(registro.get(campo)) for campo in COLUNAS}
        linha["conjunto_referencias"] = identificador
        escritor.writerow(linha)
    return "\ufeff" + saida.getvalue()


def exportar_validacao_no_banco() -> dict[str, object]:
    configuracao = carregar_configuracao_banco()
    with abrir_conexao(configuracao) as conexao, conexao.cursor() as cursor:
        cursor.execute(
            "SELECT r.numero_ap, concat_ws(',', r.res_01, r.res_02, r.res_03, r.res_04, r.res_05, r.res_06), "
            "c.codigo, c.nome, c.categoria, c.funcao_python, c.tipo_resultado, c.precisao_decimal, "
            "g.grupo_cod, g.grupo_nome, coalesce(a.estado_valor_esperado, a.estado_padrao_esperado), "
            "a.valor_esperado::text, pe.padrao_cod, pe.padrao_nome, "
            "coalesce(a.estado_valor_calculado, a.estado_padrao_calculado), a.valor_calculado::text, "
            "pc.padrao_cod, pc.padrao_nome, a.aprovado, a.diferenca::text, c.assinatura_funcao, "
            "c.assinatura_regra, a.assinatura_executada, a.referencia_origem, a.referencia_revisor, "
            "a.referencia_conferida_em, a.calculado_em FROM avaliacoes_validacao a "
            "JOIN amostras_validacao am USING (id_resultado) JOIN resultados r USING (id_resultado) "
            "JOIN criterios_validacao c USING (id_criterio) LEFT JOIN padroes_grupo g ON g.id_grupo = a.id_grupo "
            "LEFT JOIN padroes_subgrupo pe ON pe.id_grupo = a.id_grupo AND pe.id_padrao = a.id_padrao_esperado "
            "LEFT JOIN padroes_subgrupo pc ON pc.id_grupo = a.id_grupo AND pc.id_padrao = a.id_padrao_calculado "
            "WHERE am.ativo AND c.ativo ORDER BY am.ordem, c.categoria, c.codigo"
        )
        return montar_exportacao(cursor.fetchall())
