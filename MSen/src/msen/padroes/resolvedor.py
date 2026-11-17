"""Resolução controlada das funções detectoras cadastradas no banco."""

from __future__ import annotations

from importlib import import_module
import re

from .contratos import DetectorPadrao


NAMESPACE_AUTORIZADO = "msen.padroes."
NOME_QUALIFICADO = re.compile(
    r"^[A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)+$"
)


class ErroResolucaoDetector(RuntimeError):
    """Falha funcional segura ao localizar ou executar um detector."""

    def __init__(self, codigo: str, mensagem: str) -> None:
        super().__init__(mensagem)
        self.codigo = codigo


def resolver_funcao_detectora(nome_qualificado: str | None) -> DetectorPadrao:
    """Localiza uma função detectora dentro do namespace autorizado."""

    if nome_qualificado is None or (
        isinstance(nome_qualificado, str) and not nome_qualificado.strip()
    ):
        raise ErroResolucaoDetector(
            "FUNCAO_NAO_INFORMADA", "A função detectora não foi informada."
        )
    if not isinstance(nome_qualificado, str):
        raise TypeError("O nome da função detectora deve ser texto ou nulo.")

    nome = nome_qualificado.strip()
    if NOME_QUALIFICADO.fullmatch(nome) is None:
        raise ErroResolucaoDetector(
            "FUNCAO_NAO_ENCONTRADA", f"Função {nome}() não encontrada."
        )

    modulo_nome, _, funcao_nome = nome.rpartition(".")
    if not modulo_nome.startswith(NAMESPACE_AUTORIZADO):
        raise ErroResolucaoDetector(
            "MODULO_NAO_AUTORIZADO",
            "A função detectora não pertence a um módulo autorizado.",
        )

    try:
        modulo = import_module(modulo_nome)
    except ModuleNotFoundError:
        raise ErroResolucaoDetector(
            "MODULO_NAO_ENCONTRADO", f"Módulo {modulo_nome} não encontrado."
        ) from None

    try:
        detector = getattr(modulo, funcao_nome)
    except AttributeError:
        raise ErroResolucaoDetector(
            "FUNCAO_NAO_ENCONTRADA", f"Função {nome}() não encontrada."
        ) from None
    if not callable(detector):
        raise ErroResolucaoDetector(
            "FUNCAO_NAO_CHAMAVEL", f"O objeto {nome} não é uma função chamável."
        )
    return detector


def executar_funcao_detectora(
    nome_qualificado: str | None, dezenas: tuple[int, ...]
) -> bool:
    """Resolve, executa e exige resposta estritamente booleana do detector."""

    detector = resolver_funcao_detectora(nome_qualificado)
    resultado = detector(dezenas)
    if type(resultado) is not bool:
        raise ErroResolucaoDetector(
            "RESPOSTA_DETECTOR_INVALIDA",
            "A função detectora deve devolver verdadeiro ou falso.",
        )
    return resultado
