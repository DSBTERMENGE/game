"""API de leitura do quadro experimental do screener."""

from flask import Blueprint, current_app, jsonify, request

from msen.screener import (
    ErroConfiguracaoScreener,
    gerar_quadro_screener,
    validar_limite_raridade,
)


screener_api = Blueprint("screener_api", __name__)


@screener_api.get("/api/screener/quadro")
def obter_quadro_screener():
    """Executa a amostra protegida e retorna quadro e casos de validação."""

    bruto = request.args.get("limite_validacoes", "30")
    try:
        limite = int(bruto)
    except (TypeError, ValueError):
        return jsonify(erro={
            "codigo": "LIMITE_VALIDACOES_INVALIDO",
            "mensagem": "limite_validacoes deve ser um número inteiro",
        }), 400
    if not 1 <= limite <= 200:
        return jsonify(erro={
            "codigo": "LIMITE_VALIDACOES_INVALIDO",
            "mensagem": "limite_validacoes deve estar entre 1 e 200",
        }), 400
    executor = current_app.config["GERAR_QUADRO_SCREENER"]
    return jsonify(executor(limite))


@screener_api.post("/api/screener/quadro-extensivel")
def obter_quadro_screener_extensivel():
    """Executa somente a amostra fixa do novo funil em três níveis."""

    dados = request.get_json(silent=True)
    if dados is None and request.data:
        return jsonify(erro={
            "codigo": "CONFIGURACAO_RARIDADE_INVALIDA",
            "mensagem": "O corpo deve ser um objeto JSON válido.",
        }), 400
    if dados is None:
        dados = {}
    if not isinstance(dados, dict) or set(dados).difference({"limite_raridade"}):
        return jsonify(erro={
            "codigo": "CONFIGURACAO_RARIDADE_INVALIDA",
            "mensagem": "Informe somente o limite percentual de raridade.",
        }), 400
    try:
        limite = (
            None
            if "limite_raridade" not in dados
            else validar_limite_raridade(dados["limite_raridade"])
        )
    except ErroConfiguracaoScreener as erro:
        return jsonify(erro={"codigo": erro.codigo, "mensagem": str(erro)}), 400
    try:
        executor = current_app.config["GERAR_QUADRO_SCREENER_EXTENSIVEL"]
        return jsonify(executor(limite))
    except Exception as erro:
        codigo = getattr(erro, "codigo", "ENSAIO_EXTENSIVEL_INDISPONIVEL")
        current_app.logger.exception("Falha no ensaio extensível")
        return jsonify(erro={
            "codigo": codigo,
            "mensagem": "Não foi possível executar a amostra protegida.",
        }), 503
