"""Valida, sem escrita, o catálogo e os executores contra o banco games."""

import json

from dotenv import load_dotenv

from msen.config import carregar_configuracao_banco
from msen.database import abrir_conexao
from msen.modelos import ResultadoEntrada
from msen.padroes import criar_fotografia_historica_diagonal
from msen.services import (
    carregar_catalogo_filtros_validacao,
    processar_validacao_nova_no_banco,
)


def _carregar_combinacoes(cursor) -> tuple[tuple[int, ...], ...]:
    cursor.execute(
        "SELECT res_01,res_02,res_03,res_04,res_05,res_06 "
        "FROM resultados_teste ORDER BY id_resultado_teste"
    )
    return tuple(tuple(linha) for linha in cursor.fetchall())


def _carregar_historico(cursor) -> tuple[ResultadoEntrada, ...]:
    cursor.execute(
        "SELECT data_resultado,numero_ap,res_01,res_02,res_03,res_04,res_05,res_06 "
        "FROM resultados ORDER BY numero_ap"
    )
    return tuple(
        ResultadoEntrada.criar(
            data_resultado=linha[0],
            numero_ap=linha[1],
            resultados=linha[2:],
        )
        for linha in cursor.fetchall()
    )


def main() -> None:
    load_dotenv()
    configuracao = carregar_configuracao_banco()
    if configuracao.nome != "games":
        raise RuntimeError("A validação integrada exige GAME_DB_NAME=games.")

    with abrir_conexao(configuracao) as conexao, conexao.cursor() as cursor:
        catalogo = carregar_catalogo_filtros_validacao(conexao)
        combinacoes = _carregar_combinacoes(cursor)
        historico = _carregar_historico(cursor)
        fotografia = criar_fotografia_historica_diagonal(historico)

        filtros = tuple(
            (grupo, filtro)
            for grupo in catalogo
            for filtro in grupo.filtros
        )
        if len(combinacoes) != 1_000:
            raise RuntimeError(
                f"A coleção de controle deveria conter 1.000 itens; contém {len(combinacoes)}."
            )
        if len(filtros) != 12:
            raise RuntimeError(
                f"Eram esperados 12 filtros executáveis; foram encontrados {len(filtros)}."
            )

        relatorio = processar_validacao_nova_no_banco(
            conexao,
            fotografia_diagonal=fotografia,
        )

    print(json.dumps({
        "banco": configuracao.nome,
        "grupos_executaveis": len(catalogo),
        "filtros_executaveis": len(filtros),
        "combinacoes_por_filtro": relatorio.total_combinacoes,
        "avaliacoes_totais": relatorio.total_avaliacoes,
        "filtros": [
            {
                "id_grupo": item.id_grupo,
                "grupo": item.nome_grupo,
                "id_filtro": item.id_filtro,
                "filtro": item.nome_filtro,
                "testadas": item.total_testado,
                "ocorrencias": item.ocorrencias,
                "incidencia_percentual": str(item.incidencia_percentual),
            }
            for item in relatorio.resultados
        ],
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
