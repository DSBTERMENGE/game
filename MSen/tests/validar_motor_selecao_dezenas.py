"""Valida o motor 23.5 contra cortes reais sem gravar pesquisas."""

from dotenv import load_dotenv

from msen.config import carregar_configuracao_banco
from msen.database import RepositorioFonteSelecaoDezenas, abrir_conexao
from msen.services import configuracao_selecao_inicial, selecionar_dezenas_para_alvo


def executar() -> None:
    load_dotenv()
    with abrir_conexao(carregar_configuracao_banco()) as conexao:
        fonte = RepositorioFonteSelecaoDezenas(conexao)
        corte_499 = fonte.carregar_estatisticas_corte(499)
        assert len(corte_499) == 60
        assert all(
            item.ultima_ocorrencia is None or item.ultima_ocorrencia <= 499
            for item in corte_499
        )
        selecao_500 = selecionar_dezenas_para_alvo(
            corte_499,
            configuracao_selecao_inicial(),
            numero_concurso_alvo=500,
            numero_concurso_corte=499,
        )
        assert len(selecao_500.avaliacoes) == 60
        assert all(item.dezena in range(1, 61) for item in selecao_500.avaliacoes)

        with conexao.cursor() as cursor:
            cursor.execute("SELECT MAX(numero_ap) FROM resultados")
            ultimo = cursor.fetchone()[0]
        corte_atual = fonte.carregar_estatisticas_corte(ultimo)
        previsao = selecionar_dezenas_para_alvo(
            corte_atual,
            configuracao_selecao_inicial(),
            numero_concurso_alvo=ultimo + 1,
            numero_concurso_corte=ultimo,
        )
        assert len(previsao.avaliacoes) == 60
        print(
            f"Alvo 500: {len(selecao_500.dezenas_retornadas)} dezenas; "
            f"alvo {ultimo + 1}: {len(previsao.dezenas_retornadas)} dezenas."
        )


if __name__ == "__main__":
    executar()
