"""Valida autorização e persistência dos jogos em database efêmero."""

from decimal import Decimal
import os

from dotenv import load_dotenv

from msen.config import carregar_configuracao_banco
from msen.services import (
    ConfiguracaoSelecaoDezenas,
    ErroCombinacoesSelecao,
    emitir_previsao_futura,
    persistir_combinacoes_alvo,
)
from tests.suporte_banco_integracao import conectar, criar, remover


COLUNAS = (
    "data_resultado,numero_ap,res_01,res_02,res_03,res_04,res_05,res_06,"
    "soma_res,media_aritmetica_res,mediana_res,desvio_padrao_media,"
    "media_coordenada_x,media_coordenada_y,versao_calculo"
)


def executar() -> None:
    load_dotenv()
    banco = carregar_configuracao_banco()
    temporario = f"games_test_7_1_{os.getpid()}"
    with conectar(banco, banco.nome) as origem:
        with origem.cursor() as cursor:
            cursor.execute(
                f"SELECT {COLUNAS} FROM resultados "
                "WHERE numero_ap <= 505 ORDER BY numero_ap"
            )
            resultados = cursor.fetchall()
    assert len(resultados) == 505

    criar(banco, temporario)
    try:
        with conectar(banco, temporario) as conexao:
            with conexao.transaction():
                with conexao.cursor() as cursor:
                    cursor.executemany(
                        f"INSERT INTO resultados ({COLUNAS}) "
                        "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                        resultados,
                    )
            configuracao = ConfiguracaoSelecaoDezenas(
                nome="Integração de sete dezenas",
                fator_k=Decimal("1.000000"),
                fator_j=Decimal("0.000000"),
                modo_quantidade="FIXA",
                quantidade_dezenas=7,
                versao_calculo=1,
            )
            previsao = emitir_previsao_futura(conexao, configuracao)
            with conexao.cursor() as cursor:
                cursor.execute(
                    "SELECT id_alvo_selecao FROM alvos_pesquisa_selecao "
                    "WHERE id_execucao_selecao=%s",
                    (previsao.id_execucao_selecao,),
                )
                id_alvo = cursor.fetchone()[0]

            try:
                persistir_combinacoes_alvo(conexao, id_alvo)
                raise AssertionError("A persistência não autorizada deveria falhar.")
            except ErroCombinacoesSelecao as erro:
                assert erro.codigo == "OPERACAO_NAO_AUTORIZADA"
            with conexao.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM lotes_jogos_selecao")
                assert cursor.fetchone()[0] == 0

            relatorio = persistir_combinacoes_alvo(
                conexao, id_alvo, autorizar_persistencia=True
            )
            assert relatorio.quantidade_combinacoes == 7
            with conexao.cursor() as cursor:
                cursor.execute(
                    "SELECT l.estado,l.quantidade_dezenas,l.quantidade_combinacoes,"
                    "COUNT(j.ordem),COUNT(DISTINCT ROW(j.dezena_1,j.dezena_2,j.dezena_3,"
                    "j.dezena_4,j.dezena_5,j.dezena_6)),MIN(j.ordem),MAX(j.ordem) "
                    "FROM lotes_jogos_selecao l JOIN jogos_selecao_dezenas j "
                    "ON j.id_lote_jogos=l.id_lote_jogos "
                    "WHERE l.id_lote_jogos=%s GROUP BY l.id_lote_jogos",
                    (relatorio.id_lote_jogos,),
                )
                estado, quantidade_dezenas, total, linhas, distintas, minimo, maximo = cursor.fetchone()
            assert (estado, quantidade_dezenas, total) == ("CONCLUIDO", 7, 7)
            assert (linhas, distintas, minimo, maximo) == (7, 7, 1, 7)
        print("Autorização, vínculo e sete jogos distintos validados.")
    finally:
        remover(banco, temporario)


if __name__ == "__main__":
    executar()
