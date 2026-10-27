"""Persistência exclusiva do cadastro e das estatísticas de padrões."""

from dataclasses import dataclass
from decimal import Decimal
import re
from typing import Any

import psycopg

from msen.padroes import EstatisticaPadrao


COLUNAS_PADRAO = """
id_padrao, padrao_cod, padrao_nome, padrao_descr,
num_oco, intervalo_medio, desv_padrao
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
    """Representa uma linha validada e recuperada da tabela `padroes`."""

    id_padrao: int
    padrao_cod: str
    padrao_nome: str
    padrao_descr: str
    num_oco: int | None
    intervalo_medio: Decimal | None
    desv_padrao: Decimal | None


def _linha_para_padrao(linha: tuple[Any, ...]) -> PadraoPersistido:
    if len(linha) != 7:
        raise ValueError("A consulta de padrão deve retornar exatamente 7 colunas.")
    return PadraoPersistido(*linha)


def _validar_codigo(codigo: str) -> str:
    if not isinstance(codigo, str) or FORMATO_CODIGO.fullmatch(codigo) is None:
        raise ValueError("O código deve seguir o formato PD_001.")
    return codigo


def _validar_texto(nome: str, valor: str) -> str:
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

    def listar(self) -> tuple[PadraoPersistido, ...]:
        """Lista os padrões em ordem crescente do código estável."""

        try:
            with self._conexao.transaction():
                with self._conexao.cursor() as cursor:
                    cursor.execute(
                        f"SELECT {COLUNAS_PADRAO} FROM padroes ORDER BY padrao_cod"
                    )
                    return tuple(
                        _linha_para_padrao(linha) for linha in cursor.fetchall()
                    )
        except psycopg.Error:
            raise ErroRepositorioPadrao(
                "FALHA_LISTAGEM", "Não foi possível listar os padrões."
            ) from None

    def criar(self, padrao_nome: str, padrao_descr: str) -> PadraoPersistido:
        """Cria um cadastro com código automático que nunca será reutilizado.

        Parâmetros:
            padrao_nome: Nome curto preenchido pelo usuário.
            padrao_descr: Explicação detalhada preenchida pelo usuário.

        Retorno:
            Linha criada com estatísticas nulas e código estável.

        Regra:
            A sequência PostgreSQL pode deixar lacunas em caso de erro, mas
            nunca reaproveita o código de um padrão excluído.
        """

        nome = _validar_texto("padrao_nome", padrao_nome)
        descricao = _validar_texto("padrao_descr", padrao_descr)
        try:
            with self._conexao.transaction():
                with self._conexao.cursor() as cursor:
                    cursor.execute("SELECT NEXTVAL('padroes_codigo_seq')")
                    numero = cursor.fetchone()[0]
                    codigo = f"PD_{numero:03d}"
                    cursor.execute(
                        "INSERT INTO padroes "
                        "(padrao_cod, padrao_nome, padrao_descr) "
                        "VALUES (%s, %s, %s) "
                        f"RETURNING {COLUNAS_PADRAO}",
                        (codigo, nome, descricao),
                    )
                    return _linha_para_padrao(cursor.fetchone())
        except psycopg.errors.UniqueViolation:
            raise ErroRepositorioPadrao(
                "PADRAO_DUPLICADO", "Já existe um padrão com o nome informado."
            ) from None
        except psycopg.Error:
            raise ErroRepositorioPadrao(
                "FALHA_CADASTRO", "Não foi possível cadastrar o padrão."
            ) from None

    def atualizar_textos(
        self, padrao_cod: str, padrao_nome: str, padrao_descr: str
    ) -> PadraoPersistido:
        """Altera somente o nome e a descrição de um padrão.

        Código e estatísticas não são parâmetros desta operação e permanecem
        inalterados. Código inexistente produz erro funcional explícito.
        """

        codigo = _validar_codigo(padrao_cod)
        nome = _validar_texto("padrao_nome", padrao_nome)
        descricao = _validar_texto("padrao_descr", padrao_descr)
        try:
            with self._conexao.transaction():
                with self._conexao.cursor() as cursor:
                    cursor.execute(
                        "UPDATE padroes SET padrao_nome = %s, padrao_descr = %s "
                        "WHERE padrao_cod = %s "
                        f"RETURNING {COLUNAS_PADRAO}",
                        (nome, descricao, codigo),
                    )
                    linha = cursor.fetchone()
                    if linha is None:
                        raise ErroRepositorioPadrao(
                            "PADRAO_NAO_ENCONTRADO",
                            "O padrão não foi encontrado.",
                            padrao_cod=codigo,
                        )
                    return _linha_para_padrao(linha)
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
                    cursor.execute(
                        "DELETE FROM padroes WHERE padrao_cod = %s "
                        f"RETURNING {COLUNAS_PADRAO}",
                        (codigo,),
                    )
                    linha = cursor.fetchone()
                    if linha is None:
                        raise ErroRepositorioPadrao(
                            "PADRAO_NAO_ENCONTRADO",
                            "O padrão não foi encontrado.",
                            padrao_cod=codigo,
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
        self, padrao_cod: str, padrao_nome: str, padrao_descr: str
    ) -> PadraoPersistido:
        """Insere um cadastro ausente sem sobrescrever textos já editados.

        Parâmetros:
            padrao_cod: Código estável associado ao detector Python.
            padrao_nome: Nome inicial apresentado ao usuário.
            padrao_descr: Explicação inicial da regra.

        Retorno:
            A linha inserida ou a linha preexistente com o mesmo código.

        Regra:
            Um conflito pelo código preserva nome e descrição existentes. Outro
            conflito de unicidade é tratado como cadastro inconsistente.
        """

        codigo = _validar_codigo(padrao_cod)
        nome = _validar_texto("padrao_nome", padrao_nome)
        descricao = _validar_texto("padrao_descr", padrao_descr)
        try:
            with self._conexao.transaction():
                with self._conexao.cursor() as cursor:
                    cursor.execute(
                        "INSERT INTO padroes "
                        "(padrao_cod, padrao_nome, padrao_descr) "
                        "VALUES (%s, %s, %s) "
                        "ON CONFLICT (padrao_cod) DO NOTHING "
                        f"RETURNING {COLUNAS_PADRAO}",
                        (codigo, nome, descricao),
                    )
                    linha = cursor.fetchone()
                    if linha is None:
                        cursor.execute(
                            f"SELECT {COLUNAS_PADRAO} FROM padroes "
                            "WHERE padrao_cod = %s",
                            (codigo,),
                        )
                        linha = cursor.fetchone()
                    return _linha_para_padrao(linha)
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
                        "UPDATE padroes SET num_oco = %s, intervalo_medio = %s, "
                        "desv_padrao = %s WHERE padrao_cod = %s "
                        f"RETURNING {COLUNAS_PADRAO}",
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
                    return _linha_para_padrao(linha)
        except ErroRepositorioPadrao:
            raise
        except psycopg.Error:
            raise ErroRepositorioPadrao(
                "FALHA_ATUALIZACAO",
                "Não foi possível atualizar a estatística do padrão.",
                padrao_cod=estatistica.padrao_cod,
            ) from None
