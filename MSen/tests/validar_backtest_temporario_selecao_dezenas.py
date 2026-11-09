"""Valida o motor temporário completo contra o banco real sem gravar dados."""

from __future__ import annotations

import json

from dotenv import load_dotenv

from msen.config import carregar_configuracao_banco
from msen.database import abrir_conexao
from msen.services import ErroBacktestTemporario, executar_backtest_temporario


def _cardinalidades(conexao) -> tuple[int, int, int, int, int]:
    with conexao.transaction():
        with conexao.cursor() as cursor:
            cursor.execute(
                "SELECT "
                "(SELECT COUNT(*) FROM configuracoes_pesquisa_selecao),"
                "(SELECT COUNT(*) FROM resultados),"
                "(SELECT COUNT(*) FROM execucoes_pesquisa_selecao),"
                "(SELECT COUNT(*) FROM alvos_pesquisa_selecao),"
                "(SELECT COUNT(*) FROM avaliacoes_dezenas_pesquisa)"
            )
            return cursor.fetchone()


def main() -> None:
    load_dotenv()
    with abrir_conexao(carregar_configuracao_banco()) as conexao:
        with conexao.transaction():
            with conexao.cursor() as cursor:
                cursor.execute(
                    "SELECT id_configuracao_selecao "
                    "FROM configuracoes_pesquisa_selecao "
                    "WHERE estado='DISPONIVEL' "
                    "ORDER BY id_configuracao_selecao LIMIT 1"
                )
                linha = cursor.fetchone()
        if linha is None:
            raise RuntimeError("É necessária uma configuração salva e disponível.")

        antes = _cardinalidades(conexao)
        progresso: list[tuple[int, int]] = []
        relatorio = executar_backtest_temporario(
            conexao,
            linha[0],
            concurso_inicial=500,
            concurso_final=3069,
            informar_progresso=lambda atual, total: progresso.append((atual, total)),
        )
        depois = _cardinalidades(conexao)

        try:
            executar_backtest_temporario(
                conexao,
                linha[0],
                concurso_inicial=500,
                concurso_final=510,
                cancelamento_solicitado=lambda: True,
            )
        except ErroBacktestTemporario as erro:
            assert erro.codigo == "BACKTEST_CANCELADO"
        else:
            raise AssertionError("O cancelamento solicitado não foi respeitado.")
        depois_cancelamento = _cardinalidades(conexao)

    assert antes == depois
    assert antes == depois_cancelamento
    assert len(relatorio.pontos) == 2570
    assert relatorio.pontos[0].concurso == 500
    assert relatorio.pontos[-1].concurso == 3069
    assert relatorio.resumo.testes_efetuados == 2570
    assert sum(item.quantidade for item in relatorio.resumo.classes) == 2570
    assert progresso[0] == (1, 2570)
    assert progresso[-1] == (2570, 2570)

    print(json.dumps({
        "configuracao": relatorio.id_configuracao_selecao,
        "periodo": [relatorio.concurso_inicial, relatorio.concurso_final],
        "pontos": len(relatorio.pontos),
        "minimo_dezenas": relatorio.resumo.minimo_dezenas,
        "maximo_dezenas": relatorio.resumo.maximo_dezenas,
        "media_dezenas": str(relatorio.resumo.media_dezenas),
        "media_acertos": str(relatorio.resumo.media_acertos),
        "classes": {
            str(item.classe): item.quantidade for item in relatorio.resumo.classes
        },
        "premiados": relatorio.resumo.concursos_premiados,
        "duracao_segundos": str(relatorio.duracao_segundos),
        "cardinalidades_inalteradas": antes == depois,
        "cancelamento_sem_gravacao": antes == depois_cancelamento,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
