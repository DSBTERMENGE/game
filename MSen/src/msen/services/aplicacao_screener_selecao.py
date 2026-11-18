"""Aplica o motor comum às dezenas registradas para um concurso-alvo."""

from collections.abc import Callable
from decimal import Decimal

from msen.config import carregar_configuracao_banco
from msen.database import abrir_conexao
from msen.screener import executar_funil_extensivel

from .combinacoes_selecao_dezenas import ErroCombinacoesSelecao
from .referencias_screener_selecao import verificar_referencias_atualizadas
from .solicitacao_screener_selecao import SolicitacaoScreenerSelecao
from .entradas_motor_screener import adaptar_selecao_dezenas


def carregar_dezenas_alvo_no_banco(id_alvo: int) -> tuple[int, ...]:
    """Lê somente as dezenas marcadas como retornadas para o alvo."""
    with abrir_conexao(carregar_configuracao_banco()) as conexao:
        with conexao.cursor() as cursor:
            cursor.execute(
                "SELECT dezena FROM avaliacoes_dezenas_pesquisa "
                "WHERE id_alvo_selecao=%s AND retornada ORDER BY posicao_ranking",
                (id_alvo,),
            )
            return tuple(linha[0] for linha in cursor.fetchall())

def aplicar_screener_selecao(
    solicitacao: SolicitacaoScreenerSelecao,
    *,
    verificar_referencias: Callable[[], dict[str, object]] = verificar_referencias_atualizadas,
    carregar_dezenas: Callable[[int], tuple[int, ...]] = carregar_dezenas_alvo_no_banco,
    montar_plano: Callable[[Decimal], object] | None = None,
    executar: Callable[..., object] = executar_funil_extensivel,
    adaptar_combinacoes: Callable[..., object] = adaptar_selecao_dezenas,
) -> dict[str, object]:
    """Aplica à seleção o mesmo plano usado pelo Teste e pela Aplicação."""
    if not isinstance(solicitacao, SolicitacaoScreenerSelecao):
        raise TypeError("A aplicação exige SolicitacaoScreenerSelecao.")
    verificar_referencias()
    dezenas = carregar_dezenas(solicitacao.id_alvo)
    combinacoes = adaptar_combinacoes(dezenas)
    if combinacoes.contexto["volume_elevado"]:
        raise ErroCombinacoesSelecao(
            "VOLUME_ELEVADO_SCREENER",
            "O volume bruto ultrapassa o limite seguro de 10.000 combinações.",
        )
    if montar_plano is None:
        # Importação tardia evita ciclo durante a criação da aplicação Flask.
        from msen.api.screener_extensivel_service import montar_plano_filtros_screener
        montar_plano = montar_plano_filtros_screener
    plano = montar_plano(solicitacao.limite_raridade)
    relatorio = executar(
        combinacoes,
        plano.familias,
        limite_aprovadas=solicitacao.quantidade_maxima_jogos,
    )
    interrompido = (
        relatorio.total_inicial < combinacoes.total_combinacoes
        and relatorio.total_aprovado >= solicitacao.quantidade_maxima_jogos
    )
    return {
        "total_recebido": relatorio.total_inicial,
        "total_aprovado": relatorio.total_aprovado,
        "total_excluido": relatorio.total_excluido,
        "total_universo": combinacoes.total_combinacoes,
        "interrompido_por_limite": interrompido,
        "combinacoes_aprovadas": relatorio.combinacoes_aprovadas,
        "exclusoes": (),
    }
