"""Configuração central da aplicação Flask."""

from collections.abc import Mapping
from pathlib import Path
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
from .padroes import (
    criar_padrao_no_banco,
    editar_padrao_no_banco,
    excluir_padrao_no_banco,
    listar_padroes_do_banco,
    padroes_api,
)


def criar_app(configuracao: Mapping[str, Any] | None = None) -> Flask:
    """Cria uma instância isolada da API, adequada a testes e WSGI."""

    frontend = Path(__file__).resolve().parents[4] / "frontend"
    app = Flask(
        __name__,
        static_folder=str(frontend),
        static_url_path="",
    )
    app.config.from_mapping(
        TESTING=False,
        PROPAGATE_EXCEPTIONS=False,
        MAX_CONTENT_LENGTH=10 * 1024 * 1024,
        EDITAR_RESULTADO=editar_resultado_no_banco,
        IMPORTAR_RESULTADOS=importar_resultados_no_banco,
        INCLUIR_RESULTADO=incluir_resultado_no_banco,
        LISTAR_RESULTADOS=listar_resultados_do_banco,
        CRIAR_PADRAO=criar_padrao_no_banco,
        EDITAR_PADRAO=editar_padrao_no_banco,
        EXCLUIR_PADRAO=excluir_padrao_no_banco,
        LISTAR_PADROES=listar_padroes_do_banco,
    )
    if configuracao is not None:
        app.config.update(configuracao)

    @app.get("/api/saude")
    def saude():
        return jsonify(aplicacao="MSen", status="ok")

    @app.get("/")
    def pagina_inicial():
        return app.send_static_file("index.html")

    @app.errorhandler(RequestEntityTooLarge)
    def arquivo_muito_grande(_erro):
        return jsonify(erro={
            "codigo": "ARQUIVO_MUITO_GRANDE",
            "mensagem": "A planilha excede o limite permitido de 10 MiB.",
        }), 413

    app.register_blueprint(resultados_api)
    app.register_blueprint(padroes_api)

    return app
