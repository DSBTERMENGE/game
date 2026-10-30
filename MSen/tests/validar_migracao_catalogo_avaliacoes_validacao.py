"""Valida a migração 012 exclusivamente em database PostgreSQL temporário."""

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
ASSINATURA_A = "a" * 64
ASSINATURA_B = "b" * 64


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
    raise AssertionError("O PostgreSQL aceitou um catálogo ou avaliação inválida.")


def _preparar_dados(conexao) -> dict[str, int]:
    with conexao.cursor() as cursor:
        resultado_1 = _inserir_resultado(cursor, 920001)
        resultado_2 = _inserir_resultado(cursor, 920002)
        cursor.execute(
            "INSERT INTO amostras_validacao (id_resultado, ordem) "
            "VALUES (%s, 1), (%s, 2)",
            (resultado_1, resultado_2),
        )
        cursor.execute(
            "SELECT g.id_grupo, p.id_padrao FROM padroes_grupo g "
            "JOIN padroes_subgrupo p USING (id_grupo) "
            "WHERE g.grupo_cod = 'PG_001' AND p.padrao_cod = 'PD_001'"
        )
        grupo_1, padrao_1 = cursor.fetchone()
        cursor.execute(
            "SELECT g.id_grupo, p.id_padrao FROM padroes_grupo g "
            "JOIN padroes_subgrupo p USING (id_grupo) "
            "WHERE g.grupo_cod = 'PG_002' AND p.padrao_cod = 'PD_004'"
        )
        grupo_2, padrao_2 = cursor.fetchone()
        cursor.execute(
            "INSERT INTO criterios_validacao "
            "(codigo, nome, categoria, funcao_python, tipo_resultado, assinatura_funcao) "
            "VALUES ('EST_SOMA', 'Soma', 'ESTATISTICA', 'msen.calculos.soma', "
            "'INTEIRO', %s) RETURNING id_criterio",
            (ASSINATURA_A,),
        )
        criterio_numerico = cursor.fetchone()[0]
        cursor.execute(
            "INSERT INTO criterios_validacao "
            "(codigo, nome, categoria, funcao_python, tipo_resultado, id_grupo, "
            "assinatura_funcao) VALUES ('PAD_SEQ', 'Sequenciais', 'PADRAO', "
            "'msen.padroes.classificacao', 'PADRAO', %s, %s) RETURNING id_criterio",
            (grupo_1, ASSINATURA_B),
        )
        criterio_padrao = cursor.fetchone()[0]
    conexao.commit()
    return {
        "resultado_1": resultado_1,
        "resultado_2": resultado_2,
        "grupo_1": grupo_1,
        "grupo_2": grupo_2,
        "padrao_1": padrao_1,
        "padrao_2": padrao_2,
        "criterio_numerico": criterio_numerico,
        "criterio_padrao": criterio_padrao,
    }


def _validar_casos(configuracao, nome: str) -> dict[str, object]:
    with conectar(configuracao, nome) as conexao:
        dados = _preparar_dados(conexao)
        with conexao.cursor() as cursor:
            cursor.execute(
                "INSERT INTO avaliacoes_validacao "
                "(id_resultado, id_criterio, referencia_conferida, valor_esperado, "
                "valor_calculado, executado, assinatura_executada, aprovado, "
                "diferenca, calculado_em) VALUES (%s, %s, TRUE, 21, 21, TRUE, "
                "%s, 'S', 0, CURRENT_TIMESTAMP)",
                (dados["resultado_1"], dados["criterio_numerico"], ASSINATURA_A),
            )
            cursor.execute(
                "INSERT INTO avaliacoes_validacao "
                "(id_resultado, id_criterio, id_grupo, referencia_conferida, "
                "estado_padrao_esperado, id_padrao_esperado, executado, "
                "estado_padrao_calculado, id_padrao_calculado, assinatura_executada, "
                "aprovado, calculado_em) VALUES (%s, %s, %s, TRUE, "
                "'PADRAO_IDENTIFICADO', %s, TRUE, 'PADRAO_IDENTIFICADO', %s, %s, "
                "'S', CURRENT_TIMESTAMP)",
                (
                    dados["resultado_1"], dados["criterio_padrao"], dados["grupo_1"],
                    dados["padrao_1"], dados["padrao_1"], ASSINATURA_B,
                ),
            )
            cursor.execute(
                "INSERT INTO avaliacoes_validacao "
                "(id_resultado, id_criterio, id_grupo, referencia_conferida, "
                "estado_padrao_esperado, executado, estado_padrao_calculado, "
                "assinatura_executada, aprovado, calculado_em) VALUES "
                "(%s, %s, %s, TRUE, 'SEM_CORRESPONDENCIA', TRUE, "
                "'SEM_CORRESPONDENCIA', %s, 'S', CURRENT_TIMESTAMP)",
                (
                    dados["resultado_2"], dados["criterio_padrao"],
                    dados["grupo_1"], ASSINATURA_B,
                ),
            )
        conexao.commit()

        _exigir_rejeicao(
            conexao,
            "INSERT INTO criterios_validacao "
            "(codigo, nome, categoria, funcao_python, tipo_resultado, assinatura_funcao) "
            "VALUES ('INV_ASS', 'Inválido', 'ESTATISTICA', 'f', 'INTEIRO', 'x')",
            (),
        )
        _exigir_rejeicao(
            conexao,
            "INSERT INTO criterios_validacao "
            "(codigo, nome, categoria, funcao_python, tipo_resultado, assinatura_funcao) "
            "VALUES ('INV_CAT', 'Inválido', 'PADRAO', 'f', 'INTEIRO', %s)",
            (ASSINATURA_A,),
        )
        _exigir_rejeicao(
            conexao,
            "INSERT INTO avaliacoes_validacao "
            "(id_resultado, id_criterio, referencia_conferida, valor_esperado, "
            "aprovado) VALUES (%s, %s, TRUE, 21, 'S')",
            (dados["resultado_2"], dados["criterio_numerico"]),
        )
        _exigir_rejeicao(
            conexao,
            "INSERT INTO avaliacoes_validacao "
            "(id_resultado, id_criterio, id_grupo, referencia_conferida, "
            "estado_padrao_esperado, id_padrao_esperado) VALUES "
            "(%s, %s, %s, TRUE, 'PADRAO_IDENTIFICADO', %s)",
            (
                dados["resultado_2"], dados["criterio_padrao"],
                dados["grupo_1"], dados["padrao_2"],
            ),
        )

        with conexao.cursor() as cursor:
            cursor.execute(
                "DELETE FROM criterios_validacao WHERE id_criterio = %s",
                (dados["criterio_numerico"],),
            )
            cursor.execute(
                "SELECT count(*) FROM avaliacoes_validacao WHERE id_criterio = %s",
                (dados["criterio_numerico"],),
            )
            if cursor.fetchone()[0] != 0:
                raise AssertionError("A exclusão do critério não removeu avaliações.")
            cursor.execute(
                "DELETE FROM amostras_validacao WHERE id_resultado = %s",
                (dados["resultado_1"],),
            )
            cursor.execute(
                "SELECT count(*) FROM avaliacoes_validacao WHERE id_resultado = %s",
                (dados["resultado_1"],),
            )
            if cursor.fetchone()[0] != 0:
                raise AssertionError("A exclusão da amostra não removeu avaliações.")
        conexao.commit()

    return {
        "avaliacao_numerica": "confirmada",
        "avaliacao_padrao": "confirmada",
        "sem_correspondencia": "confirmado",
        "assinatura_invalida_rejeitada": True,
        "categoria_tipo_invalida_rejeitada": True,
        "aprovacao_pendente_rejeitada": True,
        "padrao_de_outro_grupo_rejeitado": True,
        "cascade_criterio": "confirmado",
        "cascade_amostra": "confirmado",
    }


def validar(nome_database: str) -> dict[str, object]:
    nome = validar_nome(nome_database)
    configuracao_base = carregar_configuracao_banco()
    criar_vazio(configuracao_base, nome)
    configuracao = replace(configuracao_base, nome=nome)
    try:
        with tempfile.TemporaryDirectory() as pasta:
            anteriores = Path(pasta)
            _copiar_migracoes(anteriores, 11)
            relatorio_anterior = executar_migracoes(configuracao, anteriores)

        relatorio_primeira = executar_migracoes(configuracao, MIGRACOES)
        relatorio_segunda = executar_migracoes(configuracao, MIGRACOES)
        if relatorio_primeira.aplicadas != ("012",):
            raise AssertionError(f"Primeira execução inesperada: {relatorio_primeira}")
        todas = tuple(f"{numero:03d}" for numero in range(1, 13))
        if relatorio_segunda.aplicadas or relatorio_segunda.ja_aplicadas != todas:
            raise AssertionError(f"Segunda execução inesperada: {relatorio_segunda}")

        return {
            "migracoes_anteriores": list(relatorio_anterior.aplicadas),
            "aplicadas_primeira_execucao": list(relatorio_primeira.aplicadas),
            "ja_aplicadas_segunda_execucao": list(relatorio_segunda.ja_aplicadas),
            "casos": _validar_casos(configuracao, nome),
        }
    finally:
        remover(configuracao_base, nome)


def main() -> None:
    load_dotenv()
    if len(sys.argv) != 2:
        raise SystemExit(
            "Uso: validar_migracao_catalogo_avaliacoes_validacao.py NOME_TEMPORARIO"
        )
    print(json.dumps(validar(sys.argv[1]), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
