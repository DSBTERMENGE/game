"""Configuração reproduzível do estudo de frequência das dezenas."""

from __future__ import annotations

from dataclasses import dataclass, fields
from decimal import Decimal
import hashlib
import json
from typing import Any


REGRAS_JANELA = frozenset({"INICIO_FIXO_FINAL_EXPANSIVO"})
TIPOS_EVENTO = frozenset({"TODOS", "SIMPLES", "2VS", "3VS"})
METODOS_FAIXA = frozenset({"MEDIA_MAIS_MENOS_DESVIO_PADRAO"})
UNIDADES_PARAMETRO = frozenset({"MULTIPLICADOR_DESVIO_PADRAO"})
REGRAS_ARREDONDAMENTO = frozenset({"LIMITES_EXTERNOS"})


def _inteiro_positivo(nome: str, valor: int) -> int:
    if isinstance(valor, bool) or not isinstance(valor, int):
        raise TypeError(f"{nome} deve ser inteiro.")
    if valor <= 0:
        raise ValueError(f"{nome} deve ser positivo.")
    return valor


def _texto_catalogado(nome: str, valor: str, permitidos: frozenset[str]) -> str:
    if not isinstance(valor, str):
        raise TypeError(f"{nome} deve ser texto.")
    normalizado = valor.strip().upper()
    if normalizado not in permitidos:
        raise ValueError(f"{nome} inválido: {valor!r}.")
    return normalizado


def _decimal_positivo(nome: str, valor: Decimal) -> Decimal:
    if not isinstance(valor, Decimal):
        raise TypeError(f"{nome} deve ser Decimal e possuir unidade explícita.")
    if not valor.is_finite() or valor <= 0:
        raise ValueError(f"{nome} deve ser finito e positivo.")
    return valor


@dataclass(frozen=True, slots=True)
class ConfiguracaoFrequencia:
    nome: str
    concurso_inicial: int
    tamanho_inicial: int
    regra_janela: str
    tipo_evento: str
    metodo_faixa: str
    parametro_faixa: Decimal
    unidade_parametro: str
    regra_arredondamento: str
    versao_calculo: int

    def __post_init__(self) -> None:
        if not isinstance(self.nome, str) or not self.nome.strip():
            raise ValueError("nome deve ser texto preenchido.")
        object.__setattr__(self, "nome", self.nome.strip())
        object.__setattr__(self, "concurso_inicial", _inteiro_positivo(
            "concurso_inicial", self.concurso_inicial
        ))
        object.__setattr__(self, "tamanho_inicial", _inteiro_positivo(
            "tamanho_inicial", self.tamanho_inicial
        ))
        object.__setattr__(self, "regra_janela", _texto_catalogado(
            "regra_janela", self.regra_janela, REGRAS_JANELA
        ))
        object.__setattr__(self, "tipo_evento", _texto_catalogado(
            "tipo_evento", self.tipo_evento, TIPOS_EVENTO
        ))
        object.__setattr__(self, "metodo_faixa", _texto_catalogado(
            "metodo_faixa", self.metodo_faixa, METODOS_FAIXA
        ))
        object.__setattr__(self, "parametro_faixa", _decimal_positivo(
            "parametro_faixa", self.parametro_faixa
        ))
        object.__setattr__(self, "unidade_parametro", _texto_catalogado(
            "unidade_parametro", self.unidade_parametro, UNIDADES_PARAMETRO
        ))
        object.__setattr__(self, "regra_arredondamento", _texto_catalogado(
            "regra_arredondamento", self.regra_arredondamento,
            REGRAS_ARREDONDAMENTO
        ))
        object.__setattr__(self, "versao_calculo", _inteiro_positivo(
            "versao_calculo", self.versao_calculo
        ))

    def conteudo_assinavel(self) -> dict[str, int | str]:
        """Representação canônica de todos os campos que alteram o resultado."""

        return {
            "concurso_inicial": self.concurso_inicial,
            "metodo_faixa": self.metodo_faixa,
            "nome": self.nome,
            "parametro_faixa": format(self.parametro_faixa, "f"),
            "regra_arredondamento": self.regra_arredondamento,
            "regra_janela": self.regra_janela,
            "tamanho_inicial": self.tamanho_inicial,
            "tipo_evento": self.tipo_evento,
            "unidade_parametro": self.unidade_parametro,
            "versao_calculo": self.versao_calculo,
        }

    @property
    def assinatura_sha256(self) -> str:
        canonico = json.dumps(
            self.conteudo_assinavel(), ensure_ascii=False,
            sort_keys=True, separators=(",", ":"),
        ).encode("utf-8")
        return hashlib.sha256(canonico).hexdigest()


@dataclass(frozen=True, slots=True)
class DivergenciaConfiguracaoFrequencia:
    campo: str
    valor_gravado: Any
    valor_calculado: Any


def configuracao_frequencia_inicial() -> ConfiguracaoFrequencia:
    return ConfiguracaoFrequencia(
        nome="Estudo acumulado inicial",
        concurso_inicial=1,
        tamanho_inicial=500,
        regra_janela="INICIO_FIXO_FINAL_EXPANSIVO",
        tipo_evento="TODOS",
        metodo_faixa="MEDIA_MAIS_MENOS_DESVIO_PADRAO",
        parametro_faixa=Decimal("1.000000"),
        unidade_parametro="MULTIPLICADOR_DESVIO_PADRAO",
        regra_arredondamento="LIMITES_EXTERNOS",
        versao_calculo=1,
    )


def comparar_configuracoes_frequencia(
    gravada: ConfiguracaoFrequencia,
    calculada: ConfiguracaoFrequencia,
) -> tuple[DivergenciaConfiguracaoFrequencia, ...]:
    if not isinstance(gravada, ConfiguracaoFrequencia):
        raise TypeError("gravada deve ser ConfiguracaoFrequencia.")
    if not isinstance(calculada, ConfiguracaoFrequencia):
        raise TypeError("calculada deve ser ConfiguracaoFrequencia.")
    return tuple(
        DivergenciaConfiguracaoFrequencia(
            campo=campo.name,
            valor_gravado=getattr(gravada, campo.name),
            valor_calculado=getattr(calculada, campo.name),
        )
        for campo in fields(ConfiguracaoFrequencia)
        if getattr(gravada, campo.name) != getattr(calculada, campo.name)
    )
