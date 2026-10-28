"""Contrato hierárquico e extensível do novo funil de combinações."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
from types import MappingProxyType
from typing import Protocol

from .gerador import Combinacao


SEIS_CASAS = Decimal("0.000001")
CEM = Decimal(100)


class ErroContratoFunil(ValueError):
    """Indica uma definição ou decisão incompatível com o novo funil."""

    def __init__(self, codigo: str, mensagem: str) -> None:
        super().__init__(mensagem)
        self.codigo = codigo


@dataclass(frozen=True, slots=True)
class DecisaoFiltro:
    """Saída auditável produzida por um filtro para uma combinação."""

    codigo_filtro: str
    aprovada: bool
    motivo: str
    evidencias: Mapping[str, object]

    @classmethod
    def criar(
        cls,
        *,
        codigo_filtro: str,
        aprovada: bool,
        motivo: str,
        evidencias: Mapping[str, object],
    ) -> DecisaoFiltro:
        """Valida e congela a decisão para impedir alterações posteriores."""

        if not isinstance(codigo_filtro, str) or not codigo_filtro.strip():
            raise ErroContratoFunil(
                "CODIGO_DECISAO_INVALIDO", "A decisão exige código de filtro."
            )
        if not isinstance(aprovada, bool):
            raise TypeError("aprovada deve ser booleana.")
        if not isinstance(motivo, str) or not motivo.strip():
            raise ErroContratoFunil(
                "MOTIVO_AUSENTE", "Toda decisão deve explicar seu motivo."
            )
        if not isinstance(evidencias, Mapping):
            raise TypeError("evidencias deve ser um mapeamento.")
        return cls(
            codigo_filtro.strip(),
            aprovada,
            motivo.strip(),
            MappingProxyType(dict(evidencias)),
        )


class AvaliadorFiltro(Protocol):
    """Assinatura única para qualquer filtro presente ou futuro."""

    def __call__(self, combinacao: Combinacao) -> DecisaoFiltro:
        """Avalia sem efeitos externos e retorna motivo e evidências."""


@dataclass(frozen=True, slots=True)
class DefinicaoFiltro:
    """Metadados estáveis e avaliador de um filtro registrável."""

    codigo: str
    nome: str
    ordem: int
    avaliador: AvaliadorFiltro


@dataclass(frozen=True, slots=True)
class DefinicaoFamilia:
    """Agrupa filtros conceitualmente relacionados e ordenados."""

    codigo: str
    nome: str
    ordem: int
    filtros: tuple[DefinicaoFiltro, ...]


@dataclass(frozen=True, slots=True)
class LinhaFiltro:
    """Contabilidade líquida de um filtro na posição executada."""

    codigo_filtro: str
    nome_filtro: str
    ordem: int
    avaliacoes: int
    exclusoes: int
    saldo: int
    percentual_total_inicial: Decimal
    percentual_saldo_recebido: Decimal


@dataclass(frozen=True, slots=True)
class LinhaFamilia:
    """Subtotal reconciliado de uma família do funil."""

    codigo_familia: str
    nome_familia: str
    ordem: int
    entrada: int
    exclusoes: int
    saldo: int
    percentual_total_inicial: Decimal
    percentual_saldo_recebido: Decimal
    filtros: tuple[LinhaFiltro, ...]


@dataclass(frozen=True, slots=True)
class RelatorioFunilExtensivel:
    """Resultado consolidado independente da quantidade de famílias/filtros."""

    total_inicial: int
    total_excluido: int
    total_aprovado: int
    familias: tuple[LinhaFamilia, ...]
    combinacoes_aprovadas: tuple[Combinacao, ...]

    @property
    def reconciliado(self) -> bool:
        """Confirma a igualdade obrigatória do funil."""

        return self.total_inicial == self.total_excluido + self.total_aprovado


def _texto(nome: str, valor: object) -> str:
    if not isinstance(valor, str) or not valor.strip():
        raise ErroContratoFunil(
            "IDENTIFICADOR_INVALIDO", f"{nome} deve ser texto preenchido."
        )
    return valor.strip()


def _ordem(nome: str, valor: object) -> int:
    if isinstance(valor, bool) or not isinstance(valor, int) or valor < 1:
        raise ErroContratoFunil(
            "ORDEM_INVALIDA", f"{nome} deve ser um inteiro positivo."
        )
    return valor


def _validar_plano(
    familias: Iterable[DefinicaoFamilia],
) -> tuple[DefinicaoFamilia, ...]:
    try:
        recebidas = tuple(familias)
    except TypeError as erro:
        raise TypeError("As famílias devem ser iteráveis.") from erro
    if not recebidas:
        raise ErroContratoFunil("PLANO_VAZIO", "O funil exige ao menos uma família.")
    if any(not isinstance(item, DefinicaoFamilia) for item in recebidas):
        raise TypeError("O plano aceita somente DefinicaoFamilia.")

    codigos_familias: set[str] = set()
    ordens_familias: set[int] = set()
    codigos_filtros: set[str] = set()
    normalizadas: list[DefinicaoFamilia] = []
    for familia in recebidas:
        codigo = _texto("codigo da família", familia.codigo)
        nome = _texto("nome da família", familia.nome)
        ordem = _ordem("ordem da família", familia.ordem)
        if codigo in codigos_familias or ordem in ordens_familias:
            raise ErroContratoFunil(
                "FAMILIA_DUPLICADA", "Códigos e ordens de famílias devem ser únicos."
            )
        if not familia.filtros:
            raise ErroContratoFunil(
                "FAMILIA_SEM_FILTRO", "Toda família deve possuir ao menos um filtro."
            )
        codigos_familias.add(codigo)
        ordens_familias.add(ordem)
        ordens_filtros: set[int] = set()
        filtros: list[DefinicaoFiltro] = []
        for filtro in familia.filtros:
            if not isinstance(filtro, DefinicaoFiltro):
                raise TypeError("A família aceita somente DefinicaoFiltro.")
            codigo_filtro = _texto("codigo do filtro", filtro.codigo)
            nome_filtro = _texto("nome do filtro", filtro.nome)
            ordem_filtro = _ordem("ordem do filtro", filtro.ordem)
            if codigo_filtro in codigos_filtros:
                raise ErroContratoFunil(
                    "FILTRO_DUPLICADO", "O código do filtro deve ser único no funil."
                )
            if ordem_filtro in ordens_filtros:
                raise ErroContratoFunil(
                    "ORDEM_FILTRO_DUPLICADA",
                    "A ordem dos filtros deve ser única dentro da família.",
                )
            if not callable(filtro.avaliador):
                raise TypeError("O avaliador do filtro deve ser chamável.")
            codigos_filtros.add(codigo_filtro)
            ordens_filtros.add(ordem_filtro)
            filtros.append(
                DefinicaoFiltro(codigo_filtro, nome_filtro, ordem_filtro, filtro.avaliador)
            )
        normalizadas.append(
            DefinicaoFamilia(
                codigo, nome, ordem, tuple(sorted(filtros, key=lambda item: item.ordem))
            )
        )
    return tuple(sorted(normalizadas, key=lambda item: item.ordem))


def _percentual(quantidade: int, base: int) -> Decimal:
    if base == 0:
        return Decimal("0.000000")
    return (Decimal(quantidade) * CEM / Decimal(base)).quantize(
        SEIS_CASAS, rounding=ROUND_HALF_UP
    )


def executar_funil_extensivel(
    combinacoes: Iterable[Combinacao],
    familias: Iterable[DefinicaoFamilia],
) -> RelatorioFunilExtensivel:
    """Executa famílias/filtros em ordem e para na primeira exclusão.

    A exclusão é atribuída somente ao filtro decisivo. A quantidade de famílias
    e filtros é definida pelo plano recebido, sem colunas ou códigos fixos.
    """

    plano = _validar_plano(familias)
    combinacoes_fixas = tuple(combinacoes)
    total = len(combinacoes_fixas)
    avaliacoes = {
        filtro.codigo: 0 for familia in plano for filtro in familia.filtros
    }
    exclusoes = dict.fromkeys(avaliacoes, 0)
    aprovadas: list[Combinacao] = []

    for combinacao in combinacoes_fixas:
        excluida = False
        for familia in plano:
            for filtro in familia.filtros:
                avaliacoes[filtro.codigo] += 1
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
                    exclusoes[filtro.codigo] += 1
                    excluida = True
                    break
            if excluida:
                break
        if not excluida:
            aprovadas.append(combinacao)

    saldo = total
    linhas_familias: list[LinhaFamilia] = []
    for familia in plano:
        entrada_familia = saldo
        linhas_filtros: list[LinhaFiltro] = []
        for filtro in familia.filtros:
            excluidas = exclusoes[filtro.codigo]
            recebido_filtro = saldo
            saldo -= excluidas
            linhas_filtros.append(
                LinhaFiltro(
                    filtro.codigo,
                    filtro.nome,
                    filtro.ordem,
                    avaliacoes[filtro.codigo],
                    excluidas,
                    saldo,
                    _percentual(excluidas, total),
                    _percentual(excluidas, recebido_filtro),
                )
            )
        exclusoes_familia = entrada_familia - saldo
        linhas_familias.append(
            LinhaFamilia(
                familia.codigo,
                familia.nome,
                familia.ordem,
                entrada_familia,
                exclusoes_familia,
                saldo,
                _percentual(exclusoes_familia, total),
                _percentual(exclusoes_familia, entrada_familia),
                tuple(linhas_filtros),
            )
        )
    relatorio = RelatorioFunilExtensivel(
        total,
        total - len(aprovadas),
        len(aprovadas),
        tuple(linhas_familias),
        tuple(aprovadas),
    )
    if not relatorio.reconciliado or saldo != relatorio.total_aprovado:
        raise RuntimeError("O fechamento interno do funil extensível divergiu.")
    return relatorio
