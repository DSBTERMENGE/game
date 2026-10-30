"""Valida a carga das 200 amostras em PostgreSQL temporário."""

from dataclasses import replace
import json
from pathlib import Path
import sys

from dotenv import load_dotenv

from msen.config import carregar_configuracao_banco
from msen.database import abrir_conexao, executar_migracoes, RepositorioValidacao
from msen.services import (
    carregar_amostras_iniciais_validacao,
    sincronizar_criterios_validacao,
)
from msen.validacao import criar_registro_criterios_producao
from suporte_banco_integracao import criar_vazio, remover, validar_nome


MIGRACOES = Path(__file__).resolve().parents[2] / "database" / "migrations"


def validar(nome_database: str) -> dict[str, object]:
    nome = validar_nome(nome_database)
    base = carregar_configuracao_banco()
    criar_vazio(base, nome)
    configuracao = replace(base, nome=nome)
    try:
        executar_migracoes(configuracao, MIGRACOES)
        with abrir_conexao(configuracao) as conexao:
            with conexao.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO resultados (data_resultado, numero_ap, res_01, res_02, "
                    "res_03, res_04, res_05, res_06, soma_res, media_aritmetica_res, "
                    "mediana_res, desvio_padrao_media, media_coordenada_x, "
                    "media_coordenada_y) SELECT DATE '2026-10-30', numero, "
                    "1, 2, 3, 4, 5, 6, 21, 3.5, 3.5, 1.707825, 2.5, 0 "
                    "FROM generate_series(1, 205) AS numero"
                )
            conexao.commit()
            sincronizar_criterios_validacao(
                conexao, criar_registro_criterios_producao()
            )
            conexao.commit()

            primeira = carregar_amostras_iniciais_validacao(conexao)
            conexao.commit()
            if (
                primeira.amostras_incluidas != 200
                or primeira.avaliacoes_criadas != 3800
                or primeira.primeiro_numero_ap != 1
                or primeira.ultimo_numero_ap != 200
            ):
                raise AssertionError(f"Primeira carga divergente: {primeira!r}")

            with conexao.cursor() as cursor:
                cursor.execute(
                    "SELECT a.ordem, r.numero_ap, r.res_01, r.res_06 "
                    "FROM amostras_validacao a JOIN resultados r USING (id_resultado) "
                    "WHERE a.ordem IN (1, 200) ORDER BY a.ordem"
                )
                extremos = cursor.fetchall()
                cursor.execute(
                    "SELECT count(*) FROM information_schema.columns WHERE "
                    "table_schema = 'public' AND table_name = 'amostras_validacao' "
                    "AND column_name LIKE 'res_%'"
                )
                dezenas_duplicadas = cursor.fetchone()[0]
                cursor.execute(
                    "SELECT count(*) FROM avaliacoes_validacao WHERE "
                    "referencia_conferida OR executado OR aprovado IS NOT NULL OR "
                    "valor_esperado IS NOT NULL OR valor_calculado IS NOT NULL"
                )
                preenchidas = cursor.fetchone()[0]
            if extremos != [(1, 1, 1, 6), (200, 200, 1, 6)]:
                raise AssertionError(f"Ordem ou JOIN divergente: {extremos!r}")
            if dezenas_duplicadas or preenchidas:
                raise AssertionError("A carga duplicou dezenas ou antecipou resultados.")

            segunda = carregar_amostras_iniciais_validacao(conexao)
            conexao.commit()
            if segunda.amostras_incluidas or segunda.avaliacoes_criadas:
                raise AssertionError("A repetição da carga não foi idempotente.")

            with conexao.cursor() as cursor:
                cursor.execute(
                    "SELECT id_resultado FROM resultados WHERE numero_ap = 205"
                )
                resultado_extra = cursor.fetchone()[0]
            RepositorioValidacao(conexao).incluir_amostra(resultado_extra, 201)
            conexao.commit()
            terceira = carregar_amostras_iniciais_validacao(conexao)
            conexao.commit()
            with conexao.cursor() as cursor:
                cursor.execute("SELECT count(*) FROM amostras_validacao")
                total_amostras = cursor.fetchone()[0]
                cursor.execute("SELECT count(*) FROM avaliacoes_validacao")
                total_avaliacoes = cursor.fetchone()[0]
                cursor.execute("SELECT atualizado, motivo FROM estado_algoritmo_selecao")
                estado = cursor.fetchone()
            if terceira.amostras_ja_existentes != 200:
                raise AssertionError("A base inicial deixou de ser reconhecida.")
            if (total_amostras, total_avaliacoes) != (201, 3819):
                raise AssertionError("A amostra adicional não foi preservada.")
            if estado != (False, "AMOSTRAS_AGUARDANDO_REFERENCIAS_E_CALCULOS"):
                raise AssertionError(f"Estado global inesperado: {estado!r}")

        return {
            "duzentas_amostras": True,
            "tres_mil_e_oitocentas_avaliacoes": True,
            "ordem_por_numero_ap": True,
            "dezenas_somente_por_join": True,
            "avaliacoes_pendentes": True,
            "carga_idempotente": True,
            "amostra_adicional_preservada": True,
            "estado_global_bloqueado": True,
        }
    finally:
        remover(base, nome)


def main() -> None:
    load_dotenv()
    if len(sys.argv) != 2:
        raise SystemExit("Uso: validar_carga_amostras_validacao.py NOME_TEMPORARIO")
    print(json.dumps(validar(sys.argv[1]), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
