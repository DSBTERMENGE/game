"""Valida os fluxos geométricos integrados em PostgreSQL temporário."""

from dataclasses import replace
from datetime import date
from decimal import Decimal
import json
from pathlib import Path
import sys
import tempfile

from dotenv import load_dotenv
from openpyxl import Workbook

from msen.config import carregar_configuracao_banco
from msen.database import RepositorioAnaliseGeometrica, RepositorioResultados
from msen.modelos import ResultadoEntrada
from msen.services import (
    editar_resultado,
    importar_planilha_no_banco,
    incluir_resultado,
    recalcular_analises_geometricas,
)
from suporte_banco_integracao import conectar, validar_nome


def _entrada(numero_ap: int, dezenas: tuple[int, ...]) -> ResultadoEntrada:
    return ResultadoEntrada.criar(
        data_resultado=date(2026, 10, numero_ap),
        numero_ap=numero_ap,
        resultados=dezenas,
    )


def _criar_planilha(caminho: Path) -> None:
    pasta = Workbook()
    folha = pasta.active
    for _ in range(6):
        folha.append(["Resultados"])
    folha.append(
        ["Concurso", "Data", "bola 1", "bola 2", "bola 3", "bola 4", "bola 5", "bola 6"]
    )
    folha.append([1, date(2026, 10, 1), 1, 20, 30, 40, 50, 51])
    folha.append([2, date(2026, 10, 2), 1, 2, 3, 10, 11, 20])
    pasta.save(caminho)
    pasta.close()


def validar_servico_geometrico(nome_database: str) -> dict[str, object]:
    """Exercita inclusão, importação, edição e recálculo geométricos.

    Args:
        nome_database: Database temporário previamente criado e migrado.

    Returns:
        Resumo serializável dos fluxos e medidas conferidos.
    """

    nome = validar_nome(nome_database)
    configuracao = replace(carregar_configuracao_banco(), nome=nome)
    with conectar(configuracao, nome) as conexao:
        incluido = incluir_resultado(conexao, _entrada(1, (1, 20, 30, 40, 50, 51)))
        repositorio_analises = RepositorioAnaliseGeometrica(conexao)
        analise_inclusao = repositorio_analises.buscar(incluido.id_resultado)
        if analise_inclusao is None or analise_inclusao.area_total != Decimal("36.000000000000"):
            raise AssertionError("A inclusão não persistiu a análise geométrica esperada.")

        with tempfile.TemporaryDirectory() as temporario:
            caminho = Path(temporario) / "resultados.xlsx"
            _criar_planilha(caminho)
            relatorio_importacao = importar_planilha_no_banco(conexao, caminho)
        if relatorio_importacao.inseridas != 1 or relatorio_importacao.iguais != 1:
            raise AssertionError("A importação incremental divergiu do esperado.")

        resultados = RepositorioResultados(conexao)
        importado = resultados.buscar_por_numero_ap(2)
        if importado is None:
            raise AssertionError("O resultado importado não foi encontrado.")
        analise_importacao = repositorio_analises.buscar(importado.id_resultado)
        if analise_importacao is None or analise_importacao.area_total != Decimal("4.500000000000"):
            raise AssertionError("A importação não calculou a figura cruzada.")

        editado = editar_resultado(conexao, _entrada(1, (1, 2, 3, 4, 5, 6)))
        analise_edicao = repositorio_analises.buscar(editado.id_resultado)
        if analise_edicao is None or analise_edicao.area_total != 0:
            raise AssertionError("A edição não substituiu a análise geométrica.")
        if analise_edicao.centro_gravidade_x is not None:
            raise AssertionError("A edição colinear deveria produzir centro nulo.")

        primeiro = recalcular_analises_geometricas(conexao)
        segundo = recalcular_analises_geometricas(conexao)
        if primeiro.analises != segundo.analises or segundo.resultados_analisados != 2:
            raise AssertionError("O recálculo histórico não foi idempotente.")
        with conexao.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM resultados")
            total_resultados = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM analise_geometrica_resultado")
            total_analises = cursor.fetchone()[0]
        if (total_resultados, total_analises) != (2, 2):
            raise AssertionError("Resultados e análises perderam a relação um para um.")

    return {
        "inclusao_area": str(analise_inclusao.area_total),
        "importacao_area": str(analise_importacao.area_total),
        "edicao_area": str(analise_edicao.area_total),
        "importacao_inseridas": relatorio_importacao.inseridas,
        "recalculo_resultados": segundo.resultados_analisados,
        "relacao_um_para_um": True,
        "recalculo_idempotente": True,
    }


def main() -> None:
    """Executa a validação no database temporário informado."""

    load_dotenv()
    if len(sys.argv) != 2:
        raise SystemExit("Uso: validar_servico_geometrico.py DATABASE_TEMPORARIO")
    print(json.dumps(validar_servico_geometrico(sys.argv[1]), ensure_ascii=False))


if __name__ == "__main__":
    main()
