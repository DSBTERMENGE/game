"""API de leitura do quadro experimental do screener."""

from flask import Blueprint, current_app, jsonify, request

from msen.screener import gerar_quadro_screener


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
