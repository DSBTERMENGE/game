"""Persistência da Gestão do desenvolvimento."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import date, datetime
import json
from typing import Any

import psycopg

from msen.services.gestao_desenvolvimento import DadosManutencao


class ErroRepositorioGestaoDesenvolvimento(RuntimeError):
    def __init__(self, codigo: str, mensagem: str) -> None:
        super().__init__(mensagem)
        self.codigo = codigo


@dataclass(frozen=True, slots=True)
class ManutencaoPersistida:
    id_manutencao: int
    tipo: str
    titulo: str
    data_registro: date
    descricao: str
    status_trabalho: str
    status_publicacao: str
    pagina_origem: str | None
    observacao_publicacao: str | None
    versao_registro: int
    criado_em: datetime
    atualizado_em: datetime
    iniciado_em: datetime | None
    concluido_em: datetime | None
    publicado_em: datetime | None
    arquivado_em: datetime | None


@dataclass(frozen=True, slots=True)
class EventoManutencaoPersistido:
    id_evento: int
    id_manutencao: int
    tipo_evento: str
    versao_registro: int
    dados: dict[str, Any]
    criado_em: datetime


COLUNAS = """id_manutencao, tipo, titulo, data_registro, descricao,
status_trabalho, status_publicacao, pagina_origem,
observacao_publicacao, versao_registro, criado_em, atualizado_em,
iniciado_em, concluido_em, publicado_em, arquivado_em"""


class RepositorioGestaoDesenvolvimento:
    def __init__(self, conexao: psycopg.Connection) -> None:
        self._conexao = conexao

    @staticmethod
    def _registro(linha: tuple[Any, ...]) -> ManutencaoPersistida:
        return ManutencaoPersistida(*linha)

    def listar(self, *, busca: str = "", tipo: str | None = None,
               status_trabalho: str | None = None,
               status_publicacao: str | None = None,
               arquivados: bool = False,
               pagina: int = 1, por_pagina: int = 20) -> tuple[tuple[ManutencaoPersistida, ...], int]:
        condicoes = ["(arquivado_em IS NOT NULL) = %s"]
        parametros: list[Any] = [arquivados]
        for coluna, valor in (("tipo", tipo),
                              ("status_trabalho", status_trabalho),
                              ("status_publicacao", status_publicacao)):
            if valor:
                condicoes.append(f"{coluna} = %s")
                parametros.append(valor)
        if busca.strip():
            condicoes.append("titulo ILIKE %s")
            parametros.append(f"%{busca.strip()}%")
        onde = " AND ".join(condicoes)
        try:
            with self._conexao.transaction(), self._conexao.cursor() as cursor:
                cursor.execute(f"SELECT COUNT(*) FROM manutencao_sistema WHERE {onde}", parametros)
                total = cursor.fetchone()[0]
                cursor.execute(
                    f"SELECT {COLUNAS} FROM manutencao_sistema WHERE {onde} "
                    "ORDER BY criado_em, id_manutencao LIMIT %s OFFSET %s",
                    parametros + [por_pagina, (pagina - 1) * por_pagina],
                )
                return tuple(self._registro(linha) for linha in cursor.fetchall()), total
        except psycopg.Error:
            raise ErroRepositorioGestaoDesenvolvimento("FALHA_LISTAGEM", "Não foi possível consultar os registros.") from None

    def consultar(self, identificador: int) -> ManutencaoPersistida:
        try:
            with self._conexao.transaction(), self._conexao.cursor() as cursor:
                cursor.execute(f"SELECT {COLUNAS} FROM manutencao_sistema WHERE id_manutencao = %s", (identificador,))
                linha = cursor.fetchone()
                if linha is None:
                    raise ErroRepositorioGestaoDesenvolvimento("NAO_ENCONTRADO", "O registro não foi encontrado.")
                return self._registro(linha)
        except ErroRepositorioGestaoDesenvolvimento:
            raise
        except psycopg.Error:
            raise ErroRepositorioGestaoDesenvolvimento("FALHA_CONSULTA", "Não foi possível consultar o registro.") from None

    def listar_historico(self, identificador: int) -> tuple[EventoManutencaoPersistido, ...]:
        try:
            with self._conexao.transaction(), self._conexao.cursor() as cursor:
                cursor.execute(
                    "SELECT id_evento, id_manutencao, tipo_evento, versao_registro, "
                    "dados_json, criado_em "
                    "FROM manutencao_sistema_historico WHERE id_manutencao = %s "
                    "ORDER BY criado_em, id_evento", (identificador,),
                )
                eventos = tuple(EventoManutencaoPersistido(*linha) for linha in cursor.fetchall())
                if not eventos:
                    cursor.execute("SELECT 1 FROM manutencao_sistema WHERE id_manutencao = %s", (identificador,))
                    if cursor.fetchone() is None:
                        raise ErroRepositorioGestaoDesenvolvimento("NAO_ENCONTRADO", "O registro não foi encontrado.")
                return eventos
        except ErroRepositorioGestaoDesenvolvimento:
            raise
        except psycopg.Error:
            raise ErroRepositorioGestaoDesenvolvimento("FALHA_HISTORICO", "Não foi possível consultar o histórico.") from None

    def criar(self, dados: DadosManutencao, chave: str) -> tuple[ManutencaoPersistida, bool]:
        valores = dados.como_dict()
        agora = datetime.now().astimezone()
        valores["iniciado_em"] = agora if dados.status_trabalho in {
            "EM_ANDAMENTO", "AGUARDANDO_VALIDACAO", "CONCLUIDO"
        } else None
        valores["concluido_em"] = agora if dados.status_trabalho == "CONCLUIDO" else None
        valores["publicado_em"] = agora if dados.status_publicacao == "PUBLICADO" else None
        try:
            with self._conexao.transaction(), self._conexao.cursor() as cursor:
                cursor.execute(f"SELECT {COLUNAS} FROM manutencao_sistema WHERE chave_idempotencia = %s", (chave,))
                existente = cursor.fetchone()
                if existente:
                    return self._registro(existente), False
                colunas = list(valores)
                cursor.execute(
                    f"INSERT INTO manutencao_sistema ({', '.join(colunas)}, chave_idempotencia) "
                    f"VALUES ({', '.join(['%s'] * (len(colunas) + 1))}) "
                    f"ON CONFLICT (chave_idempotencia) DO NOTHING RETURNING {COLUNAS}",
                    [valores[c] for c in colunas] + [chave],
                )
                linha = cursor.fetchone()
                if linha is None:
                    cursor.execute(
                        f"SELECT {COLUNAS} FROM manutencao_sistema "
                        "WHERE chave_idempotencia = %s", (chave,),
                    )
                    return self._registro(cursor.fetchone()), False
                registro = self._registro(linha)
                self._historico(cursor, registro, "CRIADO")
                return registro, True
        except psycopg.Error:
            raise ErroRepositorioGestaoDesenvolvimento("FALHA_CADASTRO", "Não foi possível criar o registro.") from None

    def atualizar(self, identificador: int, versao: int, dados: DadosManutencao) -> ManutencaoPersistida:
        valores = dados.como_dict()
        atribuicoes = [f"{campo} = %s" for campo in valores]
        atribuicoes += ["versao_registro = versao_registro + 1", "atualizado_em = CURRENT_TIMESTAMP",
                        "iniciado_em = CASE WHEN %s = 'EM_ANDAMENTO' THEN COALESCE(iniciado_em, CURRENT_TIMESTAMP) ELSE iniciado_em END",
                        "concluido_em = CASE WHEN %s = 'CONCLUIDO' THEN CURRENT_TIMESTAMP ELSE NULL END",
                        "publicado_em = CASE WHEN %s = 'PUBLICADO' THEN CURRENT_TIMESTAMP ELSE NULL END"]
        parametros = [valores[c] for c in valores] + [dados.status_trabalho, dados.status_trabalho, dados.status_publicacao, identificador, versao]
        try:
            with self._conexao.transaction(), self._conexao.cursor() as cursor:
                cursor.execute(
                    "SELECT status_trabalho, status_publicacao FROM manutencao_sistema "
                    "WHERE id_manutencao = %s AND versao_registro = %s FOR UPDATE",
                    (identificador, versao),
                )
                anterior = cursor.fetchone()
                if anterior is None:
                    cursor.execute("SELECT 1 FROM manutencao_sistema WHERE id_manutencao = %s", (identificador,))
                    codigo = "CONFLITO_VERSAO" if cursor.fetchone() else "NAO_ENCONTRADO"
                    raise ErroRepositorioGestaoDesenvolvimento(codigo, "O registro mudou ou não existe.")
                cursor.execute(
                    f"UPDATE manutencao_sistema SET {', '.join(atribuicoes)} "
                    f"WHERE id_manutencao = %s AND versao_registro = %s RETURNING {COLUNAS}", parametros,
                )
                linha = cursor.fetchone()
                if linha is None:
                    cursor.execute("SELECT 1 FROM manutencao_sistema WHERE id_manutencao = %s", (identificador,))
                    codigo = "CONFLITO_VERSAO" if cursor.fetchone() else "NAO_ENCONTRADO"
                    raise ErroRepositorioGestaoDesenvolvimento(codigo, "O registro mudou ou não existe.")
                registro = self._registro(linha)
                if anterior[0] == "CONCLUIDO" and dados.status_trabalho != "CONCLUIDO":
                    evento = "REABERTO"
                elif anterior[0] != dados.status_trabalho:
                    evento = "STATUS_ALTERADO"
                elif anterior[1] != dados.status_publicacao:
                    evento = "PUBLICACAO_ALTERADA"
                else:
                    evento = "ATUALIZADO"
                self._historico(cursor, registro, evento)
                return registro
        except ErroRepositorioGestaoDesenvolvimento:
            raise
        except psycopg.Error:
            raise ErroRepositorioGestaoDesenvolvimento("FALHA_ATUALIZACAO", "Não foi possível atualizar o registro.") from None

    def definir_arquivamento(self, identificador: int, versao: int, arquivar: bool) -> ManutencaoPersistida:
        try:
            with self._conexao.transaction(), self._conexao.cursor() as cursor:
                cursor.execute(
                    f"UPDATE manutencao_sistema SET arquivado_em = {'CURRENT_TIMESTAMP' if arquivar else 'NULL'}, "
                    "versao_registro = versao_registro + 1, atualizado_em = CURRENT_TIMESTAMP "
                    f"WHERE id_manutencao = %s AND versao_registro = %s RETURNING {COLUNAS}",
                    (identificador, versao),
                )
                linha = cursor.fetchone()
                if linha is None:
                    raise ErroRepositorioGestaoDesenvolvimento("CONFLITO_VERSAO", "O registro mudou ou não existe.")
                registro = self._registro(linha)
                self._historico(cursor, registro, "ARQUIVADO" if arquivar else "DESARQUIVADO")
                return registro
        except ErroRepositorioGestaoDesenvolvimento:
            raise
        except psycopg.Error:
            raise ErroRepositorioGestaoDesenvolvimento("FALHA_ARQUIVAMENTO", "Não foi possível alterar o arquivamento.") from None

    @staticmethod
    def _historico(cursor, registro: ManutencaoPersistida, evento: str) -> None:
        dados = asdict(registro)
        for chave, valor in tuple(dados.items()):
            if isinstance(valor, (date, datetime)):
                dados[chave] = valor.isoformat()
        cursor.execute(
            "INSERT INTO manutencao_sistema_historico "
            "(id_manutencao, tipo_evento, versao_registro, dados_json) "
            "VALUES (%s, %s, %s, %s::jsonb)",
            (registro.id_manutencao, evento, registro.versao_registro,
             json.dumps(dados, ensure_ascii=False)),
        )
