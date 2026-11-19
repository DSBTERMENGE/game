"""Catálogo legível dos filtros executáveis da nova validação."""

from collections.abc import Callable, Iterable
from dataclasses import dataclass

import psycopg

from msen.padroes import ErroResolucaoDetector, resolver_funcao_detectora


@dataclass(frozen=True, slots=True)
class FiltroExecutavelValidacao:
    id_filtro: int
    nome: str
    descricao: str


@dataclass(frozen=True, slots=True)
class GrupoFiltrosValidacao:
    id_grupo: int
    nome: str
    filtros: tuple[FiltroExecutavelValidacao, ...]


LinhaCatalogo = tuple[int, str, int, str, str, str | None]
VerificadorFuncao = Callable[[str | None], bool]


class ErroCatalogoFiltrosValidacao(RuntimeError):
    pass


def _funcao_disponivel(nome: str | None) -> bool:
    try:
        resolver_funcao_detectora(nome)
    except ErroResolucaoDetector:
        return False
    return True


def montar_catalogo_filtros_validacao(
    linhas: Iterable[LinhaCatalogo],
    *,
    funcao_disponivel: VerificadorFuncao = _funcao_disponivel,
) -> tuple[GrupoFiltrosValidacao, ...]:
    """Agrupa somente filtros executáveis e descarta os dados técnicos."""

    if not callable(funcao_disponivel):
        raise TypeError("O verificador de função deve ser chamável.")
    grupos: dict[int, tuple[str, list[FiltroExecutavelValidacao]]] = {}
    for id_grupo, grupo, id_filtro, filtro, descricao, funcao in linhas:
        if not funcao_disponivel(funcao):
            continue
        if id_grupo <= 0 or id_filtro <= 0:
            raise ValueError("Os identificadores do catálogo devem ser positivos.")
        nome_grupo = grupo.strip()
        nome_filtro = filtro.strip()
        if not nome_grupo or not nome_filtro:
            raise ValueError("Grupo e filtro devem possuir nomes preenchidos.")
        existente = grupos.setdefault(id_grupo, (nome_grupo, []))
        if existente[0] != nome_grupo:
            raise ValueError("O mesmo grupo não pode possuir nomes divergentes.")
        existente[1].append(FiltroExecutavelValidacao(
            id_filtro=id_filtro,
            nome=nome_filtro,
            descricao=descricao.strip(),
        ))

    return tuple(
        GrupoFiltrosValidacao(
            id_grupo=id_grupo,
            nome=nome,
            filtros=tuple(sorted(filtros, key=lambda item: (item.nome.casefold(), item.id_filtro))),
        )
        for id_grupo, (nome, filtros) in sorted(
            grupos.items(), key=lambda item: (item[1][0].casefold(), item[0])
        )
    )


def carregar_catalogo_filtros_validacao(
    conexao: psycopg.Connection,
) -> tuple[GrupoFiltrosValidacao, ...]:
    """Lê IDs e textos do banco sem expor códigos ou nomes de função."""

    if not isinstance(conexao, psycopg.Connection):
        raise TypeError("O catálogo exige uma conexão Psycopg válida.")
    try:
        with conexao.transaction(), conexao.cursor() as cursor:
            cursor.execute(
                "SELECT g.id_grupo, g.grupo_nome, p.id_padrao, p.padrao_nome, "
                "p.padrao_descr, p.funcao_detectora FROM padroes_grupo g "
                "JOIN padroes_subgrupo p USING (id_grupo) "
                "ORDER BY LOWER(g.grupo_nome), g.id_grupo, "
                "LOWER(p.padrao_nome), p.id_padrao"
            )
            linhas = tuple(cursor.fetchall())
    except psycopg.Error as erro:
        raise ErroCatalogoFiltrosValidacao(
            "Não foi possível consultar os filtros disponíveis."
        ) from erro
    return montar_catalogo_filtros_validacao(linhas)
