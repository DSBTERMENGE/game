"""Regras de domínio da Gestão do desenvolvimento."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Any, Mapping


TIPOS = frozenset({
    "ERRO", "MAU_FUNCIONAMENTO", "MODIFICACAO",
    "NOVA_FUNCIONALIDADE", "NAO_CLASSIFICADO",
})
STATUS_TRABALHO = frozenset({
    "NAO_INICIADO", "EM_ANALISE", "EM_ANDAMENTO",
    "AGUARDANDO_VALIDACAO", "CONCLUIDO", "CANCELADO",
})
STATUS_PUBLICACAO = frozenset({
    "NAO_APLICAVEL", "AGUARDANDO_PUBLICACAO", "PUBLICADO",
    "FALHA_PUBLICACAO",
})
CAMPOS_MUTAVEIS = frozenset({
    "tipo", "titulo", "data_registro", "descricao",
    "status_trabalho", "status_publicacao",
    "pagina_origem", "observacao_publicacao",
})


class ErroGestaoDesenvolvimento(ValueError):
    def __init__(self, codigo: str, mensagem: str) -> None:
        super().__init__(mensagem)
        self.codigo = codigo


def _texto(nome: str, valor: Any, limite: int, obrigatorio: bool) -> str | None:
    if valor is None and not obrigatorio:
        return None
    if not isinstance(valor, str):
        raise ErroGestaoDesenvolvimento("CAMPO_INVALIDO", f"{nome} deve ser texto.")
    normalizado = valor.strip()
    if obrigatorio and not normalizado:
        raise ErroGestaoDesenvolvimento("CAMPO_OBRIGATORIO", f"{nome} deve ser preenchido.")
    if len(normalizado) > limite:
        raise ErroGestaoDesenvolvimento("CAMPO_LONGO", f"{nome} excede {limite} caracteres.")
    return normalizado or None


def _catalogo(nome: str, valor: Any, permitidos: frozenset[str]) -> str:
    if not isinstance(valor, str) or valor.strip().upper() not in permitidos:
        raise ErroGestaoDesenvolvimento("VALOR_INVALIDO", f"{nome} possui valor inválido.")
    return valor.strip().upper()


def _data(valor: Any) -> date:
    if not isinstance(valor, str):
        raise ErroGestaoDesenvolvimento("CAMPO_OBRIGATORIO", "data_registro deve ser preenchida.")
    try:
        return date.fromisoformat(valor.strip())
    except ValueError:
        raise ErroGestaoDesenvolvimento("DATA_INVALIDA", "data_registro deve ser uma data válida.") from None


@dataclass(frozen=True, slots=True)
class DadosManutencao:
    tipo: str
    titulo: str
    data_registro: date
    descricao: str
    status_trabalho: str
    status_publicacao: str
    pagina_origem: str | None
    observacao_publicacao: str | None

    @classmethod
    def validar(cls, dados: Mapping[str, Any]) -> "DadosManutencao":
        if not isinstance(dados, Mapping):
            raise ErroGestaoDesenvolvimento("JSON_INVALIDO", "Os dados devem formar um objeto.")
        desconhecidos = set(dados) - CAMPOS_MUTAVEIS
        if desconhecidos:
            raise ErroGestaoDesenvolvimento("CAMPOS_DESCONHECIDOS", "Há campos não reconhecidos.")
        resultado = cls(
            tipo=_catalogo("tipo", dados.get("tipo", "NAO_CLASSIFICADO"), TIPOS),
            titulo=_texto("titulo", dados.get("titulo"), 200, True),
            data_registro=_data(dados.get("data_registro")),
            descricao=_texto("descricao", dados.get("descricao"), 20_000, True),
            status_trabalho=_catalogo("status_trabalho", dados.get("status_trabalho", "NAO_INICIADO"), STATUS_TRABALHO),
            status_publicacao=_catalogo("status_publicacao", dados.get("status_publicacao", "NAO_APLICAVEL"), STATUS_PUBLICACAO),
            pagina_origem=_texto("pagina_origem", dados.get("pagina_origem"), 300, False),
            observacao_publicacao=_texto("observacao_publicacao", dados.get("observacao_publicacao"), 10_000, False),
        )
        if resultado.status_publicacao == "FALHA_PUBLICACAO" and not resultado.observacao_publicacao:
            raise ErroGestaoDesenvolvimento("FALHA_SEM_OBSERVACAO", "Explique a falha de publicação.")
        return resultado

    def como_dict(self) -> dict[str, str | date | None]:
        return {nome: getattr(self, nome) for nome in CAMPOS_MUTAVEIS}
