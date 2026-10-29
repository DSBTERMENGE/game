"""Seleção dos padrões raros aptos a participar do screener."""

from dataclasses import dataclass
from decimal import Decimal

import psycopg

from msen.database import PadraoPersistido, RepositorioPadroes
from msen.database.padroes_repository import _validar_limite_percentual
from msen.padroes import criar_registro_detectores_aprovados


@dataclass(frozen=True, slots=True)
class SelecaoPadroesRaros:
    """Fotografia da consulta de raridade feita antes do screener."""

    limite_percentual: Decimal
    total_sorteios: int
    operador: str
    padroes: tuple[PadraoPersistido, ...]


def selecionar_padroes_raros(
    conexao: psycopg.Connection,
    *,
    limite_percentual: Decimal | int | str,
    total_sorteios: int,
) -> SelecaoPadroesRaros:
    """Consulta somente padrões com detector e percentual histórico menor."""

    if not isinstance(conexao, psycopg.Connection):
        raise TypeError("A seleção exige uma conexão Psycopg válida.")
    limite = _validar_limite_percentual(limite_percentual)
    registro = criar_registro_detectores_aprovados()
    padroes = RepositorioPadroes(conexao).listar_raros(
        limite, total_sorteios, registro.codigos_registrados()
    )
    return SelecaoPadroesRaros(limite, total_sorteios, "<", padroes)
