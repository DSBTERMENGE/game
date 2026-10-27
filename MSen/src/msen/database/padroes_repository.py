"""Persistência exclusiva do cadastro e das estatísticas de padrões."""

from dataclasses import dataclass
from decimal import Decimal
import re
from typing import Any

import psycopg

from msen.database.grupos_padroes_repository import _validar_codigo_grupo
from msen.padroes import EstatisticaPadrao


COLUNAS_PADRAO = """
p.id_padrao, p.padrao_cod, p.padrao_nome, p.padrao_descr,
p.num_oco, p.intervalo_medio, p.desv_padrao,
p.id_grupo, g.grupo_cod, g.grupo_nome
"""
FORMATO_CODIGO = re.compile(r"PD_[0-9]{3,}")


class ErroRepositorioPadrao(RuntimeError):
    """Representa uma falha segura ao acessar a tabela `padroes`."""

    def __init__(self, codigo: str, mensagem: str, *, padrao_cod: str | None = None):
        """Cria o erro sem incluir SQL, conexão ou credenciais na mensagem."""

        super().__init__(mensagem)
        self.codigo = codigo
        self.padrao_cod = padrao_cod


@dataclass(frozen=True, slots=True)
class PadraoPersistido:
    """Representa um padrão persistido e seu grupo conceitual obrigatório."""

    id_padrao: int
    padrao_cod: str
    padrao_nome: str
    padrao_descr: str
    num_oco: int | None
    intervalo_medio: Decimal | None
    desv_padrao: Decimal | None
    id_grupo: int | None = None
    grupo_cod: str | None = None
    grupo_nome: str | None = None


def _linha_para_padrao(linha: tuple[Any, ...]) -> PadraoPersistido:
    """Converte as dez colunas esperadas em um padrão persistido."""

    if len(linha) != 10:
        raise ValueError("A consulta de padrão deve retornar exatamente 10 colunas.")
    return PadraoPersistido(*linha)


def _validar_codigo(codigo: str) -> str:
    """Valida e devolve um código de padrão no formato PD_001."""

    if not isinstance(codigo, str) or FORMATO_CODIGO.fullmatch(codigo) is None:
        raise ValueError("O código deve seguir o formato PD_001.")
    return codigo


def _validar_texto(nome: str, valor: str) -> str:
    """Remove espaços externos e rejeita um texto obrigatório vazio."""

    if not isinstance(valor, str) or not valor.strip():
        raise ValueError(f"{nome} deve ser um texto preenchido.")
    return valor.strip()


class RepositorioPadroes:
    """Consulta cadastros e grava somente estatísticas calculadas pelo Python."""

    def __init__(self, conexao: psycopg.Connection) -> None:
        """Associa o repositório a uma conexão Psycopg já configurada."""

        if not isinstance(conexao, psycopg.Connection):
            raise TypeError("O repositório exige uma conexão Psycopg válida.")
        self._conexao = conexao

    @staticmethod
    def _selecionar_por_codigo(cursor, padrao_cod: str):
        """Seleciona um padrão e os dados de seu grupo usando o cursor ativo."""

        cursor.execute(
            f"SELECT {COLUNAS_PADRAO} FROM padroes_subgrupo p "
            "JOIN padroes_grupo g USING (id_grupo) WHERE p.padrao_cod = %s",
            (padrao_cod,),
        )
        return cursor.fetchone()

    @staticmethod
    def _obter_id_grupo(cursor, grupo_cod: str) -> int:
        """Obtém o identificador do grupo ou informa que ele não existe."""

        codigo = _validar_codigo_grupo(grupo_cod)
        cursor.execute(
            "SELECT id_grupo FROM padroes_grupo WHERE grupo_cod = %s", (codigo,)
        )
        linha = cursor.fetchone()
        if linha is None:
            raise ErroRepositorioPadrao(
                "GRUPO_NAO_ENCONTRADO", "O grupo de padrões não foi encontrado."
            )
        return linha[0]

    def listar(self, grupo_cod: str | None = None) -> tuple[PadraoPersistido, ...]:
        """Lista os padrões, opcionalmente limitados a um grupo válido."""

        codigo_grupo = (
            None if grupo_cod is None else _validar_codigo_grupo(grupo_cod)
        )

        try:
            with self._conexao.transaction():
                with self._conexao.cursor() as cursor:
                    consulta = (
                        f"SELECT {COLUNAS_PADRAO} FROM padroes_subgrupo p "
                        "JOIN padroes_grupo g USING (id_grupo)"
                    )
                    parametros: tuple[str, ...] = ()
                    if codigo_grupo is not None:
                        consulta += " WHERE g.grupo_cod = %s"
                        parametros = (codigo_grupo,)
                    consulta += " ORDER BY p.padrao_cod"
                    cursor.execute(consulta, parametros)
                    return tuple(
                        _linha_para_padrao(linha) for linha in cursor.fetchall()
                    )
        except psycopg.Error:
            raise ErroRepositorioPadrao(
                "FALHA_LISTAGEM", "Não foi possível listar os padrões."
            ) from None

    def criar(
        self, padrao_nome: str, padrao_descr: str, grupo_cod: str
    ) -> PadraoPersistido:
        """Cria um cadastro com código automático que nunca será reutilizado.

        Parâmetros:
            padrao_nome: Nome curto preenchido pelo usuário.
            padrao_descr: Explicação detalhada preenchida pelo usuário.
            grupo_cod: Código do grupo conceitual obrigatório.

        Retorno:
            Linha criada com estatísticas nulas e código estável.

        Regra:
            A sequência PostgreSQL pode deixar lacunas em caso de erro, mas
            nunca reaproveita o código de um padrão excluído.
        """

        nome = _validar_texto("padrao_nome", padrao_nome)
        descricao = _validar_texto("padrao_descr", padrao_descr)
        codigo_grupo = _validar_codigo_grupo(grupo_cod)
        try:
            with self._conexao.transaction():
                with self._conexao.cursor() as cursor:
                    id_grupo = self._obter_id_grupo(cursor, codigo_grupo)
                    cursor.execute("SELECT NEXTVAL('padroes_subgrupo_codigo_seq')")
                    numero = cursor.fetchone()[0]
                    codigo = f"PD_{numero:03d}"
                    cursor.execute(
                        "INSERT INTO padroes_subgrupo "
                        "(id_grupo, padrao_cod, padrao_nome, padrao_descr) "
                        "VALUES (%s, %s, %s, %s)",
                        (id_grupo, codigo, nome, descricao),
                    )
                    return _linha_para_padrao(
                        self._selecionar_por_codigo(cursor, codigo)
                    )
        except ErroRepositorioPadrao:
            raise
        except psycopg.errors.UniqueViolation:
            raise ErroRepositorioPadrao(
                "PADRAO_DUPLICADO", "Já existe um padrão com o nome informado."
            ) from None
        except psycopg.Error:
            raise ErroRepositorioPadrao(
                "FALHA_CADASTRO", "Não foi possível cadastrar o padrão."
            ) from None

    def atualizar_textos(
        self,
        padrao_cod: str,
        padrao_nome: str,
        padrao_descr: str,
        grupo_cod: str,
    ) -> PadraoPersistido:
        """Altera grupo, nome e descrição sem modificar código ou estatísticas.

        Código e estatísticas não são parâmetros desta operação e permanecem
        inalterados. Código inexistente produz erro funcional explícito.
        """

        codigo = _validar_codigo(padrao_cod)
        nome = _validar_texto("padrao_nome", padrao_nome)
        descricao = _validar_texto("padrao_descr", padrao_descr)
        codigo_grupo = _validar_codigo_grupo(grupo_cod)
        try:
            with self._conexao.transaction():
                with self._conexao.cursor() as cursor:
                    id_grupo = self._obter_id_grupo(cursor, codigo_grupo)
                    cursor.execute(
                        "UPDATE padroes_subgrupo SET id_grupo = %s, "
                        "padrao_nome = %s, padrao_descr = %s "
                        "WHERE padrao_cod = %s "
                        "RETURNING padrao_cod",
                        (id_grupo, nome, descricao, codigo),
                    )
                    linha = cursor.fetchone()
                    if linha is None:
                        raise ErroRepositorioPadrao(
                            "PADRAO_NAO_ENCONTRADO",
                            "O padrão não foi encontrado.",
                            padrao_cod=codigo,
                        )
                    return _linha_para_padrao(
                        self._selecionar_por_codigo(cursor, codigo)
                    )
        except ErroRepositorioPadrao:
            raise
        except psycopg.errors.UniqueViolation:
            raise ErroRepositorioPadrao(
                "PADRAO_DUPLICADO",
                "Já existe um padrão com o nome informado.",
                padrao_cod=codigo,
            ) from None
        except psycopg.Error:
            raise ErroRepositorioPadrao(
                "FALHA_ATUALIZACAO",
                "Não foi possível atualizar o padrão.",
                padrao_cod=codigo,
            ) from None

    def excluir(self, padrao_cod: str) -> PadraoPersistido:
        """Exclui o cadastro indicado sem reutilizar seu código no futuro."""

        codigo = _validar_codigo(padrao_cod)
        try:
            with self._conexao.transaction():
                with self._conexao.cursor() as cursor:
                    linha = self._selecionar_por_codigo(cursor, codigo)
                    if linha is None:
                        raise ErroRepositorioPadrao(
                            "PADRAO_NAO_ENCONTRADO",
                            "O padrão não foi encontrado.",
                            padrao_cod=codigo,
                        )
                    cursor.execute(
                        "DELETE FROM padroes_subgrupo WHERE padrao_cod = %s",
                        (codigo,),
                    )
                    return _linha_para_padrao(linha)
        except ErroRepositorioPadrao:
            raise
        except psycopg.Error:
            raise ErroRepositorioPadrao(
                "FALHA_EXCLUSAO",
                "Não foi possível excluir o padrão.",
                padrao_cod=codigo,
            ) from None

    def garantir_cadastro(
        self,
        padrao_cod: str,
        padrao_nome: str,
        padrao_descr: str,
        grupo_cod: str,
    ) -> PadraoPersistido:
        """Insere um cadastro ausente sem sobrescrever textos já editados.

        Parâmetros:
            padrao_cod: Código estável associado ao detector Python.
            padrao_nome: Nome inicial apresentado ao usuário.
            padrao_descr: Explicação inicial da regra.
            grupo_cod: Código do grupo conceitual obrigatório.

        Retorno:
            A linha inserida ou a linha preexistente com o mesmo código.

        Regra:
            Um conflito pelo código preserva nome e descrição existentes. Outro
            conflito de unicidade é tratado como cadastro inconsistente.
        """

        codigo = _validar_codigo(padrao_cod)
        nome = _validar_texto("padrao_nome", padrao_nome)
        descricao = _validar_texto("padrao_descr", padrao_descr)
        codigo_grupo = _validar_codigo_grupo(grupo_cod)
        try:
            with self._conexao.transaction():
                with self._conexao.cursor() as cursor:
                    id_grupo = self._obter_id_grupo(cursor, codigo_grupo)
                    cursor.execute(
                        "INSERT INTO padroes_subgrupo "
                        "(id_grupo, padrao_cod, padrao_nome, padrao_descr) "
                        "VALUES (%s, %s, %s, %s) "
                        "ON CONFLICT (padrao_cod) DO NOTHING "
                        "RETURNING padrao_cod",
                        (id_grupo, codigo, nome, descricao),
                    )
                    linha = cursor.fetchone()
                    return _linha_para_padrao(
                        self._selecionar_por_codigo(cursor, codigo)
                    )
        except ErroRepositorioPadrao:
            raise
        except psycopg.errors.UniqueViolation:
            raise ErroRepositorioPadrao(
                "CADASTRO_CONFLITANTE",
                "Já existe outro padrão com o nome informado.",
                padrao_cod=codigo,
            ) from None
        except psycopg.Error:
            raise ErroRepositorioPadrao(
                "FALHA_CADASTRO",
                "Não foi possível garantir o cadastro do padrão.",
                padrao_cod=codigo,
            ) from None

    def atualizar_estatistica(self, estatistica: EstatisticaPadrao) -> PadraoPersistido:
        """Grava somente os três campos calculados de um padrão cadastrado.

        Parâmetros:
            estatistica: Resumo produzido pelas funções históricas aprovadas.

        Retorno:
            Linha atualizada, preservando código, nome e descrição.

        Regra:
            Valores digitados pelo frontend não participam deste método. Código
            ausente gera erro explícito e não cria cadastro implicitamente.
        """

        if not isinstance(estatistica, EstatisticaPadrao):
            raise TypeError("A atualização exige uma EstatisticaPadrao.")
        try:
            with self._conexao.transaction():
                with self._conexao.cursor() as cursor:
                    cursor.execute(
                        "UPDATE padroes_subgrupo SET num_oco = %s, intervalo_medio = %s, "
                        "desv_padrao = %s WHERE padrao_cod = %s "
                        "RETURNING padrao_cod",
                        (
                            estatistica.num_oco,
                            estatistica.intervalo_medio,
                            estatistica.desv_padrao,
                            estatistica.padrao_cod,
                        ),
                    )
                    linha = cursor.fetchone()
                    if linha is None:
                        raise ErroRepositorioPadrao(
                            "PADRAO_NAO_ENCONTRADO",
                            "O padrão não está cadastrado.",
                            padrao_cod=estatistica.padrao_cod,
                        )
                    return _linha_para_padrao(
                        self._selecionar_por_codigo(
                            cursor, estatistica.padrao_cod
                        )
                    )
        except ErroRepositorioPadrao:
            raise
        except psycopg.Error:
            raise ErroRepositorioPadrao(
                "FALHA_ATUALIZACAO",
                "Não foi possível atualizar a estatística do padrão.",
                padrao_cod=estatistica.padrao_cod,
            ) from None
