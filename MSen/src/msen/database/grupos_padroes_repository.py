"""Persistência exclusiva dos grupos conceituais de padrões."""

from dataclasses import dataclass
import re
from typing import Any

import psycopg


COLUNAS_GRUPO = "id_grupo, grupo_cod, grupo_nome, grupo_descr"
FORMATO_CODIGO_GRUPO = re.compile(r"PG_[0-9]{3,}")


class ErroRepositorioGrupoPadrao(RuntimeError):
    """Representa uma falha segura ao acessar grupos de padrões."""

    def __init__(self, codigo: str, mensagem: str, *, grupo_cod: str | None = None):
        """Cria o erro sem revelar SQL, conexão ou credenciais."""

        super().__init__(mensagem)
        self.codigo = codigo
        self.grupo_cod = grupo_cod


@dataclass(frozen=True, slots=True)
class GrupoPadraoPersistido:
    """Representa um grupo de padrões validado e recuperado do PostgreSQL."""

    id_grupo: int
    grupo_cod: str
    grupo_nome: str
    grupo_descr: str


def _linha_para_grupo(linha: tuple[Any, ...]) -> GrupoPadraoPersistido:
    """Converte as quatro colunas esperadas em um grupo persistido."""

    if len(linha) != 4:
        raise ValueError("A consulta de grupo deve retornar exatamente 4 colunas.")
    return GrupoPadraoPersistido(*linha)


def _validar_codigo_grupo(codigo: str) -> str:
    """Valida e devolve um código no formato estável PG_001."""

    if (
        not isinstance(codigo, str)
        or FORMATO_CODIGO_GRUPO.fullmatch(codigo) is None
    ):
        raise ValueError("O código do grupo deve seguir o formato PG_001.")
    return codigo


def _validar_texto_grupo(nome: str, valor: str) -> str:
    """Remove espaços externos e rejeita um texto obrigatório vazio."""

    if not isinstance(valor, str) or not valor.strip():
        raise ValueError(f"{nome} deve ser um texto preenchido.")
    return valor.strip()


class RepositorioGruposPadroes:
    """Executa o CRUD dos grupos sem misturar padrões, API ou interface."""

    def __init__(self, conexao: psycopg.Connection) -> None:
        """Associa o repositório a uma conexão Psycopg já configurada."""

        if not isinstance(conexao, psycopg.Connection):
            raise TypeError("O repositório exige uma conexão Psycopg válida.")
        self._conexao = conexao

    def listar(self) -> tuple[GrupoPadraoPersistido, ...]:
        """Lista todos os grupos em ordem crescente do código estável."""

        try:
            with self._conexao.transaction():
                with self._conexao.cursor() as cursor:
                    cursor.execute(
                        f"SELECT {COLUNAS_GRUPO} FROM padroes_grupo "
                        "ORDER BY grupo_cod"
                    )
                    return tuple(
                        _linha_para_grupo(linha) for linha in cursor.fetchall()
                    )
        except psycopg.Error:
            raise ErroRepositorioGrupoPadrao(
                "FALHA_LISTAGEM", "Não foi possível listar os grupos de padrões."
            ) from None

    def criar(self, grupo_nome: str, grupo_descr: str) -> GrupoPadraoPersistido:
        """Cria um grupo com código automático que nunca será reutilizado.

        Parâmetros:
            grupo_nome: Nome curto preenchido pelo usuário.
            grupo_descr: Explicação detalhada preenchida pelo usuário.

        Retorno:
            Grupo criado com identificador e código estáveis.
        """

        nome = _validar_texto_grupo("grupo_nome", grupo_nome)
        descricao = _validar_texto_grupo("grupo_descr", grupo_descr)
        try:
            with self._conexao.transaction():
                with self._conexao.cursor() as cursor:
                    cursor.execute("SELECT NEXTVAL('padroes_grupo_codigo_seq')")
                    numero = cursor.fetchone()[0]
                    codigo = f"PG_{numero:03d}"
                    cursor.execute(
                        "INSERT INTO padroes_grupo "
                        "(grupo_cod, grupo_nome, grupo_descr) "
                        "VALUES (%s, %s, %s) "
                        f"RETURNING {COLUNAS_GRUPO}",
                        (codigo, nome, descricao),
                    )
                    return _linha_para_grupo(cursor.fetchone())
        except psycopg.errors.UniqueViolation:
            raise ErroRepositorioGrupoPadrao(
                "GRUPO_DUPLICADO", "Já existe um grupo com o nome informado."
            ) from None
        except psycopg.Error:
            raise ErroRepositorioGrupoPadrao(
                "FALHA_CADASTRO", "Não foi possível cadastrar o grupo de padrões."
            ) from None

    def atualizar_textos(
        self, grupo_cod: str, grupo_nome: str, grupo_descr: str
    ) -> GrupoPadraoPersistido:
        """Altera somente o nome e a descrição do grupo indicado."""

        codigo = _validar_codigo_grupo(grupo_cod)
        nome = _validar_texto_grupo("grupo_nome", grupo_nome)
        descricao = _validar_texto_grupo("grupo_descr", grupo_descr)
        try:
            with self._conexao.transaction():
                with self._conexao.cursor() as cursor:
                    cursor.execute(
                        "UPDATE padroes_grupo SET grupo_nome = %s, "
                        "grupo_descr = %s WHERE grupo_cod = %s "
                        f"RETURNING {COLUNAS_GRUPO}",
                        (nome, descricao, codigo),
                    )
                    linha = cursor.fetchone()
                    if linha is None:
                        raise ErroRepositorioGrupoPadrao(
                            "GRUPO_NAO_ENCONTRADO",
                            "O grupo de padrões não foi encontrado.",
                            grupo_cod=codigo,
                        )
                    return _linha_para_grupo(linha)
        except ErroRepositorioGrupoPadrao:
            raise
        except psycopg.errors.UniqueViolation:
            raise ErroRepositorioGrupoPadrao(
                "GRUPO_DUPLICADO",
                "Já existe um grupo com o nome informado.",
                grupo_cod=codigo,
            ) from None
        except psycopg.Error:
            raise ErroRepositorioGrupoPadrao(
                "FALHA_ATUALIZACAO",
                "Não foi possível atualizar o grupo de padrões.",
                grupo_cod=codigo,
            ) from None

    def possui_padroes(self, grupo_cod: str) -> bool:
        """Informa se o grupo existente possui ao menos um padrão associado."""

        codigo = _validar_codigo_grupo(grupo_cod)
        try:
            with self._conexao.transaction():
                with self._conexao.cursor() as cursor:
                    cursor.execute(
                        "SELECT EXISTS ("
                        "SELECT 1 FROM padroes_subgrupo p "
                        "JOIN padroes_grupo g USING (id_grupo) "
                        "WHERE g.grupo_cod = %s)",
                        (codigo,),
                    )
                    possui = cursor.fetchone()[0]
                    cursor.execute(
                        "SELECT 1 FROM padroes_grupo WHERE grupo_cod = %s",
                        (codigo,),
                    )
                    if cursor.fetchone() is None:
                        raise ErroRepositorioGrupoPadrao(
                            "GRUPO_NAO_ENCONTRADO",
                            "O grupo de padrões não foi encontrado.",
                            grupo_cod=codigo,
                        )
                    return possui
        except ErroRepositorioGrupoPadrao:
            raise
        except psycopg.Error:
            raise ErroRepositorioGrupoPadrao(
                "FALHA_CONSULTA",
                "Não foi possível consultar os vínculos do grupo.",
                grupo_cod=codigo,
            ) from None

    def excluir(self, grupo_cod: str) -> GrupoPadraoPersistido:
        """Exclui um grupo vazio e rejeita grupos que ainda possuam padrões."""

        codigo = _validar_codigo_grupo(grupo_cod)
        try:
            with self._conexao.transaction():
                with self._conexao.cursor() as cursor:
                    cursor.execute(
                        "DELETE FROM padroes_grupo WHERE grupo_cod = %s "
                        f"RETURNING {COLUNAS_GRUPO}",
                        (codigo,),
                    )
                    linha = cursor.fetchone()
                    if linha is None:
                        raise ErroRepositorioGrupoPadrao(
                            "GRUPO_NAO_ENCONTRADO",
                            "O grupo de padrões não foi encontrado.",
                            grupo_cod=codigo,
                        )
                    return _linha_para_grupo(linha)
        except ErroRepositorioGrupoPadrao:
            raise
        except psycopg.errors.ForeignKeyViolation:
            raise ErroRepositorioGrupoPadrao(
                "GRUPO_EM_USO",
                "O grupo possui padrões e não pode ser excluído.",
                grupo_cod=codigo,
            ) from None
        except psycopg.Error:
            raise ErroRepositorioGrupoPadrao(
                "FALHA_EXCLUSAO",
                "Não foi possível excluir o grupo de padrões.",
                grupo_cod=codigo,
            ) from None
