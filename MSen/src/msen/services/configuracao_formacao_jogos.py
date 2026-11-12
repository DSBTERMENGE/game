"""Configuração imutável da futura formação de jogos selecionados."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from hashlib import sha256
import json
import re


MAXIMO_JOGOS = 50_063_860
DUAS_CASAS = Decimal("0.01")
HASH_SHA256 = re.compile(r"^[0-9a-f]{64}$")


class ErroConfiguracaoFormacaoJogos(ValueError):
    def __init__(self, codigo: str, mensagem: str) -> None:
        super().__init__(mensagem)
        self.codigo = codigo


def _inteiro_positivo(nome: str, valor: object, *, maximo: int | None = None) -> int:
    if isinstance(valor, bool) or not isinstance(valor, int) or valor < 1:
        raise ErroConfiguracaoFormacaoJogos(
            "CONFIGURACAO_JOGOS_INVALIDA", f"{nome} deve ser um inteiro positivo."
        )
    if maximo is not None and valor > maximo:
        raise ErroConfiguracaoFormacaoJogos(
            "CONFIGURACAO_JOGOS_INVALIDA", f"{nome} deve ser no máximo {maximo}."
        )
    return valor


def _assinatura(nome: str, valor: object) -> str:
    if not isinstance(valor, str) or not HASH_SHA256.fullmatch(valor):
        raise ErroConfiguracaoFormacaoJogos(
            "CONFIGURACAO_JOGOS_INVALIDA",
            f"{nome} deve ser uma assinatura SHA-256 minúscula.",
        )
    return valor


def _valor_unitario(valor: object) -> Decimal:
    try:
        decimal = Decimal(str(valor))
    except (InvalidOperation, ValueError) as erro:
        raise ErroConfiguracaoFormacaoJogos(
            "VALOR_JOGO_INVALIDO", "O valor de um jogo deve ser monetário."
        ) from erro
    if not decimal.is_finite() or decimal <= 0 or decimal != decimal.quantize(DUAS_CASAS):
        raise ErroConfiguracaoFormacaoJogos(
            "VALOR_JOGO_INVALIDO",
            "O valor de um jogo deve ser maior que zero e possuir no máximo duas casas decimais.",
        )
    return decimal.quantize(DUAS_CASAS)


@dataclass(frozen=True, slots=True)
class ConfiguracaoFormacaoJogos:
    id_alvo_selecao: int
    quantidade_dezenas: int
    quantidade_combinacoes_brutas: int
    quantidade_jogos_solicitada: int
    valor_unitario: Decimal
    assinatura_screener: str
    versao_classificador: int
    assinatura_classificador: str
    versao_formacao: int = 1

    @classmethod
    def criar(
        cls,
        *,
        id_alvo_selecao: int,
        quantidade_dezenas: int,
        quantidade_combinacoes_brutas: int,
        quantidade_jogos_solicitada: int,
        valor_unitario: object,
        assinatura_screener: str,
        versao_classificador: int,
        assinatura_classificador: str,
        versao_formacao: int = 1,
    ) -> ConfiguracaoFormacaoJogos:
        alvo = _inteiro_positivo("id_alvo_selecao", id_alvo_selecao)
        dezenas = _inteiro_positivo("quantidade_dezenas", quantidade_dezenas, maximo=60)
        if dezenas < 6:
            raise ErroConfiguracaoFormacaoJogos(
                "DEZENAS_INSUFICIENTES", "São necessárias ao menos seis dezenas."
            )
        brutas = _inteiro_positivo(
            "quantidade_combinacoes_brutas", quantidade_combinacoes_brutas,
            maximo=MAXIMO_JOGOS,
        )
        solicitada = _inteiro_positivo(
            "quantidade_jogos_solicitada", quantidade_jogos_solicitada,
            maximo=MAXIMO_JOGOS,
        )
        return cls(
            alvo,
            dezenas,
            brutas,
            solicitada,
            _valor_unitario(valor_unitario),
            _assinatura("assinatura_screener", assinatura_screener),
            _inteiro_positivo("versao_classificador", versao_classificador),
            _assinatura("assinatura_classificador", assinatura_classificador),
            _inteiro_positivo("versao_formacao", versao_formacao),
        )

    @property
    def valor_maximo_previsto(self) -> Decimal:
        return (self.valor_unitario * self.quantidade_jogos_solicitada).quantize(
            DUAS_CASAS
        )

    @property
    def chave_idempotencia(self) -> str:
        conteudo = {
            "assinatura_classificador": self.assinatura_classificador,
            "assinatura_screener": self.assinatura_screener,
            "id_alvo_selecao": self.id_alvo_selecao,
            "quantidade_combinacoes_brutas": self.quantidade_combinacoes_brutas,
            "quantidade_dezenas": self.quantidade_dezenas,
            "quantidade_jogos_solicitada": self.quantidade_jogos_solicitada,
            "valor_unitario": format(self.valor_unitario, ".2f"),
            "versao_classificador": self.versao_classificador,
            "versao_formacao": self.versao_formacao,
        }
        canonico = json.dumps(
            conteudo, ensure_ascii=False, sort_keys=True, separators=(",", ":")
        )
        return sha256(canonico.encode("utf-8")).hexdigest()
