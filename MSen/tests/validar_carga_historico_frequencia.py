"""Valida carga, acréscimo, troca e recuperação em PostgreSQL efêmero."""

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
    atualizar_historico_frequencia,
    configuracao_frequencia_inicial,
)
from tests.suporte_banco_integracao import conectar, criar_vazio, remover


RAIZ = Path(__file__).resolve().parents[2]
MIGRACOES = RAIZ / "database" / "migrations"


def entrada(numero: int) -> ResultadoEntrada:
    inclui_10 = numero in {1, 2, 3, 5, 6, 7, 8}
    dezenas = (10, 21, 32, 43, 54, 60) if inclui_10 else (9, 21, 32, 43, 54, 60)
    return ResultadoEntrada.criar(
        data_resultado=date(2020, 1, 1) + timedelta(days=numero),
        numero_ap=numero,
        resultados=dezenas,
    )


def inserir(conexao, numeros) -> None:
    repositorio = RepositorioResultados(conexao)
    for numero in numeros:
        repositorio.inserir(calcular_resultado(entrada(numero)))


def estado(conexao):
    with conexao.cursor() as cursor:
        cursor.execute(
            "SELECT id_geracao, concurso_final, quantidade_fotografias "
            "FROM geracoes_frequencia_dezenas WHERE estado='ATIVA'"
        )
        geracao = cursor.fetchone()
        cursor.execute("SELECT count(*) FROM historico_frequencia_dezenas")
        linhas = cursor.fetchone()[0]
    conexao.commit()
    return geracao, linhas


def executar() -> None:
    load_dotenv(Path(__file__).resolve().parents[1] / ".env")
    configuracao_banco = carregar_configuracao_banco()
    nome = f"games_test_7_1_{os.getpid()}"
    criar_vazio(configuracao_banco, nome)
    try:
        config_teste = replace(configuracao_banco, nome=nome)
        executar_migracoes(config_teste, MIGRACOES)
        with conectar(configuracao_banco, nome) as conexao:
            config_3 = replace(
                configuracao_frequencia_inicial(), nome="Teste 3", tamanho_inicial=3
            )
            inserir(conexao, range(1, 6))
            primeira = atualizar_historico_frequencia(
                conexao, config_3, confirmacao_gravacao=True
            )
            if (primeira.modo, primeira.fotografias_adicionadas,
                    primeira.linhas_adicionadas) != ("CARGA_COMPLETA", 3, 540):
                raise AssertionError("Primeira carga divergiu.")
            geracao_inicial, linhas_iniciais = estado(conexao)

            repetida = atualizar_historico_frequencia(
                conexao, config_3, confirmacao_gravacao=True
            )
            if repetida.modo != "SEM_ALTERACAO" or estado(conexao)[1] != 540:
                raise AssertionError("Repetição não foi idempotente.")

            inserir(conexao, (6, 7))
            incremental = atualizar_historico_frequencia(
                conexao, config_3, confirmacao_gravacao=True
            )
            if (incremental.modo, incremental.fotografias_adicionadas,
                    incremental.linhas_adicionadas) != ("INCREMENTAL", 2, 360):
                raise AssertionError("Acréscimo incremental divergiu.")
            geracao_incremental, linhas_incrementais = estado(conexao)
            if geracao_incremental[0] != geracao_inicial[0] or linhas_incrementais != 900:
                raise AssertionError("Incremental substituiu a geração ou refez linhas.")

            config_4 = replace(config_3, nome="Teste 4", tamanho_inicial=4)
            antes_falha = estado(conexao)
            try:
                atualizar_historico_frequencia(
                    conexao, config_4, confirmacao_gravacao=True,
                    _falhar_apos_lotes=1,
                )
            except ErroCargaHistoricoFrequencia as erro:
                if erro.codigo != "FALHA_SIMULADA":
                    raise
            else:
                raise AssertionError("A falha controlada não ocorreu.")
            if estado(conexao) != antes_falha:
                raise AssertionError("Falha alterou a geração ativa.")

            troca = atualizar_historico_frequencia(
                conexao, config_4, confirmacao_gravacao=True
            )
            geracao_trocada, linhas_trocadas = estado(conexao)
            if troca.modo != "CARGA_COMPLETA" or linhas_trocadas != 720:
                raise AssertionError("Troca de configuração divergiu.")
            if geracao_trocada[0] == geracao_incremental[0]:
                raise AssertionError("Troca não criou nova geração.")

            with conexao.cursor() as cursor:
                cursor.execute(
                    "UPDATE resultados SET res_01=8 WHERE numero_ap=2"
                )
            conexao.commit()
            try:
                atualizar_historico_frequencia(
                    conexao, config_4, confirmacao_gravacao=True
                )
            except ErroCargaHistoricoFrequencia as erro:
                if erro.codigo != "RECONSTRUCAO_NECESSARIA":
                    raise
            else:
                raise AssertionError("Alteração antiga não exigiu reconstrução.")
            if estado(conexao) != (geracao_trocada, linhas_trocadas):
                raise AssertionError("Detecção de alteração modificou a geração ativa.")

            reconstruida = atualizar_historico_frequencia(
                conexao, config_4, reconstruir_origem_alterada=True,
                confirmacao_gravacao=True,
            )
            if reconstruida.modo != "CARGA_COMPLETA":
                raise AssertionError("Reconstrução autorizada não foi integral.")

            with conexao.cursor() as cursor:
                cursor.execute(
                    "SELECT count(*) FROM geracoes_frequencia_dezenas"
                )
                if cursor.fetchone()[0] != 1:
                    raise AssertionError("Gerações antigas detalhadas foram conservadas.")

            inserir(conexao, (8,))
            antes_incremental_falho = estado(conexao)
            try:
                atualizar_historico_frequencia(
                    conexao, config_4, confirmacao_gravacao=True,
                    _falhar_apos_lotes=1,
                )
            except ErroCargaHistoricoFrequencia as erro:
                if erro.codigo != "FALHA_SIMULADA":
                    raise
            else:
                raise AssertionError("Falha incremental controlada não ocorreu.")
            if estado(conexao) != antes_incremental_falho:
                raise AssertionError("Falha incremental deixou linhas parciais.")
            atualizar_historico_frequencia(
                conexao, config_4, confirmacao_gravacao=True
            )

            with conexao.cursor() as cursor:
                cursor.execute("DELETE FROM resultados WHERE numero_ap=4")
            conexao.commit()
            antes_lacuna = estado(conexao)
            try:
                atualizar_historico_frequencia(
                    conexao, config_4, confirmacao_gravacao=True
                )
            except ErroCargaHistoricoFrequencia as erro:
                if erro.codigo != "LACUNA_HISTORICA":
                    raise
            else:
                raise AssertionError("Lacuna da origem não foi detectada.")
            if estado(conexao) != antes_lacuna:
                raise AssertionError("Detecção de lacuna alterou a geração ativa.")

            print(
                "Carga histórica validada: completa %.4fs, incremental %.4fs, troca %.4fs."
                % (primeira.duracao_segundos, incremental.duracao_segundos,
                   troca.duracao_segundos)
            )
    finally:
        remover(configuracao_banco, nome)


if __name__ == "__main__":
    executar()
