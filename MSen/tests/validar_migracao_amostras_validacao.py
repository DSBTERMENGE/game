"""Valida a migração 011 exclusivamente em database PostgreSQL temporário."""

from dataclasses import replace
import json
from pathlib import Path
import shutil
import sys
import tempfile

from dotenv import load_dotenv
import psycopg

from msen.config import carregar_configuracao_banco
from msen.database import executar_migracoes
from suporte_banco_integracao import conectar, criar_vazio, remover, validar_nome


RAIZ = Path(__file__).resolve().parents[2]
MIGRACOES = RAIZ / "database" / "migrations"


def _copiar_migracoes(destino: Path, versao_final: int) -> None:
    for caminho in sorted(MIGRACOES.glob("[0-9][0-9][0-9]_*.sql")):
        if int(caminho.name[:3]) <= versao_final:
            shutil.copy2(caminho, destino / caminho.name)


def _inserir_resultado(cursor: psycopg.Cursor, numero_ap: int) -> int:
    cursor.execute(
        "INSERT INTO resultados ("
        "data_resultado, numero_ap, res_01, res_02, res_03, res_04, res_05, res_06, "
        "soma_res, media_aritmetica_res, mediana_res, desvio_padrao_media, "
        "media_coordenada_x, media_coordenada_y"
        ") VALUES (DATE '2026-10-29', %s, 1, 2, 3, 4, 5, 6, "
        "21, 3.5, 3.5, 1.707825, 2.5, 0) RETURNING id_resultado",
        (numero_ap,),
    )
    return cursor.fetchone()[0]


def _exigir_rejeicao(conexao, comando: str, parametros: tuple[object, ...]) -> None:
    try:
        with conexao.transaction():
            with conexao.cursor() as cursor:
                cursor.execute(comando, parametros)
    except psycopg.IntegrityError:
        return
    raise AssertionError("O PostgreSQL aceitou uma amostra inválida.")


def _validar_restricoes(configuracao, nome: str) -> dict[str, object]:
    with conectar(configuracao, nome) as conexao:
        with conexao.cursor() as cursor:
            resultado_1 = _inserir_resultado(cursor, 910001)
            resultado_2 = _inserir_resultado(cursor, 910002)
            cursor.execute(
                "INSERT INTO amostras_validacao (id_resultado, ordem) VALUES (%s, 1)",
                (resultado_1,),
            )
        conexao.commit()

        inserir = "INSERT INTO amostras_validacao (id_resultado, ordem) VALUES (%s, %s)"
        _exigir_rejeicao(conexao, inserir, (resultado_1, 2))
        _exigir_rejeicao(conexao, inserir, (resultado_2, 1))
        _exigir_rejeicao(conexao, inserir, (resultado_2, 0))
        _exigir_rejeicao(conexao, inserir, (9_999_999, 2))

        with conexao.cursor() as cursor:
            cursor.execute(
                "SELECT r.res_01, r.res_02, r.res_03, r.res_04, r.res_05, r.res_06, a.ativo "
                "FROM amostras_validacao a INNER JOIN resultados r USING (id_resultado) "
                "WHERE a.id_resultado = %s",
                (resultado_1,),
            )
            linha = cursor.fetchone()
            if linha != (1, 2, 3, 4, 5, 6, True):
                raise AssertionError(f"JOIN inesperado: {linha}")
            cursor.execute("DELETE FROM resultados WHERE id_resultado = %s", (resultado_1,))
            cursor.execute(
                "SELECT count(*) FROM amostras_validacao WHERE id_resultado = %s",
                (resultado_1,),
            )
            if cursor.fetchone()[0] != 0:
                raise AssertionError("A exclusão do resultado não removeu a amostra.")
        conexao.commit()
    return {
        "pk_rejeitada": True,
        "ordem_duplicada_rejeitada": True,
        "ordem_zero_rejeitada": True,
        "fk_inexistente_rejeitada": True,
        "join_dezenas": "confirmado",
        "cascade_resultado": "confirmado",
    }


def validar(nome_database: str) -> dict[str, object]:
    nome = validar_nome(nome_database)
    configuracao_base = carregar_configuracao_banco()
    criar_vazio(configuracao_base, nome)
    configuracao = replace(configuracao_base, nome=nome)
    try:
        with tempfile.TemporaryDirectory() as pasta:
            anteriores = Path(pasta)
            _copiar_migracoes(anteriores, 10)
            relatorio_anterior = executar_migracoes(configuracao, anteriores)

        relatorio_primeira = executar_migracoes(configuracao, MIGRACOES)
        relatorio_segunda = executar_migracoes(configuracao, MIGRACOES)
        if relatorio_primeira.aplicadas != ("011",):
            raise AssertionError(f"Primeira execução inesperada: {relatorio_primeira}")
        todas = tuple(f"{numero:03d}" for numero in range(1, 12))
        if relatorio_segunda.aplicadas or relatorio_segunda.ja_aplicadas != todas:
            raise AssertionError(f"Segunda execução inesperada: {relatorio_segunda}")

        return {
            "migracoes_anteriores": list(relatorio_anterior.aplicadas),
            "aplicadas_primeira_execucao": list(relatorio_primeira.aplicadas),
            "ja_aplicadas_segunda_execucao": list(relatorio_segunda.ja_aplicadas),
            "restricoes": _validar_restricoes(configuracao, nome),
        }
    finally:
        remover(configuracao_base, nome)


def main() -> None:
    load_dotenv()
    if len(sys.argv) != 2:
        raise SystemExit("Uso: validar_migracao_amostras_validacao.py NOME_TEMPORARIO")
    print(json.dumps(validar(sys.argv[1]), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
