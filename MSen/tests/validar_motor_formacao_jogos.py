"""Executa o motor com a seleção real sem gravar combinações."""

from dotenv import load_dotenv

from msen.config import carregar_configuracao_banco
from msen.database import abrir_conexao
from msen.services import executar_geracao_controlada


load_dotenv()
with abrir_conexao(carregar_configuracao_banco()) as conexao, conexao.cursor() as cursor:
    cursor.execute(
        "SELECT a.id_alvo_selecao, ARRAY_AGG(v.dezena ORDER BY v.posicao_ranking) "
        "FROM alvos_pesquisa_selecao a "
        "JOIN avaliacoes_dezenas_pesquisa v ON v.id_alvo_selecao=a.id_alvo_selecao "
        "WHERE v.retornada "
        "GROUP BY a.id_alvo_selecao ORDER BY a.id_alvo_selecao DESC LIMIT 1"
    )
    id_alvo, dezenas = cursor.fetchone()
    cursor.execute("SELECT COUNT(*) FROM formacoes_jogos_selecao")
    formacoes_antes = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM jogos_finais_selecao")
    jogos_antes = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM lotes_jogos_selecao")
    lotes_antes = cursor.fetchone()[0]

progressos = []
relatorio = executar_geracao_controlada(
    dezenas,
    lambda _combinacao: None,
    informar_progresso=lambda atual, total: progressos.append((atual, total)),
    intervalo_progresso=1_000,
)

with abrir_conexao(carregar_configuracao_banco()) as conexao, conexao.cursor() as cursor:
    cursor.execute("SELECT COUNT(*) FROM formacoes_jogos_selecao")
    assert cursor.fetchone()[0] == formacoes_antes
    cursor.execute("SELECT COUNT(*) FROM jogos_finais_selecao")
    assert cursor.fetchone()[0] == jogos_antes
    cursor.execute("SELECT COUNT(*) FROM lotes_jogos_selecao")
    assert cursor.fetchone()[0] == lotes_antes

assert relatorio.estado == "CONCLUIDA"
assert relatorio.quantidade_dezenas == 16
assert relatorio.quantidade_combinacoes == 8_008
assert relatorio.quantidade_encaminhada == 8_008
assert progressos[0] == (0, 8_008)
assert progressos[-1] == (8_008, 8_008)

print({
    "id_alvo": id_alvo,
    "dezenas": len(dezenas),
    "combinacoes_encaminhadas": relatorio.quantidade_encaminhada,
    "duracao_segundos": relatorio.duracao_segundos,
    "gravacoes": 0,
})
