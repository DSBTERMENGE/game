"""Fotografia canônica e reproduzível da configuração de uma execução."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import date, datetime
from decimal import ROUND_HALF_UP, Decimal
from hashlib import sha256
import json
from types import MappingProxyType
from typing import TypeAlias

from .contrato_extensivel import DefinicaoFamilia


ValorCanonico: TypeAlias = str | int | bool | None | tuple["ValorCanonico", ...] | Mapping[str, "ValorCanonico"]


class ErroFotografia(ValueError):
    """Indica conteúdo ambíguo ou inconsistente na fotografia."""

    def __init__(self, codigo: str, mensagem: str) -> None:
        super().__init__(mensagem)
        self.codigo = codigo


@dataclass(frozen=True, slots=True)
class FrequenciaPadraoFotografada:
    """Frequência histórica congelada de uma classe de padrão."""

    padrao_cod: str | None
    quantidade: int
    percentual: Decimal


@dataclass(frozen=True, slots=True)
class GrupoPadroesFotografado:
    """Política e perfil histórico usados por um grupo na execução."""

    grupo_cod: str
    limite_raridade: Decimal
    operador: str
    numero_ap_inicial: int
    numero_ap_final: int
    data_inicial: date
    data_final: date
    denominador: int
    frequencias: tuple[FrequenciaPadraoFotografada, ...]
    padroes_excludentes: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class FiltroFotografado:
    """Identidade, posição e parâmetros canônicos de um filtro."""

    codigo: str
    nome: str
    ordem: int
    parametros: Mapping[str, ValorCanonico]


@dataclass(frozen=True, slots=True)
class FamiliaFotografada:
    """Família ordenada sem referência ao código executável."""

    codigo: str
    nome: str
    ordem: int
    filtros: tuple[FiltroFotografado, ...]


@dataclass(frozen=True, slots=True)
class FotografiaConfiguracao:
    """Conteúdo suficiente para identificar e reproduzir uma execução."""

    versao_formato: int
    modo: str
    semente: int
    limite_combinacoes: int
    versoes_calculo: Mapping[str, int]
    familias: tuple[FamiliaFotografada, ...]
    grupos_padroes: tuple[GrupoPadroesFotografado, ...]


@dataclass(frozen=True, slots=True)
class EnvelopeFotografia:
    """Representação JSON canônica acompanhada de SHA-256 verificável."""

    conteudo_json: str
    checksum_sha256: str


def _texto(nome: str, valor: object) -> str:
    if not isinstance(valor, str) or not valor.strip():
        raise ErroFotografia("TEXTO_INVALIDO", f"{nome} deve ser preenchido.")
    return valor.strip()


def _inteiro_positivo(nome: str, valor: object, *, zero: bool = False) -> int:
    minimo = 0 if zero else 1
    if isinstance(valor, bool) or not isinstance(valor, int) or valor < minimo:
        raise ErroFotografia("INTEIRO_INVALIDO", f"{nome} possui valor inválido.")
    return valor


def _canonizar(valor: object, *, caminho: str) -> ValorCanonico:
    """Converte somente tipos determinísticos e congela estruturas aninhadas."""

    if valor is None or isinstance(valor, (str, bool, int)):
        return valor
    if isinstance(valor, Decimal):
        if not valor.is_finite():
            raise ErroFotografia("NUMERO_NAO_FINITO", f"{caminho} não é finito.")
        return format(valor, "f")
    if isinstance(valor, datetime):
        raise ErroFotografia("DATA_COM_HORARIO", f"{caminho} não aceita horário.")
    if isinstance(valor, date):
        return valor.isoformat()
    if isinstance(valor, Mapping):
        if any(not isinstance(chave, str) or not chave for chave in valor):
            raise ErroFotografia(
                "CHAVE_INVALIDA", f"{caminho} exige chaves textuais preenchidas."
            )
        itens: dict[str, ValorCanonico] = {}
        for chave in sorted(valor):
            itens[chave] = _canonizar(valor[chave], caminho=f"{caminho}.{chave}")
        return MappingProxyType(itens)
    if isinstance(valor, (tuple, list)):
        return tuple(
            _canonizar(item, caminho=f"{caminho}[{indice}]")
            for indice, item in enumerate(valor)
        )
    raise ErroFotografia(
        "TIPO_NAO_CANONICO",
        f"{caminho} usa tipo não permitido; float e coleções sem ordem são proibidos.",
    )


def criar_grupo_padroes_fotografado(
    *,
    grupo_cod: str,
    limite_raridade: Decimal | int | str,
    operador: str,
    numero_ap_inicial: int,
    numero_ap_final: int,
    data_inicial: date,
    data_final: date,
    denominador: int,
    frequencias: tuple[FrequenciaPadraoFotografada, ...],
) -> GrupoPadroesFotografado:
    """Valida o perfil e calcula a lista excludente uma única vez."""

    codigo = _texto("grupo_cod", grupo_cod)
    try:
        limite = Decimal(limite_raridade)
    except Exception as erro:
        raise ErroFotografia("LIMITE_INVALIDO", "O limite deve ser decimal.") from erro
    if not limite.is_finite() or not Decimal(0) <= limite <= Decimal(100):
        raise ErroFotografia("LIMITE_INVALIDO", "O limite deve estar entre 0 e 100.")
    if operador not in {"<", "<="}:
        raise ErroFotografia("OPERADOR_INVALIDO", "O operador deve ser < ou <=.")
    inicio = _inteiro_positivo("numero_ap_inicial", numero_ap_inicial)
    fim = _inteiro_positivo("numero_ap_final", numero_ap_final)
    total = _inteiro_positivo("denominador", denominador)
    if inicio > fim:
        raise ErroFotografia("INTERVALO_INVALIDO", "O concurso inicial supera o final.")
    if isinstance(data_inicial, datetime) or not isinstance(data_inicial, date):
        raise ErroFotografia("DATA_INVALIDA", "data_inicial deve ser date.")
    if isinstance(data_final, datetime) or not isinstance(data_final, date):
        raise ErroFotografia("DATA_INVALIDA", "data_final deve ser date.")
    if data_inicial > data_final:
        raise ErroFotografia("INTERVALO_INVALIDO", "A data inicial supera a final.")
    if not isinstance(frequencias, tuple) or not frequencias:
        raise ErroFotografia("FREQUENCIAS_AUSENTES", "Informe as frequências do grupo.")

    vistas: set[str | None] = set()
    fixas: list[FrequenciaPadraoFotografada] = []
    for item in frequencias:
        if not isinstance(item, FrequenciaPadraoFotografada):
            raise TypeError("frequencias aceita somente FrequenciaPadraoFotografada.")
        if item.padrao_cod is not None:
            _texto("padrao_cod", item.padrao_cod)
        if item.padrao_cod in vistas:
            raise ErroFotografia("PADRAO_DUPLICADO", "A classe aparece mais de uma vez.")
        vistas.add(item.padrao_cod)
        quantidade = _inteiro_positivo("quantidade", item.quantidade, zero=True)
        if quantidade > total:
            raise ErroFotografia("CONTAGEM_INVALIDA", "A frequência supera o denominador.")
        percentual = Decimal(item.percentual)
        if not percentual.is_finite() or not Decimal(0) <= percentual <= Decimal(100):
            raise ErroFotografia("PERCENTUAL_INVALIDO", "Percentual fora de 0 a 100.")
        esperado = (Decimal(quantidade) * Decimal(100) / Decimal(total)).quantize(
            Decimal("0.000001"), rounding=ROUND_HALF_UP
        )
        if percentual.quantize(Decimal("0.000001"), rounding=ROUND_HALF_UP) != esperado:
            raise ErroFotografia(
                "FREQUENCIA_DIVERGENTE", "Quantidade e percentual não reconciliam."
            )
        fixas.append(FrequenciaPadraoFotografada(item.padrao_cod, quantidade, percentual))
    if sum(item.quantidade for item in fixas) != total:
        raise ErroFotografia(
            "DENOMINADOR_DIVERGENTE", "As classes não fecham com o denominador."
        )
    comparar = (lambda valor: valor < limite) if operador == "<" else (lambda valor: valor <= limite)
    excludentes = tuple(
        sorted(
            item.padrao_cod
            for item in fixas
            if item.padrao_cod is not None and comparar(item.percentual)
        )
    )
    return GrupoPadroesFotografado(
        codigo, limite, operador, inicio, fim, data_inicial, data_final, total,
        tuple(sorted(fixas, key=lambda item: "" if item.padrao_cod is None else item.padrao_cod)),
        excludentes,
    )


def criar_fotografia_configuracao(
    *,
    familias: tuple[DefinicaoFamilia, ...],
    parametros_filtros: Mapping[str, Mapping[str, object]],
    grupos_padroes: tuple[GrupoPadroesFotografado, ...],
    versoes_calculo: Mapping[str, int],
    modo: str,
    semente: int,
    limite_combinacoes: int,
    versao_formato: int = 1,
) -> FotografiaConfiguracao:
    """Remove os avaliadores executáveis e congela somente dados reproduzíveis."""

    if not isinstance(familias, tuple) or not familias:
        raise ErroFotografia("FAMILIAS_AUSENTES", "Informe as famílias do funil.")
    if not isinstance(parametros_filtros, Mapping):
        raise TypeError("parametros_filtros deve ser um mapeamento.")
    codigos_esperados = {
        filtro.codigo for familia in familias for filtro in familia.filtros
    }
    if set(parametros_filtros) != codigos_esperados:
        raise ErroFotografia(
            "PARAMETROS_INCOMPLETOS",
            "Os parâmetros devem corresponder exatamente aos filtros do plano.",
        )
    familias_fixas = tuple(
        FamiliaFotografada(
            _texto("codigo da família", familia.codigo),
            _texto("nome da família", familia.nome),
            _inteiro_positivo("ordem da família", familia.ordem),
            tuple(
                FiltroFotografado(
                    _texto("codigo do filtro", filtro.codigo),
                    _texto("nome do filtro", filtro.nome),
                    _inteiro_positivo("ordem do filtro", filtro.ordem),
                    _canonizar(
                        parametros_filtros[filtro.codigo],
                        caminho=f"filtros.{filtro.codigo}",
                    ),
                )
                for filtro in sorted(familia.filtros, key=lambda item: item.ordem)
            ),
        )
        for familia in sorted(familias, key=lambda item: item.ordem)
    )
    versoes = _canonizar(versoes_calculo, caminho="versoes_calculo")
    if any(isinstance(valor, bool) or not isinstance(valor, int) or valor < 1 for valor in versoes_calculo.values()):
        raise ErroFotografia("VERSAO_INVALIDA", "Versões de cálculo devem ser positivas.")
    if not isinstance(versoes, Mapping):
        raise TypeError("versoes_calculo deve produzir um mapeamento.")
    codigos_grupos = [item.grupo_cod for item in grupos_padroes]
    if len(codigos_grupos) != len(set(codigos_grupos)):
        raise ErroFotografia("GRUPO_DUPLICADO", "O grupo aparece mais de uma vez.")
    return FotografiaConfiguracao(
        _inteiro_positivo("versao_formato", versao_formato),
        _texto("modo", modo),
        _inteiro_positivo("semente", semente, zero=True),
        _inteiro_positivo("limite_combinacoes", limite_combinacoes),
        versoes,
        familias_fixas,
        tuple(sorted(grupos_padroes, key=lambda item: item.grupo_cod)),
    )


def _descanonizar(valor: ValorCanonico) -> object:
    """Converte estruturas congeladas para tipos aceitos pelo codificador JSON."""

    if isinstance(valor, Mapping):
        return {chave: _descanonizar(item) for chave, item in valor.items()}
    if isinstance(valor, tuple):
        return [_descanonizar(item) for item in valor]
    return valor


def _dados_fotografia(fotografia: FotografiaConfiguracao) -> dict[str, object]:
    return {
        "versao_formato": fotografia.versao_formato,
        "modo": fotografia.modo,
        "semente": fotografia.semente,
        "limite_combinacoes": fotografia.limite_combinacoes,
        "versoes_calculo": _descanonizar(fotografia.versoes_calculo),
        "familias": [
            {
                "codigo": familia.codigo,
                "nome": familia.nome,
                "ordem": familia.ordem,
                "filtros": [
                    {
                        "codigo": filtro.codigo,
                        "nome": filtro.nome,
                        "ordem": filtro.ordem,
                        "parametros": _descanonizar(filtro.parametros),
                    }
                    for filtro in familia.filtros
                ],
            }
            for familia in fotografia.familias
        ],
        "grupos_padroes": [
            {
                "grupo_cod": grupo.grupo_cod,
                "limite_raridade": format(grupo.limite_raridade, "f"),
                "operador": grupo.operador,
                "intervalo_historico": {
                    "numero_ap_inicial": grupo.numero_ap_inicial,
                    "numero_ap_final": grupo.numero_ap_final,
                    "data_inicial": grupo.data_inicial.isoformat(),
                    "data_final": grupo.data_final.isoformat(),
                },
                "denominador": grupo.denominador,
                "frequencias": [
                    {
                        "padrao_cod": item.padrao_cod,
                        "quantidade": item.quantidade,
                        "percentual": format(item.percentual, "f"),
                    }
                    for item in grupo.frequencias
                ],
                "padroes_excludentes": list(grupo.padroes_excludentes),
            }
            for grupo in fotografia.grupos_padroes
        ],
    }


def envelopar_fotografia(fotografia: FotografiaConfiguracao) -> EnvelopeFotografia:
    """Serializa com ordem estável e calcula o checksum do conteúdo exato."""

    if not isinstance(fotografia, FotografiaConfiguracao):
        raise TypeError("É necessário fornecer FotografiaConfiguracao.")
    conteudo = json.dumps(
        _dados_fotografia(fotografia),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    return EnvelopeFotografia(conteudo, sha256(conteudo.encode("utf-8")).hexdigest())


def verificar_envelope_fotografia(envelope: EnvelopeFotografia) -> bool:
    """Confere se o JSON permanece idêntico ao conteúdo fotografado."""

    if not isinstance(envelope, EnvelopeFotografia):
        raise TypeError("É necessário fornecer EnvelopeFotografia.")
    calculado = sha256(envelope.conteudo_json.encode("utf-8")).hexdigest()
    return calculado == envelope.checksum_sha256
