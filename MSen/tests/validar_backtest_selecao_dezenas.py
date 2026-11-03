"""Ensaia execução, cancelamento, retomada e comparação em banco efêmero."""

from decimal import Decimal
import os

from dotenv import load_dotenv

from msen.config import carregar_configuracao_banco
from msen.services import (
    ConfiguracaoSelecaoDezenas,
    comparar_backtests,
    detalhar_backtest,
    executar_backtest_selecao,
)
from tests.suporte_banco_integracao import conectar, criar, remover


COLUNAS_RESULTADO = (
    "data_resultado,numero_ap,res_01,res_02,res_03,res_04,res_05,res_06,"
    "soma_res,media_aritmetica_res,mediana_res,desvio_padrao_media,"
    "media_coordenada_x,media_coordenada_y,versao_calculo"
)


def configuracao(nome: str, modo: str, quantidade: int | None):
    return ConfiguracaoSelecaoDezenas(
        nome=nome,
        fator_k=Decimal("1.000000"),
        fator_j=Decimal("0.000000"),
        modo_quantidade=modo,
        quantidade_dezenas=quantidade,
        horizonte_concursos=1,
        versao_calculo=1,
    )


def executar() -> None:
    load_dotenv()
    banco = carregar_configuracao_banco()
    nome_temporario = f"games_test_7_1_{os.getpid()}"
    with conectar(banco, banco.nome) as origem:
        with origem.cursor() as cursor:
            cursor.execute(
                f"SELECT {COLUNAS_RESULTADO} FROM resultados "
                "WHERE numero_ap <= 505 ORDER BY numero_ap"
            )
            resultados = cursor.fetchall()
    assert len(resultados) == 505

    criar(banco, nome_temporario)
    try:
        with conectar(banco, nome_temporario) as conexao:
            with conexao.transaction():
                with conexao.cursor() as cursor:
                    cursor.executemany(
                        f"INSERT INTO resultados ({COLUNAS_RESULTADO}) "
                        "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                        resultados,
                    )

            primeira = executar_backtest_selecao(
                conexao, configuracao("MAX", "MAX", None),
                concurso_inicial=500, concurso_final=505,
            )
            segunda = executar_backtest_selecao(
                conexao, configuracao("FIXA 10", "FIXA", 10),
                concurso_inicial=500, concurso_final=505,
            )
            assert primeira.estado == segunda.estado == "CONCLUIDA"
            assert primeira.resumo.avaliados == segunda.resumo.avaliados == 6
            assert sum(item.quantidade for item in primeira.resumo.classes) == 6

            chamadas = 0
            def cancelar_depois_de_dois() -> bool:
                nonlocal chamadas
                chamadas += 1
                return chamadas > 2

            cancelada = executar_backtest_selecao(
                conexao, configuracao("FIXA 8", "FIXA", 8),
                concurso_inicial=500, concurso_final=505,
                cancelamento_solicitado=cancelar_depois_de_dois,
            )
            assert cancelada.estado == "CANCELADA"
            assert cancelada.alvos_processados_agora == 2

            retomada = executar_backtest_selecao(
                conexao, configuracao("FIXA 8", "FIXA", 8),
                concurso_inicial=500, concurso_final=505,
            )
            assert retomada.estado == "CONCLUIDA"
            assert retomada.alvos_ja_existentes == 2
            assert retomada.alvos_processados_agora == 4

            comparacao = comparar_backtests(
                conexao,
                (primeira.id_execucao_selecao, segunda.id_execucao_selecao),
            )
            assert comparacao.comparavel
            assert len(comparacao.pesquisas) == 2
            assert comparacao.pesquisas[0].modo_quantidade == "MAX"
            detalhes = detalhar_backtest(conexao, primeira.id_execucao_selecao)
            assert len(detalhes) == 6
            assert detalhes[0].numero_concurso_alvo == 500
            assert detalhes[-1].numero_concurso_alvo == 505
            with conexao.cursor() as cursor:
                cursor.execute("SELECT COUNT(1) FROM avaliacoes_dezenas_pesquisa")
                assert cursor.fetchone()[0] == 18 * 60
        print("Backtest, cancelamento, retomada e comparação validados.")
    finally:
        remover(banco, nome_temporario)


if __name__ == "__main__":
    executar()
