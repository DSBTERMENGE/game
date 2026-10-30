"""Valida a migração 013 exclusivamente em database PostgreSQL temporário."""

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
ASSINATURA_CATALOGO = "c" * 64
ASSINATURA_RESULTADOS = "d" * 64


def _copiar_migracoes(destino: Path, versao_final: int) -> None:
    for caminho in sorted(MIGRACOES.glob("[0-9][0-9][0-9]_*.sql")):
        if int(caminho.name[:3]) <= versao_final:
            shutil.copy2(caminho, destino / caminho.name)


def _exigir_rejeicao(conexao, comando: str, parametros=()) -> None:
    try:
        with conexao.transaction():
            with conexao.cursor() as cursor:
                cursor.execute(comando, parametros)
    except (psycopg.IntegrityError, psycopg.errors.RaiseException):
        return
    raise AssertionError("O PostgreSQL aceitou um estado global inválido.")


def _validar_casos(configuracao, nome: str) -> dict[str, object]:
    with conectar(configuracao, nome) as conexao:
        with conexao.cursor() as cursor:
            cursor.execute(
                "SELECT id_estado, atualizado, motivo, quantidade_resultados "
                "FROM estado_algoritmo_selecao"
            )
            inicial = cursor.fetchone()
        if inicial != (1, False, "AGUARDANDO_HOMOLOGACAO_INICIAL", 0):
            raise AssertionError(f"Estado inicial inesperado: {inicial!r}")

        _exigir_rejeicao(
            conexao,
            "INSERT INTO estado_algoritmo_selecao (id_estado) VALUES (2)",
        )
        _exigir_rejeicao(
            conexao,
            "UPDATE estado_algoritmo_selecao SET atualizado = TRUE WHERE id_estado = 1",
        )
        _exigir_rejeicao(
            conexao,
            "UPDATE estado_algoritmo_selecao SET quantidade_resultados = -1 "
            "WHERE id_estado = 1",
        )
        _exigir_rejeicao(
            conexao,
            "DELETE FROM estado_algoritmo_selecao WHERE id_estado = 1",
        )

        with conexao.cursor() as cursor:
            cursor.execute(
                "UPDATE estado_algoritmo_selecao SET "
                "atualizado = TRUE, motivo = 'TODAS_AS_CONDICOES_CONFIRMADAS', "
                "assinatura_catalogo_homologado = %s, "
                "assinatura_conjunto_resultados = %s, quantidade_resultados = 3069, "
                "homologado_em = CURRENT_TIMESTAMP, "
                "perfis_atualizados_em = CURRENT_TIMESTAMP, "
                "cobertura_confirmada_em = CURRENT_TIMESTAMP, "
                "alterado_em = CURRENT_TIMESTAMP WHERE id_estado = 1",
                (ASSINATURA_CATALOGO, ASSINATURA_RESULTADOS),
            )
            cursor.execute(
                "SELECT atualizado, quantidade_resultados, "
                "assinatura_catalogo_homologado, assinatura_conjunto_resultados "
                "FROM estado_algoritmo_selecao WHERE id_estado = 1"
            )
            liberado = cursor.fetchone()
        conexao.commit()
        if liberado != (
            True, 3069, ASSINATURA_CATALOGO, ASSINATURA_RESULTADOS
        ):
            raise AssertionError(f"Estado liberado inesperado: {liberado!r}")

        with conexao.cursor() as cursor:
            cursor.execute(
                "UPDATE estado_algoritmo_selecao SET atualizado = FALSE, "
                "motivo = 'NOVOS_RESULTADOS_PENDENTES', alterado_em = CURRENT_TIMESTAMP "
                "WHERE id_estado = 1 RETURNING atualizado, motivo"
            )
            desatualizado = cursor.fetchone()
        conexao.commit()
        if desatualizado != (False, "NOVOS_RESULTADOS_PENDENTES"):
            raise AssertionError(f"Transição de bloqueio inesperada: {desatualizado!r}")

    return {
        "estado_inicial_desatualizado": True,
        "segunda_linha_rejeitada": True,
        "liberacao_sem_evidencias_rejeitada": True,
        "quantidade_negativa_rejeitada": True,
        "exclusao_rejeitada": True,
        "liberacao_com_evidencias": True,
        "retorno_a_desatualizado": True,
    }


def validar(nome_database: str) -> dict[str, object]:
    nome = validar_nome(nome_database)
    configuracao_base = carregar_configuracao_banco()
    criar_vazio(configuracao_base, nome)
    configuracao = replace(configuracao_base, nome=nome)
    try:
        with tempfile.TemporaryDirectory() as pasta:
            anteriores = Path(pasta)
            _copiar_migracoes(anteriores, 12)
            relatorio_anterior = executar_migracoes(configuracao, anteriores)

        relatorio_primeira = executar_migracoes(configuracao, MIGRACOES)
        relatorio_segunda = executar_migracoes(configuracao, MIGRACOES)
        if relatorio_primeira.aplicadas != ("013",):
            raise AssertionError(f"Primeira execução inesperada: {relatorio_primeira}")
        todas = tuple(f"{numero:03d}" for numero in range(1, 14))
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
            "Uso: validar_migracao_estado_algoritmo_selecao.py NOME_TEMPORARIO"
        )
    print(json.dumps(validar(sys.argv[1]), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
