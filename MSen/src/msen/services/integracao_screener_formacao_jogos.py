"""Integra o gerador streaming ao contrato oficial do Screener extensível."""

from __future__ import annotations

from collections.abc import Callable, Iterable
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP

from msen.screener import (
    DecisaoFiltro,
    DefinicaoFamilia,
    EnvelopeFotografia,
    ErroContratoFunil,
    LinhaFamilia,
    LinhaFiltro,
    verificar_envelope_fotografia,
    validar_plano_funil,
)

from .motor_formacao_jogos import (
    Combinacao,
    RelatorioGeracaoControlada,
    executar_geracao_controlada,
)


SEIS_CASAS = Decimal("0.000001")


def _percentual(quantidade: int, base: int) -> Decimal:
    if base == 0:
        return Decimal("0.000000")
    return (Decimal(quantidade) * 100 / Decimal(base)).quantize(
        SEIS_CASAS, rounding=ROUND_HALF_UP
    )


@dataclass(frozen=True, slots=True)
class PlanoScreenerFormacao:
    familias: tuple[DefinicaoFamilia, ...]
    fotografia: EnvelopeFotografia
    filtros_inativos: tuple[str, ...] = ()

    @classmethod
    def criar(
        cls,
        *,
        familias: Iterable[DefinicaoFamilia],
        fotografia: EnvelopeFotografia,
        filtros_inativos: Iterable[str] = (),
    ) -> PlanoScreenerFormacao:
        plano = validar_plano_funil(familias)
        if not isinstance(fotografia, EnvelopeFotografia):
            raise TypeError("fotografia deve ser EnvelopeFotografia.")
        if not verificar_envelope_fotografia(fotografia):
            raise ValueError("A fotografia do Screener foi alterada ou corrompida.")
        inativos = tuple(sorted(set(filtros_inativos)))
        ativos = {filtro.codigo for familia in plano for filtro in familia.filtros}
        if any(not isinstance(codigo, str) or not codigo.strip() for codigo in inativos):
            raise ValueError("Todo filtro inativo deve possuir código.")
        if ativos.intersection(inativos):
            raise ValueError("Um filtro não pode estar ativo e inativo ao mesmo tempo.")
        return cls(plano, fotografia, inativos)


@dataclass(frozen=True, slots=True)
class RelatorioScreenerFormacao:
    total_examinado: int
    total_reprovado: int
    total_aprovado: int
    familias: tuple[LinhaFamilia, ...]
    filtros_inativos: tuple[str, ...]
    assinatura_screener: str

    @property
    def reconciliado(self) -> bool:
        return self.total_examinado == self.total_reprovado + self.total_aprovado


@dataclass(frozen=True, slots=True)
class ResultadoIntegracaoScreener:
    geracao: RelatorioGeracaoControlada
    screener: RelatorioScreenerFormacao


class AdaptadorScreenerFormacao:
    """Aplica o plano em fluxo e conserva somente contadores."""

    def __init__(
        self,
        plano: PlanoScreenerFormacao,
        *,
        ao_aprovar: Callable[[Combinacao], None] | None = None,
    ) -> None:
        if not isinstance(plano, PlanoScreenerFormacao):
            raise TypeError("plano deve ser PlanoScreenerFormacao.")
        if ao_aprovar is not None and not callable(ao_aprovar):
            raise TypeError("ao_aprovar deve ser chamável.")
        self._plano = plano
        self._ao_aprovar = ao_aprovar or (lambda _combinacao: None)
        self._total = 0
        self._aprovadas = 0
        self._avaliacoes = {
            filtro.codigo: 0
            for familia in plano.familias for filtro in familia.filtros
        }
        self._exclusoes = dict.fromkeys(self._avaliacoes, 0)

    def __call__(self, combinacao: Combinacao) -> None:
        self._total += 1
        for familia in self._plano.familias:
            for filtro in familia.filtros:
                self._avaliacoes[filtro.codigo] += 1
                decisao = filtro.avaliador(combinacao)
                if not isinstance(decisao, DecisaoFiltro):
                    raise ErroContratoFunil(
                        "DECISAO_INVALIDA", "O avaliador deve retornar DecisaoFiltro."
                    )
                if decisao.codigo_filtro != filtro.codigo:
                    raise ErroContratoFunil(
                        "CODIGO_DECISAO_DIVERGENTE",
                        "A decisão deve identificar o filtro que a produziu.",
                    )
                if not decisao.aprovada:
                    self._exclusoes[filtro.codigo] += 1
                    return
        self._aprovadas += 1
        self._ao_aprovar(combinacao)

    def relatorio(self) -> RelatorioScreenerFormacao:
        saldo = self._total
        familias = []
        for familia in self._plano.familias:
            entrada_familia = saldo
            linhas = []
            for filtro in familia.filtros:
                entrada_filtro = saldo
                excluidas = self._exclusoes[filtro.codigo]
                saldo -= excluidas
                linhas.append(LinhaFiltro(
                    filtro.codigo, filtro.nome, filtro.ordem,
                    self._avaliacoes[filtro.codigo], excluidas, saldo,
                    _percentual(excluidas, self._total),
                    _percentual(excluidas, entrada_filtro),
                ))
            excluidas_familia = entrada_familia - saldo
            familias.append(LinhaFamilia(
                familia.codigo, familia.nome, familia.ordem,
                entrada_familia, excluidas_familia, saldo,
                _percentual(excluidas_familia, self._total),
                _percentual(excluidas_familia, entrada_familia),
                tuple(linhas),
            ))
        relatorio = RelatorioScreenerFormacao(
            self._total, self._total - self._aprovadas, self._aprovadas,
            tuple(familias), self._plano.filtros_inativos,
            self._plano.fotografia.checksum_sha256,
        )
        if not relatorio.reconciliado or saldo != relatorio.total_aprovado:
            raise RuntimeError("A contabilidade streaming do Screener divergiu.")
        return relatorio


def executar_screener_formacao(
    dezenas: Iterable[int],
    plano: PlanoScreenerFormacao,
    *,
    ao_aprovar: Callable[[Combinacao], None] | None = None,
    informar_progresso: Callable[[int, int], None] | None = None,
    cancelamento_solicitado: Callable[[], bool] | None = None,
    intervalo_progresso: int = 1_000,
) -> ResultadoIntegracaoScreener:
    adaptador = AdaptadorScreenerFormacao(plano, ao_aprovar=ao_aprovar)
    geracao = executar_geracao_controlada(
        dezenas,
        adaptador,
        informar_progresso=informar_progresso,
        cancelamento_solicitado=cancelamento_solicitado,
        intervalo_progresso=intervalo_progresso,
    )
    return ResultadoIntegracaoScreener(geracao, adaptador.relatorio())
