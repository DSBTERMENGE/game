"""Gera e grava uma única vez a coleção fixa no banco games."""

from collections import Counter
import json
import sys

from dotenv import load_dotenv

from msen.config import carregar_configuracao_banco
from msen.database import abrir_conexao, RepositorioResultadosTeste
from msen.validacao import chave_canonica, gerar_combinacoes_teste


def main() -> None:
    load_dotenv()
    if sys.argv[1:] != ["CONFIRMAR_COLECAO_RESULTADOS_13_1_8"]:
        raise SystemExit(
            "Uso: aplicar_colecao_resultados_teste_games.py "
            "CONFIRMAR_COLECAO_RESULTADOS_13_1_8"
        )
    configuracao = carregar_configuracao_banco()
    if configuracao.nome != "games":
        raise RuntimeError("A operação exige GAME_DB_NAME=games.")

    colecao = gerar_combinacoes_teste()
    chaves = {chave_canonica(item) for item in colecao}
    if len(colecao) != 1_000 or len(chaves) != 1_000:
        raise RuntimeError("A coleção gerada não contém 1.000 combinações únicas.")

    with abrir_conexao(configuracao) as conexao:
        with conexao.cursor() as cursor:
            cursor.execute("SELECT max(versao) FROM schema_migrations")
            versao = cursor.fetchone()[0]
            cursor.execute("SELECT count(*) FROM resultados_teste")
            quantidade_antes = cursor.fetchone()[0]
        if versao != "038" or quantidade_antes != 0:
            raise RuntimeError(
                f"Estado inicial inesperado: versão={versao!r}, "
                f"registros={quantidade_antes}."
            )

        with conexao.transaction():
            resultado = RepositorioResultadosTeste(conexao).gravar_colecao_fixa(
                colecao
            )
            with conexao.cursor() as cursor:
                cursor.execute(
                    "SELECT res_01,res_02,res_03,res_04,res_05,res_06 "
                    "FROM resultados_teste ORDER BY id_resultado_teste"
                )
                persistidas = tuple(cursor.fetchall())
            if resultado.quantidade != 1_000 or persistidas != colecao:
                raise RuntimeError("O conteúdo persistido diverge da coleção gerada.")
            if len({chave_canonica(item) for item in persistidas}) != 1_000:
                raise RuntimeError("O banco contém combinações equivalentes.")

    frequencias = Counter(dezena for item in colecao for dezena in item)
    print(json.dumps({
        "migracao": versao,
        "quantidade_antes": quantidade_antes,
        "quantidade_depois": len(colecao),
        "chaves_canonicas_distintas": len(chaves),
        "ordem_preservada": True,
        "menor_frequencia": min(frequencias.values()),
        "maior_frequencia": max(frequencias.values()),
        "primeiras_cinco": colecao[:5],
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
