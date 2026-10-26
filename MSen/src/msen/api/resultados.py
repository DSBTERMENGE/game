"""Rotas de consulta e importação dos resultados."""

from dataclasses import asdict, replace
from decimal import Decimal
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Callable

import psycopg
from flask import Blueprint, current_app, jsonify, request

from msen.config import ErroConfiguracaoBanco, carregar_configuracao_banco
from msen.database import (
    ErroConexaoBanco,
    ErroRepositorioResultado,
    RepositorioResultados,
    ResultadoPersistido,
    abrir_conexao,
)
from msen.importacao import ErroLeituraExcel
from msen.modelos import ErroValidacaoResultado, ResultadoEntrada
from msen.services import (
    RelatorioImportacaoBanco,
    editar_resultado,
    importar_planilha_no_banco,
    incluir_resultado,
)


resultados_api = Blueprint("resultados_api", __name__)


def listar_resultados_do_banco() -> tuple[ResultadoPersistido, ...]:
    """Abre a conexão somente durante a consulta e devolve todo o histórico."""

    configuracao = carregar_configuracao_banco()
    with abrir_conexao(configuracao) as conexao:
        return RepositorioResultados(conexao).listar(limite=10_000)


def importar_resultados_no_banco(caminho: str | Path) -> RelatorioImportacaoBanco:
    """Importa uma planilha usando uma conexão curta e transacional."""

    configuracao = carregar_configuracao_banco()
    with abrir_conexao(configuracao) as conexao:
        return importar_planilha_no_banco(conexao, caminho)


def incluir_resultado_no_banco(entrada: ResultadoEntrada) -> ResultadoPersistido:
    configuracao = carregar_configuracao_banco()
    with abrir_conexao(configuracao) as conexao:
        return incluir_resultado(conexao, entrada)


def editar_resultado_no_banco(entrada: ResultadoEntrada) -> ResultadoPersistido:
    configuracao = carregar_configuracao_banco()
    with abrir_conexao(configuracao) as conexao:
        return editar_resultado(conexao, entrada)


def _decimal_texto(valor: Decimal) -> str:
    return format(valor, "f")


def serializar_resultado(persistido: ResultadoPersistido) -> dict[str, object]:
    resultado = persistido.resultado
    return {
        "id_resultado": persistido.id_resultado,
        "data_resultado": resultado.data_resultado.isoformat(),
        "numero_ap": resultado.numero_ap,
        "dezenas": list(resultado.resultados),
        "res_01": resultado.res_01,
        "res_02": resultado.res_02,
        "res_03": resultado.res_03,
        "res_04": resultado.res_04,
        "res_05": resultado.res_05,
        "res_06": resultado.res_06,
        "soma_res": resultado.soma_res,
        "media_aritmetica_res": _decimal_texto(resultado.media_aritmetica_res),
        "mediana_res": _decimal_texto(resultado.mediana_res),
        "desvio_padrao_media": _decimal_texto(resultado.desvio_padrao_media),
        "media_coordenada_x": _decimal_texto(resultado.media_coordenada_x),
        "media_coordenada_y": _decimal_texto(resultado.media_coordenada_y),
        "versao_calculo": resultado.versao_calculo,
    }


@resultados_api.get("/api/resultados")
def listar_resultados():
    servico: Callable[[], tuple[ResultadoPersistido, ...]] = current_app.config[
        "LISTAR_RESULTADOS"
    ]
    try:
        persistidos = tuple(sorted(servico(), key=lambda item: item.numero_ap))
    except (
        ErroConfiguracaoBanco,
        ErroConexaoBanco,
        ErroRepositorioResultado,
        psycopg.Error,
    ):
        return jsonify(
            erro={
                "codigo": "BANCO_INDISPONIVEL",
                "mensagem": "Não foi possível consultar os resultados.",
            }
        ), 503

    resultados = [serializar_resultado(item) for item in persistidos]
    return jsonify(resultados=resultados, total=len(resultados))


def _erro(codigo: str, mensagem: str, status: int):
    return jsonify(erro={"codigo": codigo, "mensagem": mensagem}), status


@resultados_api.post("/api/resultados/importar")
def importar_resultados():
    arquivo = request.files.get("arquivo")
    if arquivo is None or not arquivo.filename:
        return _erro("ARQUIVO_AUSENTE", "Selecione uma planilha XLSX.", 400)

    nome_original = Path(arquivo.filename).name
    if Path(nome_original).suffix.casefold() != ".xlsx":
        return _erro(
            "FORMATO_NAO_SUPORTADO",
            "A fonte deve ser uma planilha no formato .xlsx.",
            415,
        )

    servico: Callable[[str | Path], RelatorioImportacaoBanco] = current_app.config[
        "IMPORTAR_RESULTADOS"
    ]
    try:
        with TemporaryDirectory(prefix="msen-upload-") as pasta:
            temporario = Path(pasta) / "fonte.xlsx"
            arquivo.save(temporario)
            if temporario.stat().st_size == 0:
                return _erro("ARQUIVO_VAZIO", "A planilha enviada está vazia.", 400)
            relatorio = servico(temporario)
    except ErroLeituraExcel as erro:
        return _erro(erro.codigo, str(erro), 422)
    except (
        ErroConfiguracaoBanco,
        ErroConexaoBanco,
        ErroRepositorioResultado,
        psycopg.Error,
    ):
        return _erro(
            "IMPORTACAO_INDISPONIVEL",
            "Não foi possível armazenar os resultados. Nenhuma alteração parcial foi confirmada.",
            503,
        )

    relatorio = replace(relatorio, arquivo=nome_original)
    return jsonify(
        mensagem=f"Importação concluída: {relatorio.inseridas} resultado(s) inserido(s).",
        relatorio=asdict(relatorio),
    ), 200


def _entrada_json(numero_url: int | None = None) -> ResultadoEntrada:
    dados = request.get_json(silent=True)
    if not isinstance(dados, dict):
        raise ErroValidacaoResultado(
            "JSON_INVALIDO", "O corpo deve ser um objeto JSON.", campo="corpo"
        )

    numero_corpo = dados.get("numero_ap")
    if numero_url is not None:
        if numero_corpo is not None and numero_corpo != numero_url:
            raise ErroValidacaoResultado(
                "NUMERO_AP_DIVERGENTE",
                "O número da URL deve ser igual ao número informado no corpo.",
                campo="numero_ap",
                valor=numero_corpo,
            )
        numero_corpo = numero_url

    dezenas = dados.get("dezenas")
    if dezenas is None and any(f"res_{indice:02d}" in dados for indice in range(1, 7)):
        dezenas = [dados.get(f"res_{indice:02d}") for indice in range(1, 7)]

    data = dados.get("data_resultado")
    if isinstance(data, str):
        partes = data.strip().split("-")
        if len(partes) == 3 and all(parte.isdigit() for parte in partes):
            data = "/".join(reversed(partes))

    return ResultadoEntrada.criar(
        data_resultado=data,
        numero_ap=numero_corpo,
        resultados=dezenas,
    )


def _executar_gravacao(
    servico: Callable[[ResultadoEntrada], ResultadoPersistido],
    entrada: ResultadoEntrada,
):
    try:
        persistido = servico(entrada)
    except ErroRepositorioResultado as erro:
        if erro.codigo == "RESULTADO_DUPLICADO":
            return _erro(erro.codigo, "O concurso já está cadastrado.", 409)
        if erro.codigo == "RESULTADO_NAO_ENCONTRADO":
            return _erro(erro.codigo, "O concurso não foi encontrado.", 404)
        return _erro(
            "GRAVACAO_INDISPONIVEL",
            "Não foi possível salvar o resultado. Nenhuma alteração parcial foi confirmada.",
            503,
        )
    except (ErroConfiguracaoBanco, ErroConexaoBanco, psycopg.Error):
        return _erro(
            "GRAVACAO_INDISPONIVEL",
            "Não foi possível salvar o resultado. Nenhuma alteração parcial foi confirmada.",
            503,
        )
    return jsonify(resultado=serializar_resultado(persistido))


@resultados_api.post("/api/resultados")
def incluir_resultado_api():
    try:
        entrada = _entrada_json()
    except ErroValidacaoResultado as erro:
        return _erro(erro.codigo, str(erro), 400)
    servico = current_app.config["INCLUIR_RESULTADO"]
    resposta = _executar_gravacao(servico, entrada)
    if isinstance(resposta, tuple):
        return resposta
    return resposta, 201


@resultados_api.put("/api/resultados/<int:numero_ap>")
def editar_resultado_api(numero_ap: int):
    try:
        entrada = _entrada_json(numero_ap)
    except ErroValidacaoResultado as erro:
        status = 409 if erro.codigo == "NUMERO_AP_DIVERGENTE" else 400
        return _erro(erro.codigo, str(erro), status)
    servico = current_app.config["EDITAR_RESULTADO"]
    return _executar_gravacao(servico, entrada)
