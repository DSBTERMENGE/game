"""Valida a migração geométrica exclusivamente em PostgreSQL temporário."""

from dataclasses import replace
from datetime import date
from decimal import Decimal, localcontext
from fractions import Fraction
import json
import sys

from dotenv import load_dotenv
import psycopg

from msen.calculos import calcular_resultado
from msen.config import carregar_configuracao_banco
from msen.database import RepositorioAnaliseGeometrica, RepositorioResultados
from msen.geometria import (
    calcular_area_e_centro_gravidade,
    calcular_extensao_aberta,
    calcular_perimetro_fechado,
)
from msen.modelos import ResultadoEntrada
from suporte_banco_integracao import conectar, validar_nome


def _decimal(valor: Fraction) -> Decimal:
    with localcontext() as contexto:
        contexto.prec = 30
        return Decimal(valor.numerator) / Decimal(valor.denominator)


def _inserir_resultado(
    repositorio: RepositorioResultados, numero_ap: int, dezenas: tuple[int, ...]
):
    entrada = ResultadoEntrada.criar(
        data_resultado=date(2026, 10, numero_ap),
        numero_ap=numero_ap,
        resultados=dezenas,
    )
    return repositorio.inserir(calcular_resultado(entrada))


def _salvar_calculo(repositorio, id_resultado: int, dezenas: tuple[int, ...]):
    geometria = calcular_area_e_centro_gravidade(dezenas)
    centro = geometria.centro_gravidade
    return repositorio.salvar(
        id_resultado,
        extensao_aberta=calcular_extensao_aberta(dezenas),
        perimetro_fechado=calcular_perimetro_fechado(dezenas),
        quantidade_regioes=len(geometria.regioes),
        area_total=_decimal(geometria.area_total),
        centro_gravidade_x=None if centro is None else _decimal(centro.x),
        centro_gravidade_y=None if centro is None else _decimal(centro.y),
    )


def validar_persistencia_geometrica(nome_database: str) -> dict[str, object]:
    """Persiste figuras controladas e verifica restrições e idempotência.

    Args:
        nome_database: Database temporário previamente criado e migrado.

    Returns:
        Resumo serializável das verificações realizadas.
    """

    nome = validar_nome(nome_database)
    configuracao = replace(carregar_configuracao_banco(), nome=nome)
    with conectar(configuracao, nome) as conexao:
        with conexao.cursor() as cursor:
            cursor.execute("SELECT versao FROM schema_migrations ORDER BY versao")
            versoes = tuple(linha[0] for linha in cursor.fetchall())
        if versoes != tuple(f"{numero:03d}" for numero in range(1, 8)):
            raise AssertionError(f"Migrações inesperadas: {versoes!r}")

        resultados = RepositorioResultados(conexao)
        analises = RepositorioAnaliseGeometrica(conexao)
        simples = _inserir_resultado(resultados, 1, (1, 20, 30, 40, 50, 51))
        colinear = _inserir_resultado(resultados, 2, (1, 2, 3, 4, 5, 6))

        primeira = _salvar_calculo(analises, simples.id_resultado, simples.resultado.resultados)
        repetida = _salvar_calculo(analises, simples.id_resultado, simples.resultado.resultados)
        nula = _salvar_calculo(analises, colinear.id_resultado, colinear.resultado.resultados)

        if primeira != repetida:
            raise AssertionError("O salvamento idempotente alterou as medidas.")
        if primeira.area_total != Decimal("36.000000000000"):
            raise AssertionError(f"Área simples inesperada: {primeira.area_total}")
        if (primeira.centro_gravidade_x, primeira.centro_gravidade_y) != (
            Decimal("4.125000000000"), Decimal("2.500000000000")
        ):
            raise AssertionError("Centro de gravidade simples inesperado.")
        if nula.area_total != 0 or nula.centro_gravidade_x is not None:
            raise AssertionError("A figura colinear não preservou o estado nulo.")

        rejeitados = []
        invalidos = (
            (
                "INSERT INTO analise_geometrica_resultado "
                "(id_resultado, extensao_aberta, perimetro_fechado, "
                "quantidade_regioes, area_total, centro_gravidade_x, centro_gravidade_y) "
                "VALUES (%s, 1, 2, 0, 1, NULL, NULL)",
                (colinear.id_resultado,),
                "area_sem_regiao",
            ),
            (
                "INSERT INTO analise_geometrica_resultado "
                "(id_resultado, extensao_aberta, perimetro_fechado, "
                "quantidade_regioes, area_total, centro_gravidade_x, centro_gravidade_y) "
                "VALUES (999999, 1, 2, 1, 1, 1, 1)",
                (),
                "resultado_inexistente",
            ),
        )
        for comando, parametros, caso in invalidos:
            try:
                with conexao.transaction():
                    with conexao.cursor() as cursor:
                        cursor.execute(comando, parametros)
            except psycopg.IntegrityError:
                rejeitados.append(caso)
            else:
                raise AssertionError(f"O banco aceitou o caso inválido: {caso}")

        with conexao.transaction():
            with conexao.cursor() as cursor:
                cursor.execute("DELETE FROM resultados WHERE id_resultado = %s", (colinear.id_resultado,))
        if analises.buscar(colinear.id_resultado) is not None:
            raise AssertionError("A exclusão do resultado não removeu sua análise.")

        with conexao.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM analise_geometrica_resultado")
            quantidade = cursor.fetchone()[0]

    return {
        "migracoes": list(versoes),
        "analises_restantes": quantidade,
        "area_simples": str(primeira.area_total),
        "centro_simples": [
            str(primeira.centro_gravidade_x), str(primeira.centro_gravidade_y)
        ],
        "area_nula_validada": True,
        "salvamento_idempotente": True,
        "cascata_validada": True,
        "restricoes_rejeitadas": rejeitados,
    }


def main() -> None:
    """Executa a validação no database temporário informado."""

    load_dotenv()
    if len(sys.argv) != 2:
        raise SystemExit("Uso: validar_persistencia_geometrica.py DATABASE_TEMPORARIO")
    print(json.dumps(validar_persistencia_geometrica(sys.argv[1]), ensure_ascii=False))


if __name__ == "__main__":
    main()
