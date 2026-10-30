"""Consulta paginada da página de Validação e auditoria."""

from flask import Blueprint, Response, current_app, jsonify, request

from msen.services.exportacao_validacao import serializar_csv, serializar_json

from msen.config import carregar_configuracao_banco
from msen.database import abrir_conexao


validacao_api = Blueprint("validacao_api", __name__)
CATEGORIAS = frozenset({"ESTATISTICA", "GEOMETRIA", "PADRAO"})
SITUACOES = frozenset({"S", "N", "PENDENTE"})


class ErroConsultaValidacao(ValueError):
    def __init__(self, codigo: str, mensagem: str) -> None:
        super().__init__(mensagem)
        self.codigo = codigo


def _inteiro(nome: str, texto: str | None, padrao: int, minimo: int, maximo: int) -> int:
    if texto is None:
        return padrao
    try:
        valor = int(texto)
    except ValueError as erro:
        raise ErroConsultaValidacao("PARAMETRO_INVALIDO", f"{nome} deve ser inteiro.") from erro
    if not minimo <= valor <= maximo:
        raise ErroConsultaValidacao(
            "PARAMETRO_INVALIDO", f"{nome} deve estar entre {minimo} e {maximo}."
        )
    return valor


def _texto_opcional(nome: str, valor: str | None, limite: int = 80) -> str | None:
    if valor is None or not valor.strip():
        return None
    resultado = valor.strip()
    if len(resultado) > limite:
        raise ErroConsultaValidacao("PARAMETRO_INVALIDO", f"{nome} é muito longo.")
    return resultado


def consultar_validacao_no_banco(filtros: dict[str, object]) -> dict[str, object]:
    configuracao = carregar_configuracao_banco()
    with abrir_conexao(configuracao) as conexao:
        return consultar_validacao(conexao, filtros)


def _hipotese_diagnostica(
    *, assinatura_atual: str, assinatura_executada: str | None,
    estado_esperado: str | None, estado_calculado: str | None,
    valor_esperado: str | None, valor_calculado: str | None,
    subgrupo_esperado: str | None, subgrupo_calculado: str | None,
) -> str:
    if assinatura_executada != assinatura_atual:
        return "A implementação executada não corresponde à assinatura atual; recalcule antes de analisar a fórmula."
    if estado_esperado != estado_calculado:
        return "A função discordou sobre a existência do valor ou do padrão; revise o caso-limite e a regra de ausência."
    if subgrupo_esperado != subgrupo_calculado:
        return "O detector retornou subgrupo diferente do esperado; revise exclusividade, maior bloco e vínculo com o grupo."
    if valor_esperado != valor_calculado:
        return "O valor numérico divergiu; revise fórmula, ordenação das dezenas, precisão e arredondamento contratado."
    return "A divergência exige inspeção da assinatura, dos estados persistidos e da regra do critério."


def consultar_relatorio_no_banco() -> dict[str, object]:
    configuracao = carregar_configuracao_banco()
    with abrir_conexao(configuracao) as conexao:
        return consultar_relatorio(conexao)


def consultar_relatorio(conexao) -> dict[str, object]:
    with conexao.cursor() as cursor:
        cursor.execute(
            "SELECT c.codigo, c.nome, c.categoria, c.estado, count(*), "
            "count(*) FILTER (WHERE a.executado), "
            "count(*) FILTER (WHERE a.aprovado = 'S'), "
            "count(*) FILTER (WHERE a.aprovado = 'N'), "
            "count(*) FILTER (WHERE NOT a.referencia_conferida OR NOT a.executado), "
            "count(*) FILTER (WHERE a.executado AND "
            "a.assinatura_executada <> c.assinatura_funcao), "
            "count(*) FILTER (WHERE NOT a.referencia_conferida) "
            "FROM criterios_validacao c JOIN avaliacoes_validacao a USING (id_criterio) "
            "JOIN amostras_validacao am USING (id_resultado) "
            "WHERE c.ativo AND am.ativo GROUP BY c.id_criterio ORDER BY c.categoria, c.codigo"
        )
        linhas_resumo = cursor.fetchall()
        cursor.execute(
            "SELECT c.codigo, c.nome, c.categoria, c.assinatura_funcao, "
            "a.assinatura_executada, r.numero_ap, r.res_01, r.res_02, r.res_03, "
            "r.res_04, r.res_05, r.res_06, g.grupo_cod, g.grupo_nome, "
            "a.estado_valor_esperado, a.valor_esperado::text, "
            "a.estado_valor_calculado, a.valor_calculado::text, "
            "a.estado_padrao_esperado, pe.padrao_cod, pe.padrao_nome, "
            "a.estado_padrao_calculado, pc.padrao_cod, pc.padrao_nome, "
            "a.diferenca::text FROM avaliacoes_validacao a "
            "JOIN amostras_validacao am USING (id_resultado) "
            "JOIN resultados r USING (id_resultado) "
            "JOIN criterios_validacao c USING (id_criterio) "
            "LEFT JOIN padroes_grupo g ON g.id_grupo = a.id_grupo "
            "LEFT JOIN padroes_subgrupo pe ON pe.id_grupo = a.id_grupo "
            "AND pe.id_padrao = a.id_padrao_esperado "
            "LEFT JOIN padroes_subgrupo pc ON pc.id_grupo = a.id_grupo "
            "AND pc.id_padrao = a.id_padrao_calculado "
            "WHERE c.ativo AND am.ativo AND a.aprovado = 'N' "
            "ORDER BY c.categoria, c.codigo, am.ordem"
        )
        linhas_divergentes = cursor.fetchall()
    criterios = []
    for linha in linhas_resumo:
        if linha[9]:
            estado_catalogo = "IMPLEMENTACAO_ALTERADA"
        elif linha[10] and linha[5] == 0:
            estado_catalogo = "NOVO_OU_REGRA_ALTERADA"
        elif linha[10]:
            estado_catalogo = "REFERENCIA_PENDENTE"
        else:
            estado_catalogo = "ATUAL"
        criterios.append({
            "codigo": linha[0], "nome": linha[1], "categoria": linha[2],
            "estado": linha[3], "exigidas": linha[4], "executadas": linha[5],
            "aprovadas": linha[6], "divergentes": linha[7], "pendentes": linha[8],
            "estado_catalogo": estado_catalogo,
        })
    divergencias = []
    for linha in linhas_divergentes:
        estado_esperado = linha[14] or linha[18]
        estado_calculado = linha[16] or linha[21]
        divergencias.append({
            "criterio": {"codigo": linha[0], "nome": linha[1], "categoria": linha[2]},
            "assinatura_atual": linha[3].strip(),
            "assinatura_executada": None if linha[4] is None else linha[4].strip(),
            "numero_ap": linha[5], "dezenas": list(linha[6:12]),
            "grupo": None if linha[12] is None else {"codigo": linha[12], "nome": linha[13]},
            "esperado": {"estado": estado_esperado, "valor": linha[15],
                          "subgrupo_codigo": linha[19], "subgrupo_nome": linha[20]},
            "calculado": {"estado": estado_calculado, "valor": linha[17],
                           "subgrupo_codigo": linha[22], "subgrupo_nome": linha[23]},
            "diferenca": linha[24],
            "hipotese_diagnostica": _hipotese_diagnostica(
                assinatura_atual=linha[3].strip(),
                assinatura_executada=None if linha[4] is None else linha[4].strip(),
                estado_esperado=estado_esperado, estado_calculado=estado_calculado,
                valor_esperado=linha[15], valor_calculado=linha[17],
                subgrupo_esperado=linha[19], subgrupo_calculado=linha[22],
            ),
        })
    fechamento = {
        "exigidas": sum(x["exigidas"] for x in criterios),
        "executadas": sum(x["executadas"] for x in criterios),
        "aprovadas": sum(x["aprovadas"] for x in criterios),
        "divergentes": sum(x["divergentes"] for x in criterios),
        "pendentes": sum(x["pendentes"] for x in criterios),
    }
    fechamento["valido"] = (
        fechamento["exigidas"] ==
        fechamento["aprovadas"] + fechamento["divergentes"] + fechamento["pendentes"]
    )
    return {"criterios": criterios, "divergencias": divergencias, "fechamento": fechamento}


def consultar_validacao(conexao, filtros: dict[str, object]) -> dict[str, object]:
    condicoes = ["am.ativo", "c.ativo"]
    parametros: list[object] = []
    categoria = filtros.get("categoria")
    criterio = filtros.get("criterio")
    grupo = filtros.get("grupo")
    subgrupo = filtros.get("subgrupo")
    situacao = filtros.get("situacao")
    if categoria:
        condicoes.append("c.categoria = %s"); parametros.append(categoria)
    if criterio:
        condicoes.append("c.codigo = %s"); parametros.append(criterio)
    if grupo:
        condicoes.append("g.grupo_cod = %s"); parametros.append(grupo)
    if subgrupo:
        condicoes.append("(pe.padrao_cod = %s OR pc.padrao_cod = %s)")
        parametros.extend((subgrupo, subgrupo))
    if situacao == "PENDENTE":
        condicoes.append("a.aprovado IS NULL")
    elif situacao:
        condicoes.append("a.aprovado = %s"); parametros.append(situacao)
    onde = " AND ".join(condicoes)
    base = (
        " FROM avaliacoes_validacao a "
        "JOIN amostras_validacao am USING (id_resultado) "
        "JOIN resultados r USING (id_resultado) "
        "JOIN criterios_validacao c USING (id_criterio) "
        "LEFT JOIN padroes_grupo g ON g.id_grupo = a.id_grupo "
        "LEFT JOIN padroes_subgrupo pe ON pe.id_grupo = a.id_grupo "
        "AND pe.id_padrao = a.id_padrao_esperado "
        "LEFT JOIN padroes_subgrupo pc ON pc.id_grupo = a.id_grupo "
        "AND pc.id_padrao = a.id_padrao_calculado WHERE " + onde
    )
    pagina = int(filtros["pagina"])
    limite = int(filtros["limite"])
    with conexao.cursor() as cursor:
        cursor.execute(
            "SELECT atualizado, motivo, alterado_em FROM estado_algoritmo_selecao "
            "WHERE id_estado = 1"
        )
        atualizado, motivo, alterado_em = cursor.fetchone()
        cursor.execute(
            "SELECT count(*), count(*) FILTER (WHERE aprovado = 'S'), "
            "count(*) FILTER (WHERE aprovado = 'N'), "
            "count(*) FILTER (WHERE aprovado IS NULL) FROM avaliacoes_validacao a "
            "JOIN amostras_validacao am USING (id_resultado) "
            "JOIN criterios_validacao c USING (id_criterio) WHERE am.ativo AND c.ativo"
        )
        resumo = cursor.fetchone()
        cursor.execute("SELECT count(*)" + base, parametros)
        total_filtrado = cursor.fetchone()[0]
        cursor.execute(
            "SELECT a.id_resultado, r.numero_ap, r.res_01, r.res_02, r.res_03, "
            "r.res_04, r.res_05, r.res_06, c.codigo, c.nome, c.categoria, "
            "c.estado, g.grupo_cod, g.grupo_nome, a.estado_valor_esperado, "
            "a.valor_esperado::text, a.estado_valor_calculado, "
            "a.valor_calculado::text, a.estado_padrao_esperado, pe.padrao_cod, "
            "pe.padrao_nome, a.estado_padrao_calculado, pc.padrao_cod, "
            "pc.padrao_nome, a.aprovado" + base +
            " ORDER BY am.ordem, c.categoria, c.codigo LIMIT %s OFFSET %s",
            (*parametros, limite, (pagina - 1) * limite),
        )
        linhas = cursor.fetchall()
        cursor.execute(
            "SELECT codigo, nome, categoria FROM criterios_validacao "
            "WHERE ativo ORDER BY categoria, nome"
        )
        criterios = cursor.fetchall()
        cursor.execute("SELECT grupo_cod, grupo_nome FROM padroes_grupo ORDER BY grupo_cod")
        grupos = cursor.fetchall()
        cursor.execute(
            "SELECT p.padrao_cod, p.padrao_nome, g.grupo_cod FROM padroes_subgrupo p "
            "JOIN padroes_grupo g USING (id_grupo) ORDER BY p.padrao_cod"
        )
        subgrupos = cursor.fetchall()
    avaliacoes = []
    for linha in linhas:
        avaliacoes.append({
            "id_resultado": linha[0], "numero_ap": linha[1],
            "dezenas": list(linha[2:8]),
            "criterio": {"codigo": linha[8], "nome": linha[9],
                          "categoria": linha[10], "estado": linha[11]},
            "grupo": None if linha[12] is None else {"codigo": linha[12], "nome": linha[13]},
            "esperado": {"estado": linha[14] or linha[18], "valor": linha[15],
                          "subgrupo_codigo": linha[19], "subgrupo_nome": linha[20]},
            "calculado": {"estado": linha[16] or linha[21], "valor": linha[17],
                           "subgrupo_codigo": linha[22], "subgrupo_nome": linha[23]},
            "aprovado": linha[24],
        })
    total_paginas = max(1, (total_filtrado + limite - 1) // limite)
    return {
        "estado_global": {
            "atualizado": atualizado, "motivo": motivo,
            "alterado_em": alterado_em.isoformat(),
            "mensagem": (
                "Algoritmo de seleção de combinações atualizado" if atualizado else
                "Algoritmo de seleção de combinações desatualizado"
            ),
        },
        "resumo": {"total": resumo[0], "aprovadas": resumo[1],
                   "reprovadas": resumo[2], "pendentes": resumo[3]},
        "paginacao": {"pagina": pagina, "limite": limite,
                      "total_itens": total_filtrado, "total_paginas": total_paginas},
        "filtros": {
            "criterios": [{"codigo": x[0], "nome": x[1], "categoria": x[2]} for x in criterios],
            "grupos": [{"codigo": x[0], "nome": x[1]} for x in grupos],
            "subgrupos": [{"codigo": x[0], "nome": x[1], "grupo_codigo": x[2]} for x in subgrupos],
        },
        "avaliacoes": avaliacoes,
    }


@validacao_api.get("/api/validacao/quadro")
def obter_quadro_validacao():
    try:
        categoria = _texto_opcional("categoria", request.args.get("categoria"))
        situacao = _texto_opcional("situacao", request.args.get("situacao"))
        if categoria and categoria not in CATEGORIAS:
            raise ErroConsultaValidacao("PARAMETRO_INVALIDO", "categoria inválida.")
        if situacao and situacao not in SITUACOES:
            raise ErroConsultaValidacao("PARAMETRO_INVALIDO", "situação inválida.")
        filtros = {
            "categoria": categoria,
            "criterio": _texto_opcional("criterio", request.args.get("criterio")),
            "grupo": _texto_opcional("grupo", request.args.get("grupo")),
            "subgrupo": _texto_opcional("subgrupo", request.args.get("subgrupo")),
            "situacao": situacao,
            "pagina": _inteiro("pagina", request.args.get("pagina"), 1, 1, 100_000),
            "limite": _inteiro("limite", request.args.get("limite"), 50, 1, 100),
        }
        return jsonify(current_app.config["CONSULTAR_VALIDACAO"](filtros))
    except ErroConsultaValidacao as erro:
        return jsonify(erro={"codigo": erro.codigo, "mensagem": str(erro)}), 400


@validacao_api.get("/api/validacao/relatorio")
def obter_relatorio_validacao():
    return jsonify(current_app.config["CONSULTAR_RELATORIO_VALIDACAO"]())


@validacao_api.get("/api/validacao/exportacao")
def exportar_validacao():
    formato = request.args.get("formato", "json").lower()
    dados = current_app.config["EXPORTAR_VALIDACAO"]()
    if formato == "json":
        conteudo, tipo, extensao = serializar_json(dados), "application/json", "json"
    elif formato == "csv":
        conteudo, tipo, extensao = serializar_csv(dados), "text/csv", "csv"
    else:
        return jsonify(erro={"codigo": "FORMATO_INVALIDO", "mensagem": "Use json ou csv."}), 400
    return Response(
        conteudo, mimetype=tipo,
        headers={"Content-Disposition": f'attachment; filename="validacao-auditoria.{extensao}"'},
    )
