"""Valida a subetapa 20.5-A em PostgreSQL temporário."""

from dataclasses import replace
from datetime import date
import json
from pathlib import Path
import sys

from dotenv import load_dotenv

from msen.calculos import calcular_resultado
from msen.config import carregar_configuracao_banco
from msen.database import abrir_conexao, executar_migracoes, RepositorioResultados
from msen.modelos import ResultadoEntrada
from msen.services import (
    atualizar_perfis_operacionais_atuais,
    marcar_perfis_operacionais_desatualizados,
)
from suporte_banco_integracao import criar_vazio, remover, validar_nome


MIGRACOES = Path(__file__).resolve().parents[2] / "database" / "migrations"


def _inserir(repositorio, numero_ap, dezenas):
    entrada = ResultadoEntrada.criar(
        data_resultado=date(2026, 10, 30), numero_ap=numero_ap, resultados=dezenas
    )
    return repositorio.inserir(calcular_resultado(entrada))


def validar(nome_database: str) -> dict[str, object]:
    nome = validar_nome(nome_database)
    base = carregar_configuracao_banco()
    criar_vazio(base, nome)
    configuracao = replace(base, nome=nome)
    try:
        executar_migracoes(configuracao, MIGRACOES)
        with abrir_conexao(configuracao) as conexao:
            repositorio = RepositorioResultados(conexao)
            resultados = (
                _inserir(repositorio, 950001, (1, 2, 3, 4, 5, 6)),
                _inserir(repositorio, 950002, (4, 9, 10, 13, 39, 52)),
                _inserir(repositorio, 950003, (7, 14, 21, 28, 35, 42)),
            )
            conexao.commit()
            with conexao.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO amostras_validacao (id_resultado, ordem) VALUES (%s, 1)",
                    (resultados[0].id_resultado,),
                )
                cursor.execute(
                    "INSERT INTO criterios_validacao (codigo, nome, categoria, "
                    "funcao_python, tipo_resultado, assinatura_funcao, assinatura_regra, "
                    "estado) VALUES ('TESTE_SOMA', 'Soma', 'ESTATISTICA', 'teste.soma', "
                    "'INTEIRO', %s, %s, 'APROVADO') RETURNING id_criterio",
                    ("a" * 64, "b" * 64),
                )
                criterio = cursor.fetchone()[0]
                cursor.execute(
                    "INSERT INTO avaliacoes_validacao (id_resultado, id_criterio, "
                    "referencia_conferida, estado_valor_esperado, valor_esperado, "
                    "estado_valor_calculado, valor_calculado, referencia_origem, "
                    "referencia_revisor, referencia_conferida_em, executado, "
                    "assinatura_executada, aprovado, diferenca, calculado_em) VALUES "
                    "(%s, %s, TRUE, 'VALOR_IDENTIFICADO', 21, 'VALOR_IDENTIFICADO', "
                    "21, 'TESTE_AUTOMATIZADO', 'validador 20.5-A', CURRENT_TIMESTAMP, "
                    "TRUE, %s, 'S', 0, CURRENT_TIMESTAMP)",
                    (resultados[0].id_resultado, criterio, "a" * 64),
                )
            conexao.commit()

            marcar_perfis_operacionais_desatualizados(conexao)
            conexao.commit()
            with conexao.cursor() as cursor:
                cursor.execute("SELECT atualizado, motivo FROM estado_algoritmo_selecao")
                if cursor.fetchone() != (False, "NOVOS_RESULTADOS_AGUARDANDO_PERFIS"):
                    raise AssertionError("O bloqueio anterior ao recálculo não foi persistido.")

            primeiro = atualizar_perfis_operacionais_atuais(conexao)
            conexao.commit()
            if primeiro.quantidade_resultados != 3:
                raise AssertionError("O primeiro perfil não usou os três resultados.")
            with conexao.cursor() as cursor:
                cursor.execute(
                    "SELECT categoria, count(*) FROM perfis_operacionais_atuais "
                    "GROUP BY categoria ORDER BY categoria"
                )
                categorias = dict(cursor.fetchall())
                cursor.execute(
                    "SELECT count(*) FROM perfis_operacionais_atuais "
                    "WHERE quantidade_resultados = 3"
                )
                perfis_completos = cursor.fetchone()[0]
                cursor.execute(
                    "SELECT referencia_conferida, valor_esperado, valor_calculado, "
                    "aprovado FROM avaliacoes_validacao WHERE id_criterio = %s",
                    (criterio,),
                )
                avaliacao = cursor.fetchone()
            if categorias != {"ESTATISTICA": 4, "GEOMETRIA": 6} or perfis_completos != 10:
                raise AssertionError("Os dez perfis atuais não foram reconciliados.")
            if avaliacao != (True, 21, 21, "S"):
                raise AssertionError("A atualização dos perfis alterou a homologação.")

            _inserir(repositorio, 950004, (11, 22, 33, 44, 55, 60))
            conexao.commit()
            marcar_perfis_operacionais_desatualizados(conexao)
            conexao.commit()
            segundo = atualizar_perfis_operacionais_atuais(conexao)
            conexao.commit()
            if segundo.quantidade_resultados != 4:
                raise AssertionError("O segundo perfil não incorporou o resultado novo.")
            if primeiro.assinatura_conjunto_resultados == segundo.assinatura_conjunto_resultados:
                raise AssertionError("A assinatura do conjunto não mudou.")
            with conexao.cursor() as cursor:
                cursor.execute(
                    "SELECT quantidade_resultados, assinatura_conjunto_resultados, "
                    "atualizado, motivo FROM estado_algoritmo_selecao"
                )
                estado = cursor.fetchone()
                cursor.execute(
                    "SELECT count(*) FROM padroes_subgrupo WHERE total_sorteios = 4"
                )
                padroes = cursor.fetchone()[0]
            if estado != (
                4, segundo.assinatura_conjunto_resultados, False,
                "HOMOLOGACAO_OU_COBERTURA_PENDENTE",
            ):
                raise AssertionError(f"Estado final divergente: {estado!r}")
            if padroes != 9:
                raise AssertionError("As incidências não usam o total atual.")

        return {
            "dez_perfis_substituiveis": True,
            "estatisticos_e_geometricos": True,
            "padroes_recalculados": True,
            "classificacoes_recalculadas": True,
            "assinatura_do_conjunto": True,
            "novo_resultado_incorporado": True,
            "homologacao_preservada": True,
            "estado_permanece_bloqueado": True,
        }
    finally:
        remover(base, nome)


def main() -> None:
    load_dotenv()
    if len(sys.argv) != 2:
        raise SystemExit("Uso: validar_perfis_operacionais_atuais.py NOME_TEMPORARIO")
    print(json.dumps(validar(sys.argv[1]), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
