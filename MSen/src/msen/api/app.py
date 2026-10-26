"""Configuração central da aplicação Flask."""

from collections.abc import Mapping
from typing import Any

from flask import Flask, jsonify
from werkzeug.exceptions import RequestEntityTooLarge

from .resultados import (
    editar_resultado_no_banco,
    importar_resultados_no_banco,
    incluir_resultado_no_banco,
    listar_resultados_do_banco,
    resultados_api,
)


def criar_app(configuracao: Mapping[str, Any] | None = None) -> Flask:
    """Cria uma instância isolada da API, adequada a testes e WSGI."""

    app = Flask(__name__, static_folder=None)
    app.config.from_mapping(
        TESTING=False,
        PROPAGATE_EXCEPTIONS=False,
        MAX_CONTENT_LENGTH=10 * 1024 * 1024,
        EDITAR_RESULTADO=editar_resultado_no_banco,
        IMPORTAR_RESULTADOS=importar_resultados_no_banco,
        INCLUIR_RESULTADO=incluir_resultado_no_banco,
        LISTAR_RESULTADOS=listar_resultados_do_banco,
    )
    if configuracao is not None:
        app.config.update(configuracao)

    @app.get("/api/saude")
    def saude():
        return jsonify(aplicacao="MSen", status="ok")

    @app.errorhandler(RequestEntityTooLarge)
    def arquivo_muito_grande(_erro):
        return jsonify(erro={
            "codigo": "ARQUIVO_MUITO_GRANDE",
            "mensagem": "A planilha excede o limite permitido de 10 MiB.",
        }), 413

    app.register_blueprint(resultados_api)

    return app
