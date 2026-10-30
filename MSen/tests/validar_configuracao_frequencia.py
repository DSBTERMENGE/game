"""Valida configuração de frequências em PostgreSQL efêmero."""

from dataclasses import replace
from decimal import Decimal
import os
from pathlib import Path

from dotenv import load_dotenv
import psycopg

from msen.config import carregar_configuracao_banco
from msen.database import (
    ErroRepositorioConfiguracaoFrequencia,
    RepositorioConfiguracaoFrequencia,
    executar_migracoes,
)
from msen.services import comparar_configuracoes_frequencia
from tests.suporte_banco_integracao import criar_vazio, conectar, remover


RAIZ = Path(__file__).resolve().parents[2]
MIGRACOES = RAIZ / "database" / "migrations"


def executar() -> None:
    load_dotenv(Path(__file__).resolve().parents[1] / ".env")
    configuracao_banco = carregar_configuracao_banco()
    nome = f"games_test_7_1_{os.getpid()}"
    criar_vazio(configuracao_banco, nome)
    try:
        config_teste = replace(configuracao_banco, nome=nome)
        primeira = executar_migracoes(config_teste, MIGRACOES)
        segunda = executar_migracoes(config_teste, MIGRACOES)
        if "018" not in primeira.aplicadas or segunda.aplicadas:
            raise AssertionError("A migração 018 não foi idempotente.")

        with conectar(configuracao_banco, nome) as conexao:
            repositorio = RepositorioConfiguracaoFrequencia(conexao)
            inicial = repositorio.buscar_ativa()
            calculada = replace(
                inicial.configuracao, nome="Experiência 600",
                tamanho_inicial=600, parametro_faixa=Decimal("1.500000"),
            )
            divergencias = comparar_configuracoes_frequencia(
                inicial.configuracao, calculada
            )
            if tuple(item.campo for item in divergencias) != (
                "nome", "tamanho_inicial", "parametro_faixa"
            ):
                raise AssertionError("Diferenças da configuração não foram detalhadas.")
            substituida = repositorio.substituir_ativa(calculada)
            if substituida.assinatura_sha256 != calculada.assinatura_sha256:
                raise AssertionError("Assinatura persistida divergiu da calculada.")
            conexao.commit()

            try:
                with conexao.transaction():
                    with conexao.cursor() as cursor:
                        cursor.execute(
                            "UPDATE configuracao_frequencia_dezenas "
                            "SET unidade_parametro='PERCENTUAL' WHERE id_configuracao=1"
                        )
            except psycopg.errors.CheckViolation:
                pass
            else:
                raise AssertionError("O banco aceitou unidade ambígua.")

            with conexao.cursor() as cursor:
                cursor.execute(
                    "UPDATE configuracao_frequencia_dezenas "
                    "SET assinatura_sha256=%s WHERE id_configuracao=1",
                    ("0" * 64,),
                )
            conexao.commit()
            try:
                repositorio.buscar_ativa()
            except ErroRepositorioConfiguracaoFrequencia as erro:
                if erro.codigo != "ASSINATURA_DIVERGENTE":
                    raise
            else:
                raise AssertionError("O repositório aceitou assinatura divergente.")

        print("Configuração 018 validada: semente, comparação, substituição, unidade e assinatura.")
    finally:
        remover(configuracao_banco, nome)


if __name__ == "__main__":
    executar()
