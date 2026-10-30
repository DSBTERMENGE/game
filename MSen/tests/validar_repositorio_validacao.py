"""Valida o repositório da subetapa 20.4 em PostgreSQL temporário."""

from dataclasses import replace
import json
from pathlib import Path
import sys

from dotenv import load_dotenv

from msen.config import carregar_configuracao_banco
from msen.database import abrir_conexao, executar_migracoes, RepositorioValidacao
from suporte_banco_integracao import criar_vazio, remover, validar_nome


MIGRACOES = Path(__file__).resolve().parents[2] / "database" / "migrations"
ASSINATURA_A = "a" * 64
ASSINATURA_B = "b" * 64
ASSINATURA_C = "c" * 64


def _inserir_resultado(cursor, numero_ap: int, dezenas: tuple[int, ...]) -> int:
    cursor.execute(
        "INSERT INTO resultados (data_resultado, numero_ap, res_01, res_02, res_03, "
        "res_04, res_05, res_06, soma_res, media_aritmetica_res, mediana_res, "
        "desvio_padrao_media, media_coordenada_x, media_coordenada_y) "
        "VALUES (DATE '2026-10-30', %s, %s, %s, %s, %s, %s, %s, 21, 3.5, 3.5, "
        "1.707825, 2.5, 0) RETURNING id_resultado",
        (numero_ap, *dezenas),
    )
    return cursor.fetchone()[0]


def validar(nome_database: str) -> dict[str, object]:
    nome = validar_nome(nome_database)
    base = carregar_configuracao_banco()
    criar_vazio(base, nome)
    configuracao = replace(base, nome=nome)
    try:
        executar_migracoes(configuracao, MIGRACOES)
        with abrir_conexao(configuracao) as conexao:
            with conexao.cursor() as cursor:
                resultado_1 = _inserir_resultado(cursor, 930001, (4, 9, 10, 13, 39, 52))
                resultado_2 = _inserir_resultado(cursor, 930002, (1, 2, 3, 4, 5, 6))
                cursor.execute(
                    "SELECT id_grupo FROM padroes_grupo WHERE grupo_cod = 'PG_001'"
                )
                id_grupo = cursor.fetchone()[0]
                cursor.execute(
                    "SELECT id_padrao FROM padroes_subgrupo "
                    "WHERE id_grupo = %s AND padrao_cod = 'PD_001'",
                    (id_grupo,),
                )
                id_padrao = cursor.fetchone()[0]
                cursor.execute(
                    "INSERT INTO criterios_validacao (codigo, nome, categoria, "
                    "funcao_python, tipo_resultado, assinatura_funcao) VALUES "
                    "('EST_SOMA', 'Soma', 'ESTATISTICA', 'msen.calculos.soma', "
                    "'INTEIRO', %s) RETURNING id_criterio",
                    (ASSINATURA_A,),
                )
                criterio_soma = cursor.fetchone()[0]
                cursor.execute(
                    "INSERT INTO criterios_validacao (codigo, nome, categoria, "
                    "funcao_python, tipo_resultado, id_grupo, assinatura_funcao) VALUES "
                    "('PAD_SEQ', 'Sequenciais', 'PADRAO', 'msen.padroes.sequenciais', "
                    "'PADRAO', %s, %s) RETURNING id_criterio",
                    (id_grupo, ASSINATURA_B),
                )
                criterio_padrao = cursor.fetchone()[0]
            conexao.commit()

            repositorio = RepositorioValidacao(conexao)
            amostra_1 = repositorio.incluir_amostra(resultado_1, 1)
            amostra_2 = repositorio.incluir_amostra(resultado_2, 2)
            conexao.commit()
            if amostra_1.dezenas != (4, 9, 10, 13, 39, 52):
                raise AssertionError("As dezenas não foram resolvidas por JOIN.")
            if len(repositorio.listar_avaliacoes()) != 4:
                raise AssertionError("A inclusão não criou a matriz inicial esperada.")

            with conexao.cursor() as cursor:
                cursor.execute(
                    "UPDATE avaliacoes_validacao SET referencia_conferida = TRUE, "
                    "valor_esperado = 115 WHERE id_resultado = %s AND id_criterio = %s",
                    (resultado_1, criterio_soma),
                )
                cursor.execute(
                    "UPDATE avaliacoes_validacao SET referencia_conferida = TRUE, "
                    "estado_padrao_esperado = 'PADRAO_IDENTIFICADO', "
                    "id_padrao_esperado = %s WHERE id_resultado = %s "
                    "AND id_criterio = %s",
                    (id_padrao, resultado_1, criterio_padrao),
                )
            conexao.commit()

            if repositorio.sincronizar_avaliacoes_pendentes() != 0:
                raise AssertionError("A sincronização repetida duplicou avaliações.")
            conexao.commit()
            preservada = next(
                item for item in repositorio.listar_avaliacoes(id_resultado=resultado_1)
                if item.id_criterio == criterio_soma
            )
            if preservada.valor_esperado != 115:
                raise AssertionError("A sincronização alterou o resultado esperado.")
            padrao = next(
                item for item in repositorio.listar_avaliacoes(id_resultado=resultado_1)
                if item.id_criterio == criterio_padrao
            )
            if padrao.grupo_codigo != "PG_001" or padrao.subgrupo_esperado_codigo != "PD_001":
                raise AssertionError("Grupo ou subgrupo não foi resolvido por JOIN.")

            if not repositorio.desativar_amostra(resultado_2):
                raise AssertionError("A amostra ativa não foi desativada.")
            conexao.commit()
            with conexao.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO criterios_validacao (codigo, nome, categoria, "
                    "funcao_python, tipo_resultado, precisao_decimal, assinatura_funcao) "
                    "VALUES ('EST_MEDIA', 'Média', 'ESTATISTICA', 'msen.calculos.media', "
                    "'DECIMAL', 2, %s) RETURNING id_criterio",
                    (ASSINATURA_C,),
                )
                criterio_novo = cursor.fetchone()[0]
            conexao.commit()
            criadas = repositorio.sincronizar_avaliacoes_pendentes()
            conexao.commit()
            if criadas != 1:
                raise AssertionError(f"Esperada uma avaliação nova; obtidas {criadas}.")
            with conexao.cursor() as cursor:
                cursor.execute(
                    "SELECT id_resultado FROM avaliacoes_validacao "
                    "WHERE id_criterio = %s",
                    (criterio_novo,),
                )
                ids_novos = [linha[0] for linha in cursor.fetchall()]
            if ids_novos != [resultado_1]:
                raise AssertionError("Critério novo foi associado a amostra inativa.")
            if repositorio.listar_amostras(somente_ativas=True) != (amostra_1,):
                raise AssertionError("A consulta de amostras ativas divergiu.")
            if amostra_2.ativo is not True:
                raise AssertionError("O modelo retornado foi alterado após persistência.")

        return {
            "inclusao_amostra_e_avaliacoes": True,
            "dezenas_por_join": True,
            "grupo_e_subgrupo_por_join": True,
            "sincronizacao_idempotente": True,
            "esperado_preservado": True,
            "criterio_novo_somente_amostras_ativas": True,
            "desativacao_sem_exclusao": True,
        }
    finally:
        remover(base, nome)


def main() -> None:
    load_dotenv()
    if len(sys.argv) != 2:
        raise SystemExit("Uso: validar_repositorio_validacao.py NOME_TEMPORARIO")
    print(json.dumps(validar(sys.argv[1]), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
