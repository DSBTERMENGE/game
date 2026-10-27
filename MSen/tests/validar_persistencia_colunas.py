"""Valida a persistência dos padrões de mesma coluna em database temporário."""

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
    (10, (10, 25, 35, 48, 51, 59)),
    (20, (1, 12, 23, 34, 45, 56)),
    (25, (5, 15, 22, 32, 48, 59)),
    (40, (7, 17, 27, 34, 45, 56)),
    (50, (5, 15, 25, 32, 42, 59)),
    (60, (5, 15, 25, 35, 48, 59)),
    (80, (10, 20, 30, 40, 50, 60)),
)


def validar_persistencia_colunas(nome_database: str) -> dict[str, object]:
    """Cadastra os padrões, recalcula duas vezes e confere sua persistência.

    Parâmetros:
        nome_database: Nome previamente criado dentro do padrão seguro de teste.

    Retorno:
        Resumo serializável das estatísticas e verificações executadas.

    Regra:
        O database deve ser temporário. A função não cria, remove nem acessa o
        database local de desenvolvimento `games`.
    """

    nome = validar_nome(nome_database)
    configuracao = replace(carregar_configuracao_banco(), nome=nome)
    with conectar(configuracao, nome) as conexao:
        padroes = RepositorioPadroes(conexao)
        for nome_padrao, descricao in (
            ("Duas dezenas na mesma coluna", "Sequência vertical de duas linhas."),
            ("Três dezenas na mesma coluna", "Sequência vertical de três linhas."),
            ("Mais de três dezenas na mesma coluna", "Sequência vertical superior a três linhas."),
        ):
            padroes.criar(nome_padrao, descricao, "PG_002")

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
            if item.padrao_cod in {"PD_004", "PD_005", "PD_006"}
        }
        esperado = {
            "PD_004": (2, "15.000000", "0.000000"),
            "PD_005": (2, "10.000000", "0.000000"),
            "PD_006": (2, "20.000000", "0.000000"),
        }
        if obtido != esperado:
            raise AssertionError(f"Estatísticas de colunas inesperadas: {obtido!r}")
        if primeiro.resultados_analisados != 7 or segundo.resultados_analisados != 7:
            raise AssertionError("A quantidade de resultados analisados divergiu.")
        if len(segundo.padroes) != 6:
            raise AssertionError("O recálculo alterou a quantidade de padrões.")

    return {
        "resultados_analisados": segundo.resultados_analisados,
        "padroes": len(segundo.padroes),
        "estatisticas_colunas": obtido,
        "recalculo_idempotente": True,
    }


def main() -> None:
    """Executa a validação no database temporário recebido na linha de comando."""

    load_dotenv()
    if len(sys.argv) != 2:
        raise SystemExit("Uso: validar_persistencia_colunas.py DATABASE_TEMPORARIO")
    print(json.dumps(validar_persistencia_colunas(sys.argv[1]), ensure_ascii=False))


if __name__ == "__main__":
    main()
