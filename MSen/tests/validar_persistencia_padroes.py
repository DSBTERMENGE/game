"""Valida cadastro e recálculo de padrões em database temporário protegido."""

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
    (10, (10, 25, 26, 38, 50, 58)),
    (20, (1, 3, 5, 7, 9, 11)),
    (25, (1, 10, 20, 40, 41, 60)),
    (40, (10, 25, 26, 27, 50, 58)),
    (60, (10, 25, 26, 27, 28, 58)),
    (80, (25, 26, 27, 28, 29, 30)),
)


def validar_persistencia(nome_database: str) -> dict[str, object]:
    """Executa duas vezes o recálculo e confirma dados e textos preservados."""

    nome = validar_nome(nome_database)
    configuracao = replace(carregar_configuracao_banco(), nome=nome)
    with conectar(configuracao, nome) as conexao:
        resultados = RepositorioResultados(conexao)
        for numero_ap, dezenas in RESULTADOS_CONTROLADOS:
            entrada = ResultadoEntrada.criar(
                data_resultado=date(2020, 1, 1) + timedelta(days=numero_ap),
                numero_ap=numero_ap,
                resultados=dezenas,
            )
            resultados.inserir(calcular_resultado(entrada))

        primeiro = recalcular_padroes_iniciais(conexao)
        obtido = {
            item.padrao_cod: (
                item.num_oco,
                str(item.intervalo_medio),
                str(item.desv_padrao),
            )
            for item in primeiro.padroes
        }
        esperado = {
            "PD_001": (2, "15.000000", "0.000000"),
            "PD_002": (1, "None", "None"),
            "PD_003": (2, "20.000000", "0.000000"),
        }
        if obtido != esperado:
            raise AssertionError(f"Estatísticas inesperadas: {obtido!r}")

        with conexao.transaction():
            with conexao.cursor() as cursor:
                cursor.execute(
                    "UPDATE padroes SET padrao_nome = %s WHERE padrao_cod = %s",
                    ("Nome editado pelo usuário", "PD_001"),
                )

        segundo = recalcular_padroes_iniciais(conexao)
        cadastrados = RepositorioPadroes(conexao).listar()
        if len(cadastrados) != 3:
            raise AssertionError("O recálculo duplicou o cadastro de padrões.")
        if cadastrados[0].padrao_nome != "Nome editado pelo usuário":
            raise AssertionError("O recálculo sobrescreveu o texto editável.")
        if primeiro.resultados_analisados != 6 or segundo.resultados_analisados != 6:
            raise AssertionError("A quantidade de resultados analisados divergiu.")

        repositorio_padroes = RepositorioPadroes(conexao)
        criado = repositorio_padroes.criar("Padrão futuro", "Detector pendente")
        if criado.padrao_cod != "PD_004":
            raise AssertionError(f"Código automático inesperado: {criado.padrao_cod}")
        editado = repositorio_padroes.atualizar_textos(
            criado.padrao_cod, "Padrão futuro revisto", "Descrição revista"
        )
        if editado.padrao_nome != "Padrão futuro revisto":
            raise AssertionError("A edição dos textos não foi persistida.")
        repositorio_padroes.excluir(criado.padrao_cod)
        seguinte = repositorio_padroes.criar(
            "Outro padrão futuro", "O código anterior não pode ser reutilizado"
        )
        if seguinte.padrao_cod != "PD_005":
            raise AssertionError("O código excluído foi reutilizado.")

        repositorio_padroes.excluir("PD_003")
        recalcular_padroes_iniciais(conexao)
        finais = repositorio_padroes.listar()
        codigos_finais = tuple(item.padrao_cod for item in finais)
        if codigos_finais != ("PD_001", "PD_002", "PD_005"):
            raise AssertionError(f"A exclusão não foi respeitada: {codigos_finais!r}")
        if finais[-1].num_oco is not None:
            raise AssertionError("Padrão sem detector recebeu estatística.")

    return {
        "resultados_analisados": segundo.resultados_analisados,
        "padroes": len(cadastrados),
        "estatisticas": obtido,
        "texto_editado_preservado": True,
        "recalculo_idempotente": True,
        "crud": True,
        "codigos_nao_reutilizados": True,
        "exclusao_respeitada": True,
    }


def main() -> None:
    """Executa a validação no database temporário indicado na linha de comando."""

    load_dotenv()
    if len(sys.argv) != 2:
        raise SystemExit("Uso: validar_persistencia_padroes.py NOME_DATABASE_TEMPORARIO")
    print(json.dumps(validar_persistencia(sys.argv[1]), ensure_ascii=False))


if __name__ == "__main__":
    main()
