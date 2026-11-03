"""Valida preservação, conferência e nova origem das previsões futuras."""

from decimal import Decimal
import os

from dotenv import load_dotenv

from msen.config import carregar_configuracao_banco
from msen.services import (
    ConfiguracaoSelecaoDezenas,
    atualizar_previsoes_futuras,
    emitir_previsao_futura,
)
from tests.suporte_banco_integracao import conectar, criar, remover


COLUNAS = (
    "data_resultado,numero_ap,res_01,res_02,res_03,res_04,res_05,res_06,"
    "soma_res,media_aritmetica_res,mediana_res,desvio_padrao_media,"
    "media_coordenada_x,media_coordenada_y,versao_calculo"
)


def configuracao() -> ConfiguracaoSelecaoDezenas:
    return ConfiguracaoSelecaoDezenas(
        nome="Previsão horizonte 2",
        fator_k=Decimal("1.000000"), fator_j=Decimal("0.000000"),
        modo_quantidade="MAX", quantidade_dezenas=None,
        horizonte_concursos=2, versao_calculo=1,
    )


def executar() -> None:
    load_dotenv()
    banco = carregar_configuracao_banco()
    temporario = f"games_test_7_1_{os.getpid()}"
    with conectar(banco, banco.nome) as origem:
        with origem.cursor() as cursor:
            cursor.execute(
                f"SELECT {COLUNAS} FROM resultados WHERE numero_ap <= 506 ORDER BY numero_ap"
            )
            resultados = cursor.fetchall()
    assert len(resultados) == 506

    criar(banco, temporario)
    try:
        with conectar(banco, temporario) as conexao:
            with conexao.transaction():
                with conexao.cursor() as cursor:
                    cursor.executemany(
                        f"INSERT INTO resultados ({COLUNAS}) "
                        "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                        resultados[:505],
                    )
            primeira = emitir_previsao_futura(conexao, configuracao())
            assert primeira.concurso_corte == 505
            assert (primeira.concurso_alvo_inicial, primeira.concurso_alvo_final) == (506, 507)
            assert primeira.alvos_criados_agora == 2
            repetida = emitir_previsao_futura(conexao, configuracao())
            assert repetida.id_execucao_selecao == primeira.id_execucao_selecao
            assert repetida.alvos_criados_agora == 0
            assert repetida.alvos_ja_existentes == 2

            with conexao.cursor() as cursor:
                cursor.execute(
                    "SELECT ARRAY_AGG(d.dezena ORDER BY d.dezena) FILTER (WHERE d.retornada) "
                    "FROM alvos_pesquisa_selecao a JOIN avaliacoes_dezenas_pesquisa d "
                    "ON d.id_alvo_selecao=a.id_alvo_selecao "
                    "WHERE a.id_execucao_selecao=%s AND a.numero_concurso_alvo=506",
                    (primeira.id_execucao_selecao,),
                )
                dezenas_congeladas = cursor.fetchone()[0]

            with conexao.transaction():
                with conexao.cursor() as cursor:
                    cursor.execute(
                        f"INSERT INTO resultados ({COLUNAS}) "
                        "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                        resultados[505],
                    )
            atualizacao = atualizar_previsoes_futuras(conexao, configuracao())
            assert atualizacao.conferencia.previsoes_conferidas == 1
            assert atualizacao.nova_previsao.concurso_corte == 506
            assert (
                atualizacao.nova_previsao.concurso_alvo_inicial,
                atualizacao.nova_previsao.concurso_alvo_final,
            ) == (507, 508)

            with conexao.cursor() as cursor:
                cursor.execute(
                    "SELECT a.situacao,ARRAY_AGG(d.dezena ORDER BY d.dezena) "
                    "FILTER (WHERE d.retornada) FROM alvos_pesquisa_selecao a "
                    "JOIN avaliacoes_dezenas_pesquisa d "
                    "ON d.id_alvo_selecao=a.id_alvo_selecao "
                    "WHERE a.id_execucao_selecao=%s AND a.numero_concurso_alvo=506 "
                    "GROUP BY a.id_alvo_selecao",
                    (primeira.id_execucao_selecao,),
                )
                situacao, dezenas_depois = cursor.fetchone()
                assert situacao == "AVALIADO"
                assert dezenas_depois == dezenas_congeladas
                cursor.execute(
                    "SELECT COUNT(1) FROM alvos_pesquisa_selecao "
                    "WHERE numero_concurso_alvo=507"
                )
                assert cursor.fetchone()[0] == 2
        print("Previsão congelada, conferência e nova origem validadas.")
    finally:
        remover(banco, temporario)


if __name__ == "__main__":
    executar()
