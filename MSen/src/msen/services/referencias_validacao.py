"""Registro protegido de referências produzidas fora das funções aferidas."""

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation

import psycopg


ORIGENS_REFERENCIA = frozenset({"HUMANO", "IA", "TESTE_AUTOMATIZADO"})


class ErroReferenciaValidacao(RuntimeError):
    def __init__(self, codigo: str, mensagem: str) -> None:
        super().__init__(mensagem)
        self.codigo = codigo


@dataclass(frozen=True, slots=True)
class ReferenciaAprovada:
    id_resultado: int
    id_criterio: int
    codigo_criterio: str
    estado: str
    valor: Decimal | None
    id_padrao: int | None
    origem: str
    revisor: str


def _id_positivo(nome: str, valor: int) -> int:
    if isinstance(valor, bool) or not isinstance(valor, int):
        raise TypeError(f"{nome} deve ser inteiro.")
    if valor <= 0:
        raise ValueError(f"{nome} deve ser positivo.")
    return valor


def _metadados(origem: str, revisor: str, observacao: str | None):
    if origem not in ORIGENS_REFERENCIA:
        raise ValueError("origem deve ser HUMANO, IA ou TESTE_AUTOMATIZADO.")
    if not isinstance(revisor, str) or not revisor.strip():
        raise ValueError("revisor deve ser preenchido.")
    if observacao is not None and not isinstance(observacao, str):
        raise TypeError("observacao deve ser texto ou nula.")
    return origem, revisor.strip(), None if observacao is None else observacao.strip()


def _buscar_avaliacao(cursor, id_resultado: int, id_criterio: int):
    cursor.execute(
        "SELECT c.codigo, c.categoria, c.id_grupo, a.referencia_conferida "
        "FROM avaliacoes_validacao a JOIN criterios_validacao c USING (id_criterio) "
        "WHERE a.id_resultado = %s AND a.id_criterio = %s FOR UPDATE OF a",
        (id_resultado, id_criterio),
    )
    linha = cursor.fetchone()
    if linha is None:
        raise ErroReferenciaValidacao(
            "AVALIACAO_AUSENTE", "A amostra não possui o critério informado."
        )
    if linha[3]:
        raise ErroReferenciaValidacao(
            "REFERENCIA_PROTEGIDA", "A referência conferida não pode ser sobrescrita."
        )
    return linha


def aprovar_referencia_numerica(
    conexao: psycopg.Connection,
    *,
    id_resultado: int,
    id_criterio: int,
    valor: Decimal | int | str | None,
    origem: str,
    revisor: str,
    observacao: str | None = None,
) -> ReferenciaAprovada:
    """Grava e confere atomicamente um valor independente, inclusive ausente."""

    if not isinstance(conexao, psycopg.Connection):
        raise TypeError("A aprovação exige uma conexão Psycopg válida.")
    _id_positivo("id_resultado", id_resultado)
    _id_positivo("id_criterio", id_criterio)
    origem, revisor, observacao = _metadados(origem, revisor, observacao)
    if valor is None:
        decimal = None
        estado = "SEM_VALOR"
    else:
        if isinstance(valor, bool) or not isinstance(valor, (Decimal, int, str)):
            raise TypeError("valor deve ser decimal, inteiro, texto numérico ou nulo.")
        try:
            decimal = Decimal(valor)
        except (InvalidOperation, ValueError) as erro:
            raise ValueError("valor deve ser numérico e finito.") from erro
        if not decimal.is_finite():
            raise ValueError("valor deve ser numérico e finito.")
        estado = "VALOR_IDENTIFICADO"

    with conexao.transaction():
        with conexao.cursor() as cursor:
            codigo, categoria, _id_grupo, _conferida = _buscar_avaliacao(
                cursor, id_resultado, id_criterio
            )
            if categoria == "PADRAO":
                raise ErroReferenciaValidacao(
                    "TIPO_INCOMPATIVEL", "Critério de padrão exige referência de padrão."
                )
            cursor.execute(
                "UPDATE avaliacoes_validacao SET referencia_conferida = TRUE, "
                "estado_valor_esperado = %s, valor_esperado = %s, "
                "referencia_origem = %s, referencia_revisor = %s, "
                "referencia_observacao = %s, referencia_conferida_em = CURRENT_TIMESTAMP "
                "WHERE id_resultado = %s AND id_criterio = %s",
                (estado, decimal, origem, revisor, observacao, id_resultado, id_criterio),
            )
            cursor.execute(
                "UPDATE estado_algoritmo_selecao SET atualizado = FALSE, "
                "motivo = 'REFERENCIAS_OU_CALCULOS_PENDENTES', "
                "alterado_em = CURRENT_TIMESTAMP WHERE id_estado = 1"
            )
    return ReferenciaAprovada(
        id_resultado, id_criterio, codigo, estado, decimal, None, origem, revisor
    )


def aprovar_referencia_padrao(
    conexao: psycopg.Connection,
    *,
    id_resultado: int,
    id_criterio: int,
    id_padrao: int | None,
    origem: str,
    revisor: str,
    observacao: str | None = None,
) -> ReferenciaAprovada:
    """Confere detecção ou ausência do padrão específico ligado ao critério."""

    if not isinstance(conexao, psycopg.Connection):
        raise TypeError("A aprovação exige uma conexão Psycopg válida.")
    _id_positivo("id_resultado", id_resultado)
    _id_positivo("id_criterio", id_criterio)
    if id_padrao is not None:
        _id_positivo("id_padrao", id_padrao)
    origem, revisor, observacao = _metadados(origem, revisor, observacao)
    estado = "SEM_CORRESPONDENCIA" if id_padrao is None else "PADRAO_IDENTIFICADO"

    with conexao.transaction():
        with conexao.cursor() as cursor:
            codigo, categoria, id_grupo, _conferida = _buscar_avaliacao(
                cursor, id_resultado, id_criterio
            )
            if categoria != "PADRAO" or id_grupo is None:
                raise ErroReferenciaValidacao(
                    "TIPO_INCOMPATIVEL", "Critério numérico exige referência numérica."
                )
            if id_padrao is not None:
                cursor.execute(
                    "SELECT padrao_cod FROM padroes_subgrupo "
                    "WHERE id_grupo = %s AND id_padrao = %s",
                    (id_grupo, id_padrao),
                )
                linha = cursor.fetchone()
                codigo_esperado = codigo.removeprefix("PAD_")
                if linha is None or linha[0] != codigo_esperado:
                    raise ErroReferenciaValidacao(
                        "PADRAO_INCOMPATIVEL",
                        "O padrão esperado não corresponde ao detector do critério.",
                    )
            cursor.execute(
                "UPDATE avaliacoes_validacao SET referencia_conferida = TRUE, "
                "estado_padrao_esperado = %s, id_padrao_esperado = %s, "
                "referencia_origem = %s, referencia_revisor = %s, "
                "referencia_observacao = %s, referencia_conferida_em = CURRENT_TIMESTAMP "
                "WHERE id_resultado = %s AND id_criterio = %s",
                (estado, id_padrao, origem, revisor, observacao, id_resultado, id_criterio),
            )
            cursor.execute(
                "UPDATE estado_algoritmo_selecao SET atualizado = FALSE, "
                "motivo = 'REFERENCIAS_OU_CALCULOS_PENDENTES', "
                "alterado_em = CURRENT_TIMESTAMP WHERE id_estado = 1"
            )
    return ReferenciaAprovada(
        id_resultado, id_criterio, codigo, estado, None, id_padrao, origem, revisor
    )
