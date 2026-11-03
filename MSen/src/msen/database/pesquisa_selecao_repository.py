"""Persistência transacional das pesquisas de seleção de dezenas."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from math import comb
import re
from typing import Any, Iterable

import psycopg
from psycopg.types.json import Jsonb

from msen.services.configuracao_selecao_dezenas import ConfiguracaoSelecaoDezenas


HASH_SHA256 = re.compile(r"[0-9a-f]{64}")
TIPOS_EXECUCAO = frozenset({"BACKTEST", "PREVISAO_FUTURA"})
SITUACOES_ALVO = frozenset({"AVALIADO", "PENDENTE", "NAO_AVALIAVEL"})
ESTADOS_AVALIACAO = frozenset({
    "SEM_BASE", "FORA_FAIXA",
    "APROVADA_RETORNADA", "APROVADA_NAO_RETORNADA",
})


class ErroRepositorioPesquisaSelecao(RuntimeError):
    def __init__(self, codigo: str, mensagem: str) -> None:
        super().__init__(mensagem)
        self.codigo = codigo


@dataclass(frozen=True, slots=True)
class ConfiguracaoSelecaoPersistida:
    id_configuracao_selecao: int
    configuracao: ConfiguracaoSelecaoDezenas
    estado: str
    criada_em: datetime
    arquivada_em: datetime | None


@dataclass(frozen=True, slots=True)
class ExecucaoSelecaoPersistida:
    id_execucao_selecao: int
    id_configuracao_selecao: int
    tipo_execucao: str
    assinatura_configuracao: str
    assinatura_resultados: str
    concurso_corte_origem: int
    concurso_alvo_inicial: int
    concurso_alvo_final: int
    estado: str
    alvos_concluidos: int
    total_alvos: int
    criada_em: datetime


@dataclass(frozen=True, slots=True)
class AvaliacaoDezenaPesquisaEntrada:
    dezena: int
    estado_avaliacao: str
    ultima_ocorrencia: int | None
    quantidade_intervalos: int
    media_intervalos: Decimal | None
    desvio_padrao: Decimal | None
    centro_original: Decimal | None
    centro_ajustado: Decimal | None
    limite_inferior_exato: Decimal | None
    limite_superior_exato: Decimal | None
    limite_inferior: int | None
    limite_superior: int | None
    distancia_normalizada: Decimal | None
    distancia_absoluta: Decimal | None
    posicao_ranking: int | None
    aprovada: bool
    retornada: bool


@dataclass(frozen=True, slots=True)
class AlvoPesquisaEntrada:
    numero_concurso_alvo: int
    numero_concurso_corte: int
    id_resultado: int | None
    situacao: str
    quantidade_configurada: int | None
    quantidade_acertos: int | None
    motivo: str | None = None


@dataclass(frozen=True, slots=True)
class AlvoPesquisaPersistido:
    id_alvo_selecao: int
    criado: bool
    quantidade_aprovada: int
    quantidade_retornada: int
    quantidade_combinacoes_brutas: int


COLUNAS_CONFIGURACAO = (
    "id_configuracao_selecao, nome, fator_k, fator_j, modo_quantidade, "
    "quantidade_dezenas, horizonte_concursos, versao_calculo, "
    "assinatura_sha256, estado, criada_em, arquivada_em"
)
COLUNAS_EXECUCAO = (
    "id_execucao_selecao, id_configuracao_selecao, tipo_execucao, "
    "assinatura_configuracao, assinatura_resultados, concurso_corte_origem, "
    "concurso_alvo_inicial, concurso_alvo_final, estado, alvos_concluidos, "
    "total_alvos, criada_em"
)


def _hash(valor: str, nome: str) -> str:
    if not isinstance(valor, str) or HASH_SHA256.fullmatch(valor) is None:
        raise ValueError(f"{nome} deve ser SHA-256 hexadecimal minúsculo.")
    return valor


def _mapear_configuracao(linha: tuple[Any, ...]) -> ConfiguracaoSelecaoPersistida:
    if linha is None:
        raise ErroRepositorioPesquisaSelecao(
            "CONFIGURACAO_NAO_ENCONTRADA",
            "A configuração da pesquisa não foi encontrada.",
        )
    if len(linha) != 12:
        raise ValueError("A configuração persistida deve possuir 12 colunas.")
    configuracao = ConfiguracaoSelecaoDezenas(
        nome=linha[1], fator_k=linha[2], fator_j=linha[3],
        modo_quantidade=linha[4], quantidade_dezenas=linha[5],
        horizonte_concursos=linha[6], versao_calculo=linha[7],
    )
    if linha[8].strip() != configuracao.assinatura_sha256:
        raise ErroRepositorioPesquisaSelecao(
            "ASSINATURA_DIVERGENTE",
            "A configuração gravada não corresponde à sua assinatura.",
        )
    return ConfiguracaoSelecaoPersistida(
        linha[0], configuracao, linha[9], linha[10], linha[11]
    )


def _mapear_execucao(linha: tuple[Any, ...]) -> ExecucaoSelecaoPersistida:
    if linha is None:
        raise ErroRepositorioPesquisaSelecao(
            "EXECUCAO_NAO_ENCONTRADA",
            "A execução da pesquisa não foi encontrada.",
        )
    if len(linha) != 12:
        raise ValueError("A execução persistida deve possuir 12 colunas.")
    return ExecucaoSelecaoPersistida(*linha)


def _quantidade_combinacoes(quantidade_retornada: int) -> int:
    return comb(quantidade_retornada, 6) if quantidade_retornada >= 6 else 0


def _validar_avaliacoes(
    avaliacoes: Iterable[AvaliacaoDezenaPesquisaEntrada],
) -> tuple[AvaliacaoDezenaPesquisaEntrada, ...]:
    itens = tuple(avaliacoes)
    if len(itens) != 60 or {item.dezena for item in itens} != set(range(1, 61)):
        raise ValueError("Cada alvo deve possuir exatamente as dezenas de 1 a 60.")
    rankings = [item.posicao_ranking for item in itens if item.posicao_ranking is not None]
    if len(rankings) != len(set(rankings)):
        raise ValueError("As posições de ranking não podem se repetir.")
    for item in itens:
        if item.estado_avaliacao not in ESTADOS_AVALIACAO:
            raise ValueError("estado_avaliacao inválido.")
        if item.retornada and not item.aprovada:
            raise ValueError("Uma dezena retornada deve estar aprovada.")
    return itens


class RepositorioPesquisaSelecao:
    def __init__(self, conexao: psycopg.Connection) -> None:
        if not isinstance(conexao, psycopg.Connection):
            raise TypeError("O repositório exige uma conexão Psycopg válida.")
        self._conexao = conexao

    def criar_ou_buscar_configuracao(
        self, configuracao: ConfiguracaoSelecaoDezenas
    ) -> ConfiguracaoSelecaoPersistida:
        if not isinstance(configuracao, ConfiguracaoSelecaoDezenas):
            raise TypeError("configuracao deve ser ConfiguracaoSelecaoDezenas.")
        try:
            with self._conexao.transaction():
                with self._conexao.cursor() as cursor:
                    cursor.execute(
                        "INSERT INTO configuracoes_pesquisa_selecao "
                        "(nome, fator_k, fator_j, modo_quantidade, "
                        "quantidade_dezenas, horizonte_concursos, "
                        "versao_calculo, assinatura_sha256) "
                        "VALUES (%s,%s,%s,%s,%s,%s,%s,%s) "
                        "ON CONFLICT (assinatura_sha256) DO NOTHING "
                        f"RETURNING {COLUNAS_CONFIGURACAO}",
                        (
                            configuracao.nome, configuracao.fator_k,
                            configuracao.fator_j, configuracao.modo_quantidade,
                            configuracao.quantidade_dezenas,
                            configuracao.horizonte_concursos,
                            configuracao.versao_calculo,
                            configuracao.assinatura_sha256,
                        ),
                    )
                    linha = cursor.fetchone()
                    if linha is None:
                        cursor.execute(
                            f"SELECT {COLUNAS_CONFIGURACAO} "
                            "FROM configuracoes_pesquisa_selecao "
                            "WHERE assinatura_sha256=%s",
                            (configuracao.assinatura_sha256,),
                        )
                        linha = cursor.fetchone()
                    return _mapear_configuracao(linha)
        except ErroRepositorioPesquisaSelecao:
            raise
        except psycopg.Error:
            raise ErroRepositorioPesquisaSelecao(
                "FALHA_CONFIGURACAO",
                "Não foi possível gravar a configuração da pesquisa.",
            ) from None

    def listar_configuracoes(self) -> tuple[ConfiguracaoSelecaoPersistida, ...]:
        try:
            with self._conexao.transaction():
                with self._conexao.cursor() as cursor:
                    cursor.execute(
                        f"SELECT {COLUNAS_CONFIGURACAO} "
                        "FROM configuracoes_pesquisa_selecao "
                        "ORDER BY criada_em, id_configuracao_selecao"
                    )
                    return tuple(_mapear_configuracao(linha) for linha in cursor.fetchall())
        except psycopg.Error:
            raise ErroRepositorioPesquisaSelecao(
                "FALHA_LISTAGEM_CONFIGURACOES",
                "Não foi possível listar as configurações da pesquisa.",
            ) from None

    def criar_ou_buscar_execucao(
        self, configuracao: ConfiguracaoSelecaoPersistida, *,
        tipo_execucao: str, assinatura_resultados: str,
        concurso_corte_origem: int, concurso_alvo_inicial: int,
        concurso_alvo_final: int,
    ) -> ExecucaoSelecaoPersistida:
        if not isinstance(configuracao, ConfiguracaoSelecaoPersistida):
            raise TypeError("configuracao deve estar persistida.")
        tipo = tipo_execucao.strip().upper() if isinstance(tipo_execucao, str) else ""
        if tipo not in TIPOS_EXECUCAO:
            raise ValueError("tipo_execucao inválido.")
        assinatura_origem = _hash(assinatura_resultados, "assinatura_resultados")
        total = concurso_alvo_final - concurso_alvo_inicial + 1
        if total <= 0:
            raise ValueError("O período de alvos é inválido.")
        config = configuracao.configuracao
        try:
            with self._conexao.transaction():
                with self._conexao.cursor() as cursor:
                    cursor.execute(
                        "INSERT INTO execucoes_pesquisa_selecao "
                        "(id_configuracao_selecao, tipo_execucao, configuracao_json, "
                        "assinatura_configuracao, assinatura_resultados, versao_calculo, "
                        "concurso_corte_origem, concurso_alvo_inicial, "
                        "concurso_alvo_final, total_alvos) "
                        "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) "
                        "ON CONFLICT (tipo_execucao, assinatura_configuracao, "
                        "assinatura_resultados, versao_calculo, concurso_alvo_inicial, "
                        "concurso_alvo_final) DO NOTHING "
                        f"RETURNING {COLUNAS_EXECUCAO}",
                        (
                            configuracao.id_configuracao_selecao, tipo,
                            Jsonb(config.conteudo_assinavel()),
                            config.assinatura_sha256, assinatura_origem,
                            config.versao_calculo, concurso_corte_origem,
                            concurso_alvo_inicial, concurso_alvo_final, total,
                        ),
                    )
                    linha = cursor.fetchone()
                    if linha is None:
                        cursor.execute(
                            f"SELECT {COLUNAS_EXECUCAO} "
                            "FROM execucoes_pesquisa_selecao WHERE "
                            "tipo_execucao=%s AND assinatura_configuracao=%s "
                            "AND assinatura_resultados=%s AND versao_calculo=%s "
                            "AND concurso_alvo_inicial=%s AND concurso_alvo_final=%s",
                            (
                                tipo, config.assinatura_sha256, assinatura_origem,
                                config.versao_calculo, concurso_alvo_inicial,
                                concurso_alvo_final,
                            ),
                        )
                        linha = cursor.fetchone()
                    return _mapear_execucao(linha)
        except psycopg.Error:
            raise ErroRepositorioPesquisaSelecao(
                "FALHA_EXECUCAO", "Não foi possível criar a execução da pesquisa."
            ) from None

    def iniciar_ou_retomar_execucao(self, id_execucao_selecao: int) -> str:
        """Inicia uma pendente ou retoma cancelada/falha sem apagar alvos."""
        try:
            with self._conexao.transaction():
                with self._conexao.cursor() as cursor:
                    cursor.execute(
                        "UPDATE execucoes_pesquisa_selecao SET "
                        "estado='EXECUTANDO', iniciada_em=COALESCE(iniciada_em,CURRENT_TIMESTAMP), "
                        "concluida_em=NULL, erro_codigo=NULL, erro_mensagem=NULL "
                        "WHERE id_execucao_selecao=%s "
                        "AND estado IN ('PENDENTE','CANCELADA','FALHA') RETURNING estado",
                        (id_execucao_selecao,),
                    )
                    linha = cursor.fetchone()
                    if linha is None:
                        cursor.execute(
                            "SELECT estado FROM execucoes_pesquisa_selecao "
                            "WHERE id_execucao_selecao=%s",
                            (id_execucao_selecao,),
                        )
                        linha = cursor.fetchone()
                    if linha is None:
                        raise ErroRepositorioPesquisaSelecao(
                            "EXECUCAO_NAO_ENCONTRADA", "A execução não foi encontrada."
                        )
                    return linha[0]
        except ErroRepositorioPesquisaSelecao:
            raise
        except psycopg.Error:
            raise ErroRepositorioPesquisaSelecao(
                "FALHA_INICIO_EXECUCAO", "Não foi possível iniciar a execução."
            ) from None

    def estado_execucao(self, id_execucao_selecao: int) -> str:
        try:
            with self._conexao.transaction():
                with self._conexao.cursor() as cursor:
                    cursor.execute(
                        "SELECT estado FROM execucoes_pesquisa_selecao "
                        "WHERE id_execucao_selecao=%s",
                        (id_execucao_selecao,),
                    )
                    linha = cursor.fetchone()
                    if linha is None:
                        raise ErroRepositorioPesquisaSelecao(
                            "EXECUCAO_NAO_ENCONTRADA", "A execução não foi encontrada."
                        )
                    return linha[0]
        except ErroRepositorioPesquisaSelecao:
            raise
        except psycopg.Error:
            raise ErroRepositorioPesquisaSelecao(
                "FALHA_ESTADO_EXECUCAO", "Não foi possível consultar a execução."
            ) from None

    def solicitar_cancelamento(self, id_execucao_selecao: int) -> bool:
        try:
            with self._conexao.transaction():
                with self._conexao.cursor() as cursor:
                    cursor.execute(
                        "UPDATE execucoes_pesquisa_selecao "
                        "SET estado='CANCELAMENTO_SOLICITADO' "
                        "WHERE id_execucao_selecao=%s AND estado='EXECUTANDO'",
                        (id_execucao_selecao,),
                    )
                    return cursor.rowcount == 1
        except psycopg.Error:
            raise ErroRepositorioPesquisaSelecao(
                "FALHA_CANCELAMENTO", "Não foi possível solicitar o cancelamento."
            ) from None

    def finalizar_cancelamento(self, id_execucao_selecao: int) -> None:
        self._finalizar_estado(id_execucao_selecao, "CANCELADA")

    def registrar_falha(
        self, id_execucao_selecao: int, codigo: str, mensagem: str
    ) -> None:
        codigo_limpo = codigo.strip()[:80]
        mensagem_limpa = mensagem.strip()
        if not codigo_limpo or not mensagem_limpa:
            raise ValueError("Código e mensagem da falha são obrigatórios.")
        try:
            with self._conexao.transaction():
                with self._conexao.cursor() as cursor:
                    cursor.execute(
                        "UPDATE execucoes_pesquisa_selecao SET estado='FALHA', "
                        "erro_codigo=%s, erro_mensagem=%s, "
                        "concluida_em=CURRENT_TIMESTAMP "
                        "WHERE id_execucao_selecao=%s "
                        "AND estado IN ('EXECUTANDO','CANCELAMENTO_SOLICITADO')",
                        (codigo_limpo, mensagem_limpa, id_execucao_selecao),
                    )
        except psycopg.Error:
            raise ErroRepositorioPesquisaSelecao(
                "FALHA_REGISTRO_ERRO", "Não foi possível registrar a falha da execução."
            ) from None

    def concluir_execucao(self, id_execucao_selecao: int) -> None:
        try:
            with self._conexao.transaction():
                with self._conexao.cursor() as cursor:
                    cursor.execute(
                        "UPDATE execucoes_pesquisa_selecao SET "
                        "estado='CONCLUIDA', concluida_em=CURRENT_TIMESTAMP "
                        "WHERE id_execucao_selecao=%s AND estado='EXECUTANDO' "
                        "AND alvos_concluidos=total_alvos",
                        (id_execucao_selecao,),
                    )
                    if cursor.rowcount != 1:
                        raise ErroRepositorioPesquisaSelecao(
                            "EXECUCAO_INCOMPLETA",
                            "A execução não pode ser concluída antes de todos os alvos.",
                        )
        except ErroRepositorioPesquisaSelecao:
            raise
        except psycopg.Error:
            raise ErroRepositorioPesquisaSelecao(
                "FALHA_CONCLUSAO", "Não foi possível concluir a execução."
            ) from None

    def _finalizar_estado(self, id_execucao_selecao: int, estado: str) -> None:
        try:
            with self._conexao.transaction():
                with self._conexao.cursor() as cursor:
                    cursor.execute(
                        "UPDATE execucoes_pesquisa_selecao SET "
                        "estado=%s, concluida_em=CURRENT_TIMESTAMP "
                        "WHERE id_execucao_selecao=%s "
                        "AND estado IN ('EXECUTANDO','CANCELAMENTO_SOLICITADO')",
                        (estado, id_execucao_selecao),
                    )
        except psycopg.Error:
            raise ErroRepositorioPesquisaSelecao(
                "FALHA_FINALIZACAO", "Não foi possível finalizar a execução."
            ) from None

    def alvos_ja_persistidos(self, id_execucao_selecao: int) -> frozenset[int]:
        try:
            with self._conexao.transaction():
                with self._conexao.cursor() as cursor:
                    cursor.execute(
                        "SELECT numero_concurso_alvo FROM alvos_pesquisa_selecao "
                        "WHERE id_execucao_selecao=%s",
                        (id_execucao_selecao,),
                    )
                    return frozenset(linha[0] for linha in cursor.fetchall())
        except psycopg.Error:
            raise ErroRepositorioPesquisaSelecao(
                "FALHA_LISTAGEM_ALVOS", "Não foi possível listar os alvos gravados."
            ) from None

    def salvar_alvo(
        self, id_execucao_selecao: int, alvo: AlvoPesquisaEntrada,
        avaliacoes: Iterable[AvaliacaoDezenaPesquisaEntrada],
    ) -> AlvoPesquisaPersistido:
        if (
            isinstance(id_execucao_selecao, bool)
            or not isinstance(id_execucao_selecao, int)
            or id_execucao_selecao <= 0
        ):
            raise ValueError("id_execucao_selecao deve ser positivo.")
        if not isinstance(alvo, AlvoPesquisaEntrada):
            raise TypeError("alvo deve ser AlvoPesquisaEntrada.")
        if alvo.situacao not in SITUACOES_ALVO:
            raise ValueError("situação do alvo inválida.")
        itens = _validar_avaliacoes(avaliacoes)
        aprovadas = sum(item.aprovada for item in itens)
        retornadas = sum(item.retornada for item in itens)
        configurada = alvo.quantidade_configurada
        if configurada is None:
            esperado = aprovadas
            limite_nao_atingido = False
        else:
            if isinstance(configurada, bool) or not 6 <= configurada <= 60:
                raise ValueError("quantidade_configurada deve ficar entre 6 e 60.")
            esperado = min(aprovadas, configurada)
            limite_nao_atingido = aprovadas < configurada
        if retornadas != esperado:
            raise ValueError("A quantidade retornada diverge da configuração.")
        if alvo.quantidade_acertos is not None and not 0 <= alvo.quantidade_acertos <= min(6, retornadas):
            raise ValueError("quantidade_acertos inválida.")
        combinacoes = _quantidade_combinacoes(retornadas)
        try:
            with self._conexao.transaction():
                with self._conexao.cursor() as cursor:
                    cursor.execute(
                        "INSERT INTO alvos_pesquisa_selecao "
                        "(id_execucao_selecao, numero_concurso_alvo, "
                        "numero_concurso_corte, id_resultado, situacao, "
                        "quantidade_configurada, quantidade_aprovada, "
                        "quantidade_retornada, limite_nao_atingido, "
                        "quantidade_acertos, classe_acerto, "
                        "quantidade_combinacoes_brutas, motivo, conferido_em) "
                        "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,"
                        "CASE WHEN %s='AVALIADO' THEN CURRENT_TIMESTAMP ELSE NULL END) "
                        "ON CONFLICT (id_execucao_selecao, numero_concurso_alvo) "
                        "DO NOTHING RETURNING id_alvo_selecao",
                        (
                            id_execucao_selecao, alvo.numero_concurso_alvo,
                            alvo.numero_concurso_corte, alvo.id_resultado,
                            alvo.situacao, configurada, aprovadas, retornadas,
                            limite_nao_atingido, alvo.quantidade_acertos,
                            alvo.quantidade_acertos, combinacoes, alvo.motivo,
                            alvo.situacao,
                        ),
                    )
                    linha = cursor.fetchone()
                    if linha is None:
                        cursor.execute(
                            "SELECT id_alvo_selecao, quantidade_aprovada, "
                            "quantidade_retornada, quantidade_combinacoes_brutas "
                            "FROM alvos_pesquisa_selecao "
                            "WHERE id_execucao_selecao=%s AND numero_concurso_alvo=%s",
                            (id_execucao_selecao, alvo.numero_concurso_alvo),
                        )
                        existente = cursor.fetchone()
                        return AlvoPesquisaPersistido(
                            existente[0], False, existente[1], existente[2], existente[3]
                        )
                    id_alvo = linha[0]
                    cursor.executemany(
                        "INSERT INTO avaliacoes_dezenas_pesquisa "
                        "(id_alvo_selecao, dezena, estado_avaliacao, "
                        "ultima_ocorrencia, quantidade_intervalos, media_intervalos, "
                        "desvio_padrao, centro_original, centro_ajustado, "
                        "limite_inferior_exato, limite_superior_exato, "
                        "limite_inferior, limite_superior, distancia_normalizada, "
                        "distancia_absoluta, posicao_ranking, aprovada, retornada) "
                        "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                        [
                            (id_alvo, item.dezena, item.estado_avaliacao,
                             item.ultima_ocorrencia, item.quantidade_intervalos,
                             item.media_intervalos, item.desvio_padrao,
                             item.centro_original, item.centro_ajustado,
                             item.limite_inferior_exato, item.limite_superior_exato,
                             item.limite_inferior, item.limite_superior,
                             item.distancia_normalizada, item.distancia_absoluta,
                             item.posicao_ranking, item.aprovada, item.retornada)
                            for item in itens
                        ],
                    )
                    cursor.execute(
                        "UPDATE execucoes_pesquisa_selecao SET "
                        "alvos_concluidos=alvos_concluidos+1 "
                        "WHERE id_execucao_selecao=%s "
                        "AND alvos_concluidos < total_alvos",
                        (id_execucao_selecao,),
                    )
                    return AlvoPesquisaPersistido(
                        id_alvo, True, aprovadas, retornadas, combinacoes
                    )
        except psycopg.Error:
            raise ErroRepositorioPesquisaSelecao(
                "FALHA_ALVO", "Não foi possível gravar o alvo da pesquisa."
            ) from None
