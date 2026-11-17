"""Valida a migração 037 somente em um clone PostgreSQL temporário."""

from dataclasses import replace
import json
import os
from pathlib import Path
import subprocess
import tempfile

from dotenv import load_dotenv

from msen.config import carregar_configuracao_banco
from msen.database import executar_migracoes
from msen.padroes import resolver_funcao_detectora
from msen.services import sincronizar_criterios_validacao
from msen.validacao import criar_registro_criterios_producao

from suporte_banco_integracao import conectar, criar_vazio, remover


RAIZ = Path(__file__).resolve().parents[2]
MIGRACOES = RAIZ / "database" / "migrations"
PG_DUMP = Path(r"C:\Program Files\PostgreSQL\16\bin\pg_dump.exe")
PG_RESTORE = Path(r"C:\Program Files\PostgreSQL\16\bin\pg_restore.exe")
FUNCAO = "msen.padroes.duas_linhas.detectar_dezenas_em_duas_linhas"


def _estado(configuracao, nome: str) -> tuple[str, object, int, int]:
    with conectar(configuracao, nome) as conexao:
        with conexao.cursor() as cursor:
            cursor.execute("SELECT max(versao) FROM schema_migrations")
            versao = cursor.fetchone()[0]
            cursor.execute(
                "SELECT funcao_detectora FROM padroes_subgrupo "
                "WHERE id_padrao=17 AND id_grupo=8"
            )
            linha = cursor.fetchone()
            if linha is None:
                raise RuntimeError("O padrão id_padrao=17 e id_grupo=8 não existe.")
            cursor.execute("SELECT count(*) FROM criterios_validacao")
            criterios = cursor.fetchone()[0]
            cursor.execute("SELECT count(*) FROM avaliacoes_validacao")
            avaliacoes = cursor.fetchone()[0]
    return versao, linha[0], criterios, avaliacoes


def main() -> None:
    load_dotenv()
    configuracao = carregar_configuracao_banco()
    if configuracao.nome != "games":
        raise RuntimeError("A validação exige GAME_DB_NAME=games.")
    if not PG_DUMP.is_file() or not PG_RESTORE.is_file():
        raise FileNotFoundError("pg_dump ou pg_restore não encontrado.")

    nome_temporario = f"games_test_7_1_{os.getpid()}"
    real_antes = _estado(configuracao, configuracao.nome)
    if real_antes[0] != "036" or real_antes[1] is not None:
        raise RuntimeError(f"Estado inicial do banco real inesperado: {real_antes!r}")

    ambiente = os.environ.copy()
    ambiente["PGPASSWORD"] = configuracao.senha
    criar_vazio(configuracao, nome_temporario)
    try:
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

        configuracao_temporaria = replace(configuracao, nome=nome_temporario)
        migracoes = executar_migracoes(configuracao_temporaria, MIGRACOES)
        if migracoes.aplicadas != ("037",):
            raise RuntimeError(f"Migrações inesperadas: {migracoes!r}")

        with conectar(configuracao, nome_temporario) as conexao:
            relatorio = sincronizar_criterios_validacao(
                conexao, criar_registro_criterios_producao()
            )
            conexao.commit()
            repeticao = sincronizar_criterios_validacao(
                conexao, criar_registro_criterios_producao()
            )
            conexao.commit()
            with conexao.cursor() as cursor:
                cursor.execute(
                    "SELECT c.id_padrao, c.id_grupo, c.categoria, c.tipo_resultado, "
                    "c.estado, p.funcao_detectora FROM criterios_validacao c "
                    "JOIN padroes_subgrupo p USING (id_padrao) "
                    "WHERE c.codigo='PAD_PD_011'"
                )
                criterio = cursor.fetchone()

        esperado = (17, 8, "PADRAO", "PADRAO", "PENDENTE", FUNCAO)
        if criterio != esperado:
            raise RuntimeError(f"Critério sincronizado inesperado: {criterio!r}")
        if relatorio.incluidos != ("PAD_PD_011",):
            raise RuntimeError(f"Inclusões inesperadas: {relatorio!r}")
        if repeticao.houve_alteracao or repeticao.avaliacoes_criadas:
            raise RuntimeError("A sincronização repetida não foi idempotente.")

        detector = resolver_funcao_detectora(criterio[-1])
        if not detector((1, 2, 3, 11, 12, 13)):
            raise RuntimeError("O detector recusou uma combinação em duas linhas.")
        if detector((1, 11, 21, 31, 41, 51)):
            raise RuntimeError("O detector aceitou uma combinação em seis linhas.")

        temporario = _estado(configuracao, nome_temporario)
        print(json.dumps({
            "banco_real_antes": real_antes,
            "migracoes_aplicadas_no_temporario": migracoes.aplicadas,
            "criterio_incluido": relatorio.incluidos,
            "avaliacoes_criadas": relatorio.avaliacoes_criadas,
            "criterio": criterio,
            "banco_temporario": temporario,
            "sincronizacao_idempotente": True,
            "detector_validado": True,
        }, ensure_ascii=False, indent=2, default=list))
    finally:
        remover(configuracao, nome_temporario)

    real_depois = _estado(configuracao, configuracao.nome)
    if real_depois != real_antes:
        raise RuntimeError(
            f"O banco real foi alterado: antes={real_antes!r}, depois={real_depois!r}"
        )
    print(json.dumps({"banco_real_depois": real_depois}, default=list))


if __name__ == "__main__":
    main()
