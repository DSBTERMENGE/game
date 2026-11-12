from datetime import date

from msen.screener import (
    DecisaoFiltro,
    DefinicaoFamilia,
    DefinicaoFiltro,
    EnvelopeFotografia,
    criar_fotografia_configuracao,
    envelopar_fotografia,
)
from msen.services.integracao_screener_formacao_jogos import (
    PlanoScreenerFormacao,
    executar_screener_formacao,
)


def _decisao(codigo: str, aprovada: bool) -> DecisaoFiltro:
    return DecisaoFiltro.criar(
        codigo_filtro=codigo,
        aprovada=aprovada,
        motivo="aprovada" if aprovada else "reprovada",
        evidencias={},
    )


def _plano() -> PlanoScreenerFormacao:
    primeiro = DefinicaoFiltro(
        "F_1", "Primeiro filtro", 1,
        lambda combinacao: _decisao("F_1", combinacao[0] != 1),
    )
    segundo = DefinicaoFiltro(
        "F_2", "Segundo filtro", 2,
        lambda combinacao: _decisao("F_2", combinacao[-1] != 7),
    )
    familias = (
        DefinicaoFamilia("FAMILIA_1", "Família 1", 1, (primeiro,)),
        DefinicaoFamilia("FAMILIA_2", "Família 2", 2, (segundo,)),
    )
    fotografia = criar_fotografia_configuracao(
        familias=familias,
        parametros_filtros={"F_1": {"regra": 1}, "F_2": {"regra": 2}},
        grupos_padroes=(),
        versoes_calculo={"teste": 1},
        modo="formacao_jogos",
        semente=0,
        limite_combinacoes=7,
        data_fotografia=date(2026, 11, 10),
    )
    return PlanoScreenerFormacao.criar(
        familias=familias,
        fotografia=envelopar_fotografia(fotografia),
        filtros_inativos=("F_3",),
    )


def test_executa_em_fluxo_e_preserva_primeira_reprovacao() -> None:
    aprovadas = []
    resultado = executar_screener_formacao(
        range(1, 8), _plano(), ao_aprovar=aprovadas.append
    )

    assert resultado.geracao.quantidade_encaminhada == 7
    assert resultado.screener.total_examinado == 7
    assert resultado.screener.total_reprovado == 7
    assert resultado.screener.total_aprovado == 0
    assert resultado.screener.reconciliado
    filtro_1 = resultado.screener.familias[0].filtros[0]
    filtro_2 = resultado.screener.familias[1].filtros[0]
    assert (filtro_1.avaliacoes, filtro_1.exclusoes) == (7, 6)
    assert (filtro_2.avaliacoes, filtro_2.exclusoes) == (1, 1)
    assert aprovadas == []
    assert resultado.screener.filtros_inativos == ("F_3",)


def test_cancelamento_mantem_contabilidade_parcial_reconciliada() -> None:
    chamadas = 0

    def cancelar() -> bool:
        nonlocal chamadas
        chamadas += 1
        return chamadas > 3

    resultado = executar_screener_formacao(
        range(1, 9), _plano(), cancelamento_solicitado=cancelar
    )

    assert resultado.geracao.estado == "CANCELADA"
    assert resultado.geracao.quantidade_encaminhada == 3
    assert resultado.screener.total_examinado == 3
    assert resultado.screener.reconciliado


def test_recusa_fotografia_adulterada() -> None:
    plano = _plano()
    adulterada = EnvelopeFotografia(
        plano.fotografia.conteudo_json + " ", plano.fotografia.checksum_sha256
    )

    try:
        PlanoScreenerFormacao.criar(
            familias=plano.familias,
            fotografia=adulterada,
            filtros_inativos=plano.filtros_inativos,
        )
    except ValueError as erro:
        assert "alterada ou corrompida" in str(erro)
    else:
        raise AssertionError("A fotografia adulterada foi aceita.")


def test_recusa_filtro_simultaneamente_ativo_e_inativo() -> None:
    plano = _plano()

    with pytest.raises(ValueError, match="ativo e inativo"):
        PlanoScreenerFormacao.criar(
            familias=plano.familias,
            fotografia=plano.fotografia,
            filtros_inativos=("F_1",),
        )
