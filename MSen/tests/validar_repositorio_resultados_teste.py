"""Valida persistência e rollback da coleção fixa em clone temporário."""

from dataclasses import replace
import os
from pathlib import Path
import subprocess
import tempfile

from dotenv import load_dotenv
import psycopg

from msen.config import carregar_configuracao_banco
from msen.database import (
    ErroRepositorioResultadosTeste,
    RepositorioResultadosTeste,
    executar_migracoes,
)
from msen.validacao import gerar_combinacoes_teste
from suporte_banco_integracao import conectar, criar_vazio, remover


RAIZ = Path(__file__).resolve().parents[2]
MIGRACOES = RAIZ / "database" / "migrations"
PG_DUMP = Path(r"C:\Program Files\PostgreSQL\16\bin\pg_dump.exe")
PG_RESTORE = Path(r"C:\Program Files\PostgreSQL\16\bin\pg_restore.exe")


def _clonar(configuracao, nome_temporario: str) -> None:
    ambiente = os.environ.copy()
    ambiente["PGPASSWORD"] = configuracao.senha
    with tempfile.TemporaryDirectory() as pasta:
        backup = Path(pasta) / "clone.dump"
        subprocess.run([
            str(PG_DUMP), "--format=custom", "--no-owner", "--no-privileges",
            "--host", configuracao.host, "--port", str(configuracao.porta),
            "--username", configuracao.usuario, "--file", str(backup),
            configuracao.nome,
        ], check=True, env=ambiente)
        subprocess.run([
            str(PG_RESTORE), "--exit-on-error", "--no-owner", "--no-privileges",
            "--host", configuracao.host, "--port", str(configuracao.porta),
            "--username", configuracao.usuario, "--dbname", nome_temporario,
            str(backup),
        ], check=True, env=ambiente)


def _esperar_erro(codigo: str, operacao) -> None:
    try:
        operacao()
    except ErroRepositorioResultadosTeste as erro:
        if erro.codigo != codigo:
            raise RuntimeError(f"Erro inesperado: {erro.codigo!r}") from erro
        return
    raise RuntimeError(f"A operação deveria falhar com {codigo}.")


def _contar(conexao) -> int:
    with conexao.cursor() as cursor:
        cursor.execute("SELECT count(*) FROM resultados_teste")
        return cursor.fetchone()[0]


def main() -> None:
    load_dotenv()
    configuracao = carregar_configuracao_banco()
    if configuracao.nome != "games":
        raise RuntimeError("A validação exige GAME_DB_NAME=games.")

    nome_temporario = f"games_test_repositorio_resultados_{os.getpid()}"
    criar_vazio(configuracao, nome_temporario)
    try:
        _clonar(configuracao, nome_temporario)
        temporaria = replace(configuracao, nome=nome_temporario)
        migracoes = executar_migracoes(temporaria, MIGRACOES)
        if migracoes.aplicadas != ("038",):
            raise RuntimeError(f"Migrações inesperadas: {migracoes.aplicadas!r}")

        colecao = gerar_combinacoes_teste()
        with conectar(configuracao, nome_temporario) as conexao:
            repositorio = RepositorioResultadosTeste(conexao)

            _esperar_erro(
                "QUANTIDADE_INVALIDA",
                lambda: repositorio.gravar_colecao_fixa(colecao[:-1]),
            )
            _esperar_erro(
                "QUANTIDADE_INVALIDA",
                lambda: repositorio.gravar_colecao_fixa((*colecao, (1, 2, 3, 4, 5, 6))),
            )
            repetida = (*colecao[:-1], tuple(reversed(colecao[0])))
            _esperar_erro(
                "COMBINACAO_REPETIDA",
                lambda: repositorio.gravar_colecao_fixa(repetida),
            )
            if _contar(conexao) != 0:
                raise RuntimeError("Uma validação anterior gravou dados parcialmente.")

            with conexao.transaction(), conexao.cursor() as cursor:
                cursor.execute(
                    "ALTER TABLE resultados_teste ADD CONSTRAINT "
                    "ck_resultados_teste_falha_simulada CHECK (FALSE)"
                )
            try:
                repositorio.gravar_colecao_fixa(colecao)
            except psycopg.errors.CheckViolation:
                pass
            else:
                raise RuntimeError("A falha simulada não interrompeu a gravação.")
            if _contar(conexao) != 0:
                raise RuntimeError("O rollback deixou linhas gravadas.")
            with conexao.transaction(), conexao.cursor() as cursor:
                cursor.execute(
                    "ALTER TABLE resultados_teste DROP CONSTRAINT "
                    "ck_resultados_teste_falha_simulada"
                )

            resultado = repositorio.gravar_colecao_fixa(colecao)
            if resultado.quantidade != 1_000 or _contar(conexao) != 1_000:
                raise RuntimeError("A gravação completa não produziu 1.000 linhas.")
            with conexao.cursor() as cursor:
                cursor.execute(
                    "SELECT res_01,res_02,res_03,res_04,res_05,res_06 "
                    "FROM resultados_teste ORDER BY id_resultado_teste LIMIT 10"
                )
                primeiras = tuple(cursor.fetchall())
            if primeiras != colecao[:10]:
                raise RuntimeError("A ordem gerada não foi preservada no banco.")

            _esperar_erro(
                "COLECAO_JA_EXISTENTE",
                lambda: repositorio.gravar_colecao_fixa(colecao),
            )
            if _contar(conexao) != 1_000:
                raise RuntimeError("A segunda carga alterou a coleção fixa.")

        print(
            "Persistência validada: 1.000 linhas, ordem preservada, "
            "rollback íntegro e segunda carga recusada."
        )
    finally:
        remover(configuracao, nome_temporario)


if __name__ == "__main__":
    main()
