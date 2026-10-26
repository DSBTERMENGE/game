"""Entrada WSGI para servidores de produção, inclusive PythonAnywhere."""

from msen.api import criar_app


application = criar_app()
