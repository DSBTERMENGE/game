"""Valida a sincronização da subetapa 20.5 em PostgreSQL temporário."""

from dataclasses import replace
import json
from pathlib import Path
import sys

from dotenv import load_dotenv

from msen.config import carregar_configuracao_banco
from msen.database import abrir_conexao, executar_migracoes, RepositorioValidacao
from msen.services import (
    ExclusaoCriteriosNaoConfirmada,
    sincronizar_criterios_validacao,
)
from msen.validacao import DefinicaoCriterio, RegistroCriteriosValidacao
from suporte_banco_integracao import criar_vazio, remover, validar_nome


MIGRACOES = Path(__file__).resolve().parents[2] / "database" / "migrations"


def calcular_a(valor):
    return valor


def calcular_a_corrigido(valor):
    return valor + 0


def calcular_b(valor):
    return valor


def _definicao(codigo, funcao, regra):
    return DefinicaoCriterio(
        codigo, codigo, "ESTATISTICA", funcao, "INTEIRO", regra
    )


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
                    "media_coordenada_y) VALUES (DATE '2026-10-30', 940001, "
                    "1, 2, 3, 4, 5, 6, 21, 3.5, 3.5, 1.707825, 2.5, 0) "
                    "RETURNING id_resultado"
                )
                id_resultado = cursor.fetchone()[0]
            conexao.commit()
            RepositorioValidacao(conexao).incluir_amostra(id_resultado, 1)
            conexao.commit()

            inicial = RegistroCriteriosValidacao((
                _definicao("CRIT_A", calcular_a, "Regra A"),
                _definicao("CRIT_B", calcular_b, "Regra B"),
            ))
            relatorio = sincronizar_criterios_validacao(conexao, inicial)
            conexao.commit()
            if relatorio.incluidos != ("CRIT_A", "CRIT_B") or relatorio.avaliacoes_criadas != 2:
                raise AssertionError(f"Inclusão inicial divergente: {relatorio!r}")

            with conexao.cursor() as cursor:
                cursor.execute(
                    "SELECT id_criterio FROM criterios_validacao WHERE codigo = 'CRIT_A'"
                )
                id_criterio = cursor.fetchone()[0]
                cursor.execute(
                    "UPDATE avaliacoes_validacao SET referencia_conferida = TRUE, "
                    "estado_valor_esperado = 'VALOR_IDENTIFICADO', valor_esperado = 21, "
                    "estado_valor_calculado = 'VALOR_IDENTIFICADO', valor_calculado = 21, "
                    "referencia_origem = 'TESTE_AUTOMATIZADO', "
                    "referencia_revisor = 'validador 20.5', "
                    "referencia_conferida_em = CURRENT_TIMESTAMP, executado = TRUE, "
                    "assinatura_executada = (SELECT assinatura_funcao FROM "
                    "criterios_validacao WHERE id_criterio = %s), aprovado = 'S', "
                    "diferenca = 0, calculado_em = CURRENT_TIMESTAMP "
                    "WHERE id_resultado = %s AND id_criterio = %s",
                    (id_criterio, id_resultado, id_criterio),
                )
            conexao.commit()

            implementacao = RegistroCriteriosValidacao((
                _definicao("CRIT_A", calcular_a_corrigido, "Regra A"),
                _definicao("CRIT_B", calcular_b, "Regra B"),
            ))
            alterada = sincronizar_criterios_validacao(conexao, implementacao)
            conexao.commit()
            if alterada.implementacoes_alteradas != ("CRIT_A",):
                raise AssertionError("A alteração de implementação não foi reconhecida.")
            with conexao.cursor() as cursor:
                cursor.execute(
                    "SELECT referencia_conferida, valor_esperado, executado, aprovado "
                    "FROM avaliacoes_validacao WHERE id_criterio = %s",
                    (id_criterio,),
                )
                apos_codigo = cursor.fetchone()
            if apos_codigo != (True, 21, False, None):
                raise AssertionError(f"Esperado não foi preservado: {apos_codigo!r}")

            regra = RegistroCriteriosValidacao((
                _definicao("CRIT_A", calcular_a_corrigido, "Regra A modificada"),
                _definicao("CRIT_B", calcular_b, "Regra B"),
            ))
            alterada = sincronizar_criterios_validacao(conexao, regra)
            conexao.commit()
            if alterada.regras_alteradas != ("CRIT_A",):
                raise AssertionError("A alteração de regra não foi reconhecida.")
            with conexao.cursor() as cursor:
                cursor.execute(
                    "SELECT referencia_conferida, valor_esperado FROM "
                    "avaliacoes_validacao WHERE id_criterio = %s",
                    (id_criterio,),
                )
                apos_regra = cursor.fetchone()
            if apos_regra != (False, None):
                raise AssertionError(f"Referência de regra antiga permaneceu: {apos_regra!r}")

            somente_a = RegistroCriteriosValidacao((
                _definicao("CRIT_A", calcular_a_corrigido, "Regra A modificada"),
            ))
            try:
                sincronizar_criterios_validacao(conexao, somente_a)
            except ExclusaoCriteriosNaoConfirmada as erro:
                if erro.codigos != ("CRIT_B",):
                    raise
            else:
                raise AssertionError("A exclusão sem confirmação foi aceita.")
            excluida = sincronizar_criterios_validacao(
                conexao, somente_a, confirmar_exclusoes=True
            )
            conexao.commit()
            if excluida.excluidos != ("CRIT_B",):
                raise AssertionError("A exclusão confirmada não foi executada.")

            repetida = sincronizar_criterios_validacao(conexao, somente_a)
            conexao.commit()
            if repetida.houve_alteracao or repetida.avaliacoes_criadas:
                raise AssertionError("A sincronização idempotente alterou dados.")
            with conexao.cursor() as cursor:
                cursor.execute(
                    "SELECT atualizado, motivo FROM estado_algoritmo_selecao"
                )
                estado = cursor.fetchone()
            if estado != (False, "CATALOGO_DE_CRITERIOS_ALTERADO"):
                raise AssertionError(f"Estado global inesperado: {estado!r}")

        return {
            "criterios_novos_pendentes": True,
            "avaliacoes_criadas": True,
            "implementacao_preserva_esperado": True,
            "regra_invalida_esperado": True,
            "exclusao_exige_confirmacao": True,
            "exclusao_confirmada_em_cascata": True,
            "sincronizacao_idempotente": True,
            "estado_global_desatualizado": True,
        }
    finally:
        remover(base, nome)


def main() -> None:
    load_dotenv()
    if len(sys.argv) != 2:
        raise SystemExit("Uso: validar_sincronizacao_criterios.py NOME_TEMPORARIO")
    print(json.dumps(validar(sys.argv[1]), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
