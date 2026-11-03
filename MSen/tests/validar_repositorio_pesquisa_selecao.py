"""Valida a migração 021 e o repositório em PostgreSQL efêmero."""

from decimal import Decimal
import os

from dotenv import load_dotenv

from msen.config import carregar_configuracao_banco
from msen.database import (
    AlvoPesquisaEntrada,
    AvaliacaoDezenaPesquisaEntrada,
    RepositorioPesquisaSelecao,
)
from msen.services import configuracao_selecao_inicial
from tests.suporte_banco_integracao import conectar, criar, remover


def avaliacao_sem_base(dezena: int) -> AvaliacaoDezenaPesquisaEntrada:
    return AvaliacaoDezenaPesquisaEntrada(
        dezena=dezena, estado_avaliacao="SEM_BASE",
        ultima_ocorrencia=None, quantidade_intervalos=0,
        media_intervalos=None, desvio_padrao=None,
        centro_original=None, centro_ajustado=None,
        limite_inferior_exato=None, limite_superior_exato=None,
        limite_inferior=None, limite_superior=None,
        distancia_normalizada=None, distancia_absoluta=None,
        posicao_ranking=None, aprovada=False, retornada=False,
    )


def executar() -> None:
    load_dotenv()
    configuracao_banco = carregar_configuracao_banco()
    nome_banco = f"games_test_7_1_{os.getpid()}"
    criar(configuracao_banco, nome_banco)
    try:
        with conectar(configuracao_banco, nome_banco) as conexao:
            repositorio = RepositorioPesquisaSelecao(conexao)
            configuracao = repositorio.criar_ou_buscar_configuracao(
                configuracao_selecao_inicial()
            )
            repetida = repositorio.criar_ou_buscar_configuracao(
                configuracao_selecao_inicial()
            )
            assert repetida.id_configuracao_selecao == configuracao.id_configuracao_selecao

            execucao = repositorio.criar_ou_buscar_execucao(
                configuracao,
                tipo_execucao="BACKTEST",
                assinatura_resultados="a" * 64,
                concurso_corte_origem=3069,
                concurso_alvo_inicial=500,
                concurso_alvo_final=500,
            )
            avaliacoes = tuple(avaliacao_sem_base(i) for i in range(1, 61))
            alvo = AlvoPesquisaEntrada(
                numero_concurso_alvo=500,
                numero_concurso_corte=499,
                id_resultado=None,
                situacao="PENDENTE",
                quantidade_configurada=None,
                quantidade_acertos=None,
                motivo=None,
            )
            salvo = repositorio.salvar_alvo(
                execucao.id_execucao_selecao, alvo, avaliacoes
            )
            repetido = repositorio.salvar_alvo(
                execucao.id_execucao_selecao, alvo, avaliacoes
            )
            assert salvo.criado is True
            assert repetido.criado is False
            with conexao.cursor() as cursor:
                cursor.execute("SELECT count(*) FROM avaliacoes_dezenas_pesquisa")
                assert cursor.fetchone()[0] == 60
                cursor.execute("SELECT alvos_concluidos FROM execucoes_pesquisa_selecao")
                assert cursor.fetchone()[0] == 1
        print("Migração 021 e repositório validados em PostgreSQL efêmero.")
    finally:
        remover(configuracao_banco, nome_banco)


if __name__ == "__main__":
    executar()
