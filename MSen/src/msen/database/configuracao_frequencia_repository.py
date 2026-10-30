"""Persistência da configuração ativa do estudo de frequência."""

from dataclasses import dataclass
from datetime import datetime
from typing import Any

import psycopg

from msen.services.configuracao_frequencia import ConfiguracaoFrequencia


class ErroRepositorioConfiguracaoFrequencia(RuntimeError):
    def __init__(self, codigo: str, mensagem: str) -> None:
        super().__init__(mensagem)
        self.codigo = codigo


@dataclass(frozen=True, slots=True)
class ConfiguracaoFrequenciaPersistida:
    configuracao: ConfiguracaoFrequencia
    assinatura_sha256: str
    atualizado_em: datetime


COLUNAS = (
    "nome, concurso_inicial, tamanho_inicial, regra_janela, tipo_evento, "
    "metodo_faixa, parametro_faixa, unidade_parametro, regra_arredondamento, "
    "versao_calculo, assinatura_sha256, atualizado_em"
)


def _mapear(linha: tuple[Any, ...]) -> ConfiguracaoFrequenciaPersistida:
    if len(linha) != 12:
        raise ValueError("A configuração persistida deve possuir 12 colunas.")
    configuracao = ConfiguracaoFrequencia(
        nome=linha[0], concurso_inicial=linha[1], tamanho_inicial=linha[2],
        regra_janela=linha[3], tipo_evento=linha[4], metodo_faixa=linha[5],
        parametro_faixa=linha[6], unidade_parametro=linha[7],
        regra_arredondamento=linha[8], versao_calculo=linha[9],
    )
    assinatura = linha[10].strip()
    if assinatura != configuracao.assinatura_sha256:
        raise ErroRepositorioConfiguracaoFrequencia(
            "ASSINATURA_DIVERGENTE",
            "A configuração gravada não corresponde à sua assinatura SHA-256.",
        )
    return ConfiguracaoFrequenciaPersistida(configuracao, assinatura, linha[11])


class RepositorioConfiguracaoFrequencia:
    def __init__(self, conexao: psycopg.Connection) -> None:
        if not isinstance(conexao, psycopg.Connection):
            raise TypeError("O repositório exige uma conexão Psycopg válida.")
        self._conexao = conexao

    def buscar_ativa(self) -> ConfiguracaoFrequenciaPersistida:
        with self._conexao.cursor() as cursor:
            cursor.execute(
                f"SELECT {COLUNAS} FROM configuracao_frequencia_dezenas "
                "WHERE id_configuracao = 1"
            )
            linha = cursor.fetchone()
        if linha is None:
            raise ErroRepositorioConfiguracaoFrequencia(
                "CONFIGURACAO_AUSENTE", "A configuração ativa não foi encontrada."
            )
        return _mapear(linha)

    def substituir_ativa(
        self, configuracao: ConfiguracaoFrequencia
    ) -> ConfiguracaoFrequenciaPersistida:
        if not isinstance(configuracao, ConfiguracaoFrequencia):
            raise TypeError("configuracao deve ser ConfiguracaoFrequencia.")
        with self._conexao.cursor() as cursor:
            cursor.execute(
                "UPDATE configuracao_frequencia_dezenas SET nome=%s, "
                "concurso_inicial=%s, tamanho_inicial=%s, regra_janela=%s, "
                "tipo_evento=%s, metodo_faixa=%s, parametro_faixa=%s, "
                "unidade_parametro=%s, regra_arredondamento=%s, "
                "versao_calculo=%s, assinatura_sha256=%s, "
                "atualizado_em=CURRENT_TIMESTAMP WHERE id_configuracao=1",
                (
                    configuracao.nome, configuracao.concurso_inicial,
                    configuracao.tamanho_inicial, configuracao.regra_janela,
                    configuracao.tipo_evento, configuracao.metodo_faixa,
                    configuracao.parametro_faixa, configuracao.unidade_parametro,
                    configuracao.regra_arredondamento, configuracao.versao_calculo,
                    configuracao.assinatura_sha256,
                ),
            )
            if cursor.rowcount != 1:
                raise ErroRepositorioConfiguracaoFrequencia(
                    "CONFIGURACAO_AUSENTE", "A configuração ativa não foi encontrada."
                )
        return self.buscar_ativa()
