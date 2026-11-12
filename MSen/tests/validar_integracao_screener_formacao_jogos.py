"""Validação executável da etapa 26.5, sem persistência."""

from datetime import date

from dotenv import load_dotenv

from msen.screener import DecisaoFiltro, DefinicaoFamilia, DefinicaoFiltro
from msen.screener import criar_fotografia_configuracao, envelopar_fotografia
from msen.services.homologacao_screener import (
    ErroHomologacaoScreener,
    consultar_homologacao_screener_no_banco,
    validar_homologacao_screener,
)
from msen.services.integracao_screener_formacao_jogos import (
    PlanoScreenerFormacao,
    executar_screener_formacao,
)


def _decisao(codigo: str, aprovada: bool) -> DecisaoFiltro:
    return DecisaoFiltro.criar(
        codigo_filtro=codigo,
        aprovada=aprovada,
        motivo="regra controlada",
        evidencias={},
    )


def _plano() -> PlanoScreenerFormacao:
    familias = (
        DefinicaoFamilia(
            "F1", "Primeira família", 1,
            (DefinicaoFiltro("A", "Primeiro número", 1, lambda c: _decisao("A", c[0] != 1)),),
        ),
        DefinicaoFamilia(
            "F2", "Segunda família", 2,
            (DefinicaoFiltro("B", "Último número", 1, lambda c: _decisao("B", c[-1] != 7)),),
        ),
    )
    fotografia = criar_fotografia_configuracao(
        familias=familias,
        parametros_filtros={"A": {"regra": "primeiro"}, "B": {"regra": "último"}},
        grupos_padroes=(),
        versoes_calculo={"integracao": 1},
        modo="formacao_jogos",
        semente=0,
        limite_combinacoes=7,
        data_fotografia=date.today(),
    )
    return PlanoScreenerFormacao.criar(
        familias=familias,
        fotografia=envelopar_fotografia(fotografia),
        filtros_inativos=("C",),
    )


def main() -> None:
    resultado = executar_screener_formacao(range(1, 8), _plano())
    assert resultado.geracao.quantidade_encaminhada == 7
    assert resultado.screener.reconciliado
    assert resultado.screener.total_examinado == 7
    assert resultado.screener.total_reprovado == 7
    assert resultado.screener.total_aprovado == 0
    assert resultado.screener.familias[0].filtros[0].avaliacoes == 7
    assert resultado.screener.familias[1].filtros[0].avaliacoes == 1
    assert resultado.screener.filtros_inativos == ("C",)

    load_dotenv(".env")
    estado = consultar_homologacao_screener_no_banco()
    assert not estado.atualizado
    try:
        validar_homologacao_screener(
            estado, codigos_carregados=set(), codigos_padroes_selecionados=set()
        )
    except ErroHomologacaoScreener as erro:
        assert erro.codigo == "ALGORITMO_DESATUALIZADO"
    else:
        raise AssertionError("O Screener desatualizado não foi bloqueado.")

    print("Etapa 26.5 validada: integração reconciliada e homologação respeitada.")


if __name__ == "__main__":
    main()
