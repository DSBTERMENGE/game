"""Valida a persistência dos padrões de mesma linha em database temporário."""

from dataclasses import replace
from datetime import date, timedelta
import json
import sys

from dotenv import load_dotenv

from msen.calculos import calcular_resultado
from msen.config import carregar_configuracao_banco
from msen.database import RepositorioPadroes, RepositorioResultados
from msen.modelos import ResultadoEntrada
from msen.services import recalcular_padroes_iniciais
from suporte_banco_integracao import conectar, validar_nome


RESULTADOS_CONTROLADOS = (
    (10, (1, 5, 18, 27, 44, 59)),
    (20, (1, 12, 23, 34, 45, 56)),
    (25, (1, 5, 12, 18, 44, 59)),
    (40, (21, 25, 30, 34, 45, 56)),
    (50, (1, 5, 9, 12, 18, 44)),
    (60, (31, 33, 36, 40, 45, 56)),
    (80, (1, 2, 3, 4, 5, 6)),
)


def validar_persistencia_linhas(nome_database: str) -> dict[str, object]:
    """Recalcula duas vezes e confere os padrões de mesma linha.

    Parâmetros:
        nome_database: Nome previamente criado dentro do padrão seguro de teste.

    Retorno:
        Resumo serializável das estatísticas e verificações executadas.

    Regra:
        O database deve ser temporário e já ter recebido todas as migrações. A
        função não acessa o database local `games`.
    """

    nome = validar_nome(nome_database)
    configuracao = replace(carregar_configuracao_banco(), nome=nome)
    with conectar(configuracao, nome) as conexao:
        cadastrados = RepositorioPadroes(conexao).listar("PG_003")
        if tuple(item.padrao_cod for item in cadastrados) != (
            "PD_007",
            "PD_008",
            "PD_009",
        ):
            raise AssertionError(f"Catálogo de linhas inesperado: {cadastrados!r}")

        resultados = RepositorioResultados(conexao)
        for numero_ap, dezenas in RESULTADOS_CONTROLADOS:
            entrada = ResultadoEntrada.criar(
                data_resultado=date(2020, 1, 1) + timedelta(days=numero_ap),
                numero_ap=numero_ap,
                resultados=dezenas,
            )
            resultados.inserir(calcular_resultado(entrada))

        primeiro = recalcular_padroes_iniciais(conexao)
        segundo = recalcular_padroes_iniciais(conexao)
        obtido = {
            item.padrao_cod: (
                item.num_oco,
                None if item.intervalo_medio is None else str(item.intervalo_medio),
                None if item.desv_padrao is None else str(item.desv_padrao),
            )
            for item in segundo.padroes
            if item.padrao_cod in {"PD_007", "PD_008", "PD_009"}
        }
        esperado = {
            "PD_007": (2, "15.000000", "0.000000"),
            "PD_008": (2, "10.000000", "0.000000"),
            "PD_009": (2, "20.000000", "0.000000"),
        }
        if obtido != esperado:
            raise AssertionError(f"Estatísticas de linhas inesperadas: {obtido!r}")
        if primeiro.resultados_analisados != 7 or segundo.resultados_analisados != 7:
            raise AssertionError("A quantidade de resultados analisados divergiu.")
        if len(segundo.padroes) != 9:
            raise AssertionError("O recálculo alterou a quantidade de padrões.")

    return {
        "resultados_analisados": segundo.resultados_analisados,
        "padroes": len(segundo.padroes),
        "estatisticas_linhas": obtido,
        "recalculo_idempotente": True,
    }


def main() -> None:
    """Executa a validação no database temporário recebido na linha de comando."""

    load_dotenv()
    if len(sys.argv) != 2:
        raise SystemExit("Uso: validar_persistencia_linhas.py DATABASE_TEMPORARIO")
    print(json.dumps(validar_persistencia_linhas(sys.argv[1]), ensure_ascii=False))


if __name__ == "__main__":
    main()
