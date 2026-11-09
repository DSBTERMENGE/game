"""Configuração reproduzível da pesquisa de seleção de dezenas."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
import hashlib
import json


MODOS_QUANTIDADE = frozenset({"MAX", "FIXA"})
PRECISAO_PARAMETRO = Decimal("0.000001")


def _inteiro_positivo(nome: str, valor: int) -> int:
    if isinstance(valor, bool) or not isinstance(valor, int):
        raise TypeError(f"{nome} deve ser inteiro.")
    if valor <= 0:
        raise ValueError(f"{nome} deve ser positivo.")
    return valor


def _decimal_finito(nome: str, valor: Decimal) -> Decimal:
    if not isinstance(valor, Decimal):
        raise TypeError(f"{nome} deve ser Decimal.")
    if not valor.is_finite():
        raise ValueError(f"{nome} deve ser finito.")
    return valor


@dataclass(frozen=True, slots=True)
class ConfiguracaoSelecaoDezenas:
    nome: str
    fator_k: Decimal
    fator_j: Decimal
    modo_quantidade: str
    quantidade_dezenas: int | None
    versao_calculo: int

    def __post_init__(self) -> None:
        if not isinstance(self.nome, str) or not self.nome.strip():
            raise ValueError("nome deve ser texto preenchido.")
        object.__setattr__(self, "nome", self.nome.strip())
        k = _decimal_finito("fator_k", self.fator_k).quantize(
            PRECISAO_PARAMETRO, rounding=ROUND_HALF_UP
        )
        j = _decimal_finito("fator_j", self.fator_j).quantize(
            PRECISAO_PARAMETRO, rounding=ROUND_HALF_UP
        )
        if k <= 0 or k > 1:
            raise ValueError("fator_k deve satisfazer 0 < k <= 1.")
        if j < -k or j > k:
            raise ValueError("fator_j deve satisfazer -k <= j <= k.")
        object.__setattr__(self, "fator_k", k)
        object.__setattr__(self, "fator_j", j)
        if not isinstance(self.modo_quantidade, str):
            raise TypeError("modo_quantidade deve ser texto.")
        modo = self.modo_quantidade.strip().upper()
        if modo not in MODOS_QUANTIDADE:
            raise ValueError("modo_quantidade deve ser MAX ou FIXA.")
        object.__setattr__(self, "modo_quantidade", modo)
        if modo == "MAX":
            if self.quantidade_dezenas is not None:
                raise ValueError("quantidade_dezenas deve ser nula no modo MAX.")
        elif (
            isinstance(self.quantidade_dezenas, bool)
            or not isinstance(self.quantidade_dezenas, int)
            or not 6 <= self.quantidade_dezenas <= 60
        ):
            raise ValueError("quantidade_dezenas deve ficar entre 6 e 60 no modo FIXA.")
        object.__setattr__(self, "versao_calculo", _inteiro_positivo(
            "versao_calculo", self.versao_calculo
        ))

    def conteudo_assinavel(self) -> dict[str, int | str | None]:
        return {
            "fator_j": format(self.fator_j, "f"),
            "fator_k": format(self.fator_k, "f"),
            "modo_quantidade": self.modo_quantidade,
            "nome": self.nome,
            "quantidade_dezenas": self.quantidade_dezenas,
            "versao_calculo": self.versao_calculo,
        }

    @property
    def assinatura_sha256(self) -> str:
        conteudo = json.dumps(
            self.conteudo_assinavel(), ensure_ascii=False,
            sort_keys=True, separators=(",", ":"),
        ).encode("utf-8")
        return hashlib.sha256(conteudo).hexdigest()


def configuracao_selecao_inicial() -> ConfiguracaoSelecaoDezenas:
    return ConfiguracaoSelecaoDezenas(
        nome="Seleção inicial",
        fator_k=Decimal("1.000000"),
        fator_j=Decimal("0.000000"),
        modo_quantidade="MAX",
        quantidade_dezenas=None,
        versao_calculo=1,
    )
