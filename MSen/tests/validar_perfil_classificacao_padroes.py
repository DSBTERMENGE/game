"""Valida percentuais e raridade experimental em PostgreSQL temporário."""

from dataclasses import replace
from datetime import date
import json
import sys

from dotenv import load_dotenv

from msen.calculos import calcular_resultado
from msen.config import carregar_configuracao_banco
from msen.database import RepositorioResultados, executar_migracoes
from msen.modelos import ResultadoEntrada
from msen.services import (
    ErroRecalculoClassificacao,
    calcular_perfil_grupo_sequenciais,
    recalcular_classificacoes_grupo_sequenciais,
)
from suporte_banco_integracao import (
    MIGRACOES,
    _restaurar_backup,
    conectar,
    criar,
    criar_vazio,
    remover,
    validar_nome,
)


RESULTADOS_CONTROLADOS = (
    (1, (1, 3, 5, 7, 9, 11)),
    (2, (10, 25, 26, 38, 50, 58)),
    (3, (10, 25, 26, 27, 50, 58)),
    (4, (1, 2, 3, 4, 20, 40)),
)


def _serializar(perfil) -> dict[str, object]:
    """Converte o perfil imutável para a evidência JSON do ensaio."""
    return {
        "grupo": perfil.grupo_cod,
        "total_resultados": perfil.total_resultados,
        "total_classificados": perfil.total_classificados,
        "limite": str(perfil.limite_raridade_percentual),
        "operador": perfil.operador_raridade,
        "padroes_raros": list(perfil.padroes_raros),
        "classes": [
            {
                "codigo": item.padrao_cod or "SEM_CORRESPONDENCIA",
                "quantidade": item.quantidade,
                "percentual_total": str(item.percentual_total),
                "percentual_classificados": (
                    None
                    if item.percentual_classificados is None
                    else str(item.percentual_classificados)
                ),
                "raro": item.raro,
            }
            for item in perfil.classes
        ],
    }


def _inserir_controlados(conexao) -> None:
    """Inclui quatro resultados, um de cada classe do perfil."""
    repositorio = RepositorioResultados(conexao)
    for numero_ap, dezenas in RESULTADOS_CONTROLADOS:
        entrada = ResultadoEntrada.criar(
            data_resultado=date(2026, 10, 20 + numero_ap),
            numero_ap=numero_ap,
            resultados=dezenas,
        )
        repositorio.inserir(calcular_resultado(entrada))


def validar_controlado(nome_database: str) -> dict[str, object]:
    """Prova fechamento, operador estrito e sincronização do catálogo."""
    nome = validar_nome(nome_database)
    base = carregar_configuracao_banco()
    criar(base, nome)
    configuracao = replace(base, nome=nome)
    try:
        with conectar(configuracao, nome) as conexao:
            _inserir_controlados(conexao)
            try:
                calcular_perfil_grupo_sequenciais(
                    conexao, limite_raridade_percentual=25
                )
            except ErroRecalculoClassificacao as erro:
                if erro.codigo != "CLASSIFICACAO_INCOMPLETA":
                    raise AssertionError(f"Erro inesperado: {erro.codigo}") from erro
            else:
                raise AssertionError("O perfil aceitou classificações incompletas.")

            recalcular_classificacoes_grupo_sequenciais(conexao)
            no_limite = calcular_perfil_grupo_sequenciais(
                conexao, limite_raridade_percentual=25
            )
            acima = calcular_perfil_grupo_sequenciais(
                conexao, limite_raridade_percentual="25.000001"
            )
            if no_limite.padroes_raros:
                raise AssertionError("O operador incluiu padrões exatamente no limite.")
            if acima.padroes_raros != ("PD_001", "PD_002", "PD_003"):
                raise AssertionError("O operador estrito não selecionou os três padrões.")
            if sum(item.quantidade for item in no_limite.classes) != 4:
                raise AssertionError("As quatro classes não reconciliaram.")
            if no_limite.classes[-1].percentual_classificados is not None:
                raise AssertionError("SEM_CORRESPONDENCIA recebeu percentual classificado.")
            with conexao.cursor() as cursor:
                cursor.execute(
                    "SELECT padrao_cod, num_oco FROM padroes_subgrupo "
                    "WHERE padrao_cod IN ('PD_001', 'PD_002', 'PD_003') "
                    "ORDER BY padrao_cod"
                )
                if tuple(cursor.fetchall()) != (("PD_001", 1), ("PD_002", 1), ("PD_003", 1)):
                    raise AssertionError("O catálogo não foi sincronizado.")
            return {
                "perfil_no_limite": _serializar(no_limite),
                "raros_acima_do_limite": list(acima.padroes_raros),
                "classificacao_incompleta_rejeitada": True,
                "catalogo_sincronizado": True,
            }
    finally:
        remover(base, nome)


def validar_historico(nome_database: str) -> dict[str, object]:
    """Calcula o perfil de 10% sobre um clone do histórico real."""
    nome = validar_nome(nome_database)
    base = carregar_configuracao_banco()
    criar_vazio(base, nome)
    configuracao = replace(base, nome=nome)
    try:
        _restaurar_backup(base, nome)
        executar_migracoes(configuracao, MIGRACOES)
        with conectar(configuracao, nome) as conexao:
            recalcular_classificacoes_grupo_sequenciais(conexao)
            perfil = calcular_perfil_grupo_sequenciais(
                conexao, limite_raridade_percentual=10
            )
            if perfil.padroes_raros != ("PD_002", "PD_003"):
                raise AssertionError(f"Padrões raros inesperados: {perfil.padroes_raros}")
            if sum(item.quantidade for item in perfil.classes) != perfil.total_resultados:
                raise AssertionError("O perfil histórico não fechou no total.")
            return _serializar(perfil)
    finally:
        remover(base, nome)


def main() -> None:
    load_dotenv()
    if len(sys.argv) != 3 or sys.argv[1] not in {"controlado", "historico"}:
        raise SystemExit(
            "Uso: validar_perfil_classificacao_padroes.py "
            "controlado|historico NOME_TEMPORARIO"
        )
    funcao = validar_controlado if sys.argv[1] == "controlado" else validar_historico
    print(json.dumps(funcao(sys.argv[2]), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
