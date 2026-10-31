"""Valida prévia, confirmação, simulação, progresso e cancelamento."""

from dataclasses import replace
from datetime import date, timedelta
import os
from pathlib import Path

from dotenv import load_dotenv

from msen.calculos import calcular_resultado
from msen.config import carregar_configuracao_banco
from msen.database import RepositorioResultados, executar_migracoes
from msen.modelos import ResultadoEntrada
from msen.services import (
    ErroCargaHistoricoFrequencia,
    MENSAGEM_CONFIRMACAO,
    OperacaoFrequenciaCancelada,
    atualizar_historico_frequencia,
    configuracao_frequencia_inicial,
    preparar_operacao_historico_frequencia,
    simular_historico_frequencia,
)
from tests.suporte_banco_integracao import conectar, criar_vazio, remover


RAIZ = Path(__file__).resolve().parents[2]
MIGRACOES = RAIZ / "database" / "migrations"


def entrada(numero: int) -> ResultadoEntrada:
    return ResultadoEntrada.criar(
        data_resultado=date(2020, 1, 1) + timedelta(days=numero),
        numero_ap=numero,
        resultados=(10, 21, 32, 43, 54, 60),
    )


def inserir(conexao, numeros) -> None:
    repositorio = RepositorioResultados(conexao)
    for numero in numeros:
        repositorio.inserir(calcular_resultado(entrada(numero)))


def contar(conexao) -> tuple[int, int]:
    with conexao.cursor() as cursor:
        cursor.execute("SELECT count(*) FROM geracoes_frequencia_dezenas")
        geracoes = cursor.fetchone()[0]
        cursor.execute("SELECT count(*) FROM historico_frequencia_dezenas")
        linhas = cursor.fetchone()[0]
    conexao.commit()
    return geracoes, linhas


def executar() -> None:
    load_dotenv(Path(__file__).resolve().parents[1] / ".env")
    config_banco = carregar_configuracao_banco()
    nome = f"games_test_7_1_{os.getpid()}"
    criar_vazio(config_banco, nome)
    try:
        executar_migracoes(replace(config_banco, nome=nome), MIGRACOES)
        with conectar(config_banco, nome) as conexao:
            config = replace(
                configuracao_frequencia_inicial(), nome="Operação teste",
                tamanho_inicial=3,
            )
            inserir(conexao, range(1, 6))
            previa = preparar_operacao_historico_frequencia(conexao, config)
            if not previa.exige_confirmacao or previa.mensagem_confirmacao != MENSAGEM_CONFIRMACAO:
                raise AssertionError("Prévia gravável não exigiu confirmação.")
            if previa.modo != "PRIMEIRA_CARGA" or not previa.substitui_geracao:
                raise AssertionError("Prévia inicial incorreta.")
            if (previa.quantidade_concursos, previa.linhas_estimadas) != (3, 540):
                raise AssertionError("Estimativa da primeira carga divergiu.")
            previa_simulacao = preparar_operacao_historico_frequencia(
                conexao, config, salvar_dados=False
            )
            if previa_simulacao.exige_confirmacao:
                raise AssertionError("Simulação exigiu confirmação de gravação.")

            simulada = simular_historico_frequencia(conexao, config)
            if (simulada.fotografias_calculadas, simulada.linhas_calculadas) != (3, 540):
                raise AssertionError("Simulação inicial divergiu.")
            if contar(conexao) != (0, 0):
                raise AssertionError("Simulação gravou dados.")

            try:
                atualizar_historico_frequencia(conexao, config)
            except ErroCargaHistoricoFrequencia as erro:
                if erro.codigo != "CONFIRMACAO_OBRIGATORIA":
                    raise
            else:
                raise AssertionError("Gravação sem confirmação foi aceita.")

            progressos = []
            atualizar_historico_frequencia(
                conexao, config, confirmacao_gravacao=True,
                informar_progresso=lambda etapa, feito, total: progressos.append(
                    (etapa, feito, total)
                ),
            )
            if progressos[-1][1:] != (5, 5) or contar(conexao) != (1, 540):
                raise AssertionError("Progresso ou gravação confirmada divergiu.")

            inserir(conexao, (6, 7))
            incremental = preparar_operacao_historico_frequencia(conexao, config)
            if incremental.modo != "INCREMENTAL" or incremental.concursos_novos != (6, 7):
                raise AssertionError("Prévia incremental não listou os concursos 6 e 7.")
            if (incremental.quantidade_concursos, incremental.linhas_estimadas) != (2, 360):
                raise AssertionError("Estimativa incremental divergiu.")
            simulada_incremental = simular_historico_frequencia(conexao, config)
            if simulada_incremental.linhas_calculadas != 360 or contar(conexao) != (1, 540):
                raise AssertionError("Simulação incremental alterou a geração.")

            verificacoes_cancelamento = 0
            def cancelar_depois_do_primeiro_novo():
                nonlocal verificacoes_cancelamento
                verificacoes_cancelamento += 1
                return verificacoes_cancelamento >= 7
            try:
                atualizar_historico_frequencia(
                    conexao, config, confirmacao_gravacao=True,
                    cancelamento_solicitado=cancelar_depois_do_primeiro_novo,
                )
            except OperacaoFrequenciaCancelada:
                pass
            else:
                raise AssertionError("Cancelamento não interrompeu a gravação.")
            if contar(conexao) != (1, 540):
                raise AssertionError("Cancelamento deixou linhas parciais.")

            atualizar_historico_frequencia(
                conexao, config, confirmacao_gravacao=True
            )
            config_diferente = replace(config, tamanho_inicial=4)
            previa_diferente = preparar_operacao_historico_frequencia(
                conexao, config_diferente
            )
            if previa_diferente.modo != "RECONSTRUCAO_CONFIGURACAO":
                raise AssertionError("Mudança de configuração não indicou reconstrução.")
            if not any(
                item.campo == "tamanho_inicial"
                for item in previa_diferente.divergencias_configuracao
            ):
                raise AssertionError("Prévia não detalhou o campo divergente.")

        print("Operação 22.6 validada: prévia, confirmação, simulação, progresso e cancelamento.")
    finally:
        remover(config_banco, nome)


if __name__ == "__main__":
    executar()
