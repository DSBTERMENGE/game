"""Execução protegida das funções reais contra referências independentes."""

from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP

import psycopg

from msen.modelos import ResultadoEntrada
from msen.validacao import DefinicaoCriterio, criar_registro_criterios_producao


class ErroExecucaoValidacao(RuntimeError):
    def __init__(self, codigo: str, mensagem: str) -> None:
        super().__init__(mensagem)
        self.codigo = codigo


@dataclass(frozen=True, slots=True)
class ResultadoExecucaoCriterio:
    codigo: str
    total: int
    aprovados: int
    reprovados: int
    estado: str

    @property
    def pendentes(self) -> int:
        return self.total - self.aprovados - self.reprovados


@dataclass(frozen=True, slots=True)
class RelatorioExecucaoValidacao:
    categoria: str
    total_criterios: int
    total_avaliacoes: int
    aprovadas: int
    reprovadas: int
    criterios: tuple[ResultadoExecucaoCriterio, ...]

    @property
    def pendentes(self) -> int:
        return self.total_avaliacoes - self.aprovadas - self.reprovadas


def comparar_resultado_padrao(
    *, estado_esperado: str, id_padrao_esperado: int | None,
    detectado: bool, id_padrao_criterio: int,
) -> tuple[str, int | None, str]:
    """Traduz o booleano do detector e compara com a referência protegida."""

    if not isinstance(detectado, bool):
        raise TypeError("O detector de padrão deve retornar bool.")
    if isinstance(id_padrao_criterio, bool) or not isinstance(id_padrao_criterio, int):
        raise TypeError("id_padrao_criterio deve ser inteiro.")
    if id_padrao_criterio <= 0:
        raise ValueError("id_padrao_criterio deve ser positivo.")
    if estado_esperado == "PADRAO_IDENTIFICADO":
        if id_padrao_esperado is None:
            raise ErroExecucaoValidacao(
                "REFERENCIA_INCONSISTENTE", "O padrão esperado não possui identificador."
            )
    elif estado_esperado == "SEM_CORRESPONDENCIA":
        if id_padrao_esperado is not None:
            raise ErroExecucaoValidacao(
                "REFERENCIA_INCONSISTENTE", "A ausência esperada possui identificador."
            )
    else:
        raise ErroExecucaoValidacao(
            "REFERENCIA_PENDENTE", "A avaliação não possui referência de padrão válida."
        )
    estado = "PADRAO_IDENTIFICADO" if detectado else "SEM_CORRESPONDENCIA"
    id_calculado = id_padrao_criterio if detectado else None
    aprovado = "S" if (
        estado == estado_esperado and id_calculado == id_padrao_esperado
    ) else "N"
    return estado, id_calculado, aprovado


def _decimal_calculado(valor: object) -> tuple[str, Decimal | None]:
    if valor is None:
        return "SEM_VALOR", None
    if isinstance(valor, bool) or not isinstance(valor, (int, Decimal)):
        raise TypeError("A função numérica deve retornar int, Decimal ou None.")
    decimal = Decimal(valor)
    if not decimal.is_finite():
        raise ValueError("A função numérica retornou valor não finito.")
    return "VALOR_IDENTIFICADO", decimal


def comparar_resultado_numerico(
    *, estado_esperado: str, valor_esperado: Decimal | None, valor_calculado: object,
    precisao_decimal: int | None = None,
) -> tuple[str, Decimal | None, Decimal, str]:
    """Normaliza e compara sem alterar ou recalcular a referência protegida."""

    estado_calculado, calculado = _decimal_calculado(valor_calculado)
    if estado_esperado not in {"VALOR_IDENTIFICADO", "SEM_VALOR"}:
        raise ErroExecucaoValidacao(
            "REFERENCIA_PENDENTE", "A avaliação não possui referência numérica válida."
        )
    if precisao_decimal is not None and (
        isinstance(precisao_decimal, bool) or not isinstance(precisao_decimal, int)
        or not 0 <= precisao_decimal <= 18
    ):
        raise ValueError("precisao_decimal deve estar entre 0 e 18 ou ser nula.")
    if estado_esperado == "VALOR_IDENTIFICADO":
        if valor_esperado is None:
            raise ErroExecucaoValidacao(
                "REFERENCIA_INCONSISTENTE", "A referência identificada não possui valor."
            )
        if calculado is None:
            diferenca = -valor_esperado
            iguais = False
        else:
            if precisao_decimal is None:
                esperado_comparavel, calculado_comparavel = valor_esperado, calculado
            else:
                escala = Decimal(1).scaleb(-precisao_decimal)
                esperado_comparavel = valor_esperado.quantize(
                    escala, rounding=ROUND_HALF_UP
                )
                calculado_comparavel = calculado.quantize(
                    escala, rounding=ROUND_HALF_UP
                )
            diferenca = calculado_comparavel - esperado_comparavel
            iguais = calculado_comparavel == esperado_comparavel
    else:
        if valor_esperado is not None:
            raise ErroExecucaoValidacao(
                "REFERENCIA_INCONSISTENTE", "A referência ausente possui valor."
            )
        diferenca = Decimal(0) if calculado is None else calculado
        iguais = calculado is None
    aprovado = "S" if estado_calculado == estado_esperado and iguais else "N"
    return estado_calculado, calculado, diferenca, aprovado


def _definicoes(categoria: str) -> dict[str, DefinicaoCriterio]:
    return {
        item.codigo: item
        for item in criar_registro_criterios_producao().listar()
        if item.categoria == categoria
    }


def calcular_valor_criterio(
    definicao: DefinicaoCriterio, entrada: ResultadoEntrada
) -> object:
    """Adapta o modelo validado à assinatura real de cada família de funções."""

    if not isinstance(definicao, DefinicaoCriterio):
        raise TypeError("definicao deve ser um critério registrado.")
    if not isinstance(entrada, ResultadoEntrada):
        raise TypeError("entrada deve ser um ResultadoEntrada validado.")
    if definicao.categoria == "ESTATISTICA":
        return definicao.funcao(entrada)
    if definicao.categoria == "GEOMETRIA":
        return definicao.funcao(entrada.resultados)
    raise ValueError("O adaptador numérico não executa critérios de padrão.")


def executar_criterios_numericos(
    conexao: psycopg.Connection, *, categoria: str,
    permitir_referencias_pendentes: bool = False,
) -> RelatorioExecucaoValidacao:
    """Executa atomicamente todos os critérios numéricos ativos da categoria."""

    if not isinstance(conexao, psycopg.Connection):
        raise TypeError("A execução exige uma conexão Psycopg válida.")
    if categoria not in {"ESTATISTICA", "GEOMETRIA"}:
        raise ValueError("A categoria deve ser ESTATISTICA ou GEOMETRIA.")
    if not isinstance(permitir_referencias_pendentes, bool):
        raise TypeError("permitir_referencias_pendentes deve ser booleano.")
    definicoes = _definicoes(categoria)
    resultados: list[ResultadoExecucaoCriterio] = []

    with conexao.transaction():
        with conexao.cursor() as cursor:
            cursor.execute(
                "SELECT id_criterio, codigo, assinatura_funcao FROM "
                "criterios_validacao WHERE categoria = %s AND ativo ORDER BY codigo "
                "FOR UPDATE",
                (categoria,),
            )
            criterios = cursor.fetchall()
            if not criterios or {linha[1] for linha in criterios} != set(definicoes):
                raise ErroExecucaoValidacao(
                    "CATALOGO_DIVERGENTE", "O catálogo ativo diverge do registro de produção."
                )

            for id_criterio, codigo, assinatura_banco in criterios:
                definicao = definicoes[codigo]
                if assinatura_banco.strip() != definicao.assinatura_funcao:
                    raise ErroExecucaoValidacao(
                        "ASSINATURA_DIVERGENTE",
                        f"A assinatura registrada de {codigo} não corresponde ao código atual.",
                    )
                cursor.execute(
                    "SELECT a.id_resultado, a.referencia_conferida, "
                    "a.estado_valor_esperado, a.valor_esperado, r.data_resultado, "
                    "r.numero_ap, r.res_01, r.res_02, r.res_03, r.res_04, r.res_05, "
                    "r.res_06 FROM avaliacoes_validacao a "
                    "JOIN amostras_validacao am USING (id_resultado) "
                    "JOIN resultados r USING (id_resultado) "
                    "WHERE a.id_criterio = %s AND am.ativo ORDER BY am.ordem "
                    "FOR UPDATE OF a",
                    (id_criterio,),
                )
                avaliacoes = cursor.fetchall()
                if not avaliacoes:
                    raise ErroExecucaoValidacao(
                        "AVALIACOES_AUSENTES", f"{codigo} não possui amostras ativas."
                    )
                if any(not linha[1] for linha in avaliacoes):
                    if not permitir_referencias_pendentes:
                        raise ErroExecucaoValidacao(
                            "REFERENCIA_PENDENTE",
                            f"{codigo} possui amostra ativa sem referência conferida.",
                        )
                    cursor.execute(
                        "UPDATE criterios_validacao SET estado = 'PENDENTE', "
                        "atualizado_em = CURRENT_TIMESTAMP WHERE id_criterio = %s",
                        (id_criterio,),
                    )
                    resultados.append(ResultadoExecucaoCriterio(
                        codigo, len(avaliacoes), 0, 0, "PENDENTE"
                    ))
                    continue
                aprovados = 0
                for linha in avaliacoes:
                    entrada = ResultadoEntrada.criar(
                        data_resultado=linha[4], numero_ap=linha[5], resultados=linha[6:12]
                    )
                    estado, valor, diferenca, aprovado = comparar_resultado_numerico(
                        estado_esperado=linha[2], valor_esperado=linha[3],
                        valor_calculado=calcular_valor_criterio(definicao, entrada),
                        precisao_decimal=definicao.precisao_decimal,
                    )
                    cursor.execute(
                        "UPDATE avaliacoes_validacao SET estado_valor_calculado = %s, "
                        "valor_calculado = %s, executado = TRUE, assinatura_executada = %s, "
                        "aprovado = %s, diferenca = %s, calculado_em = CURRENT_TIMESTAMP "
                        "WHERE id_resultado = %s AND id_criterio = %s",
                        (estado, valor, definicao.assinatura_funcao, aprovado, diferenca,
                         linha[0], id_criterio),
                    )
                    aprovados += aprovado == "S"
                reprovados = len(avaliacoes) - aprovados
                estado_criterio = "APROVADO" if reprovados == 0 else "REPROVADO"
                cursor.execute(
                    "UPDATE criterios_validacao SET estado = %s, atualizado_em = "
                    "CURRENT_TIMESTAMP WHERE id_criterio = %s",
                    (estado_criterio, id_criterio),
                )
                resultados.append(ResultadoExecucaoCriterio(
                    codigo, len(avaliacoes), aprovados, reprovados, estado_criterio
                ))
            cursor.execute(
                "UPDATE estado_algoritmo_selecao SET atualizado = FALSE, "
                "motivo = 'REFERENCIAS_OU_CALCULOS_PENDENTES', "
                "alterado_em = CURRENT_TIMESTAMP WHERE id_estado = 1"
            )

    return RelatorioExecucaoValidacao(
        categoria=categoria,
        total_criterios=len(resultados),
        total_avaliacoes=sum(item.total for item in resultados),
        aprovadas=sum(item.aprovados for item in resultados),
        reprovadas=sum(item.reprovados for item in resultados),
        criterios=tuple(resultados),
    )


def executar_criterios_padroes(
    conexao: psycopg.Connection, *, permitir_referencias_pendentes: bool = False,
) -> RelatorioExecucaoValidacao:
    """Executa atomicamente todos os detectores de padrões ativos."""

    if not isinstance(conexao, psycopg.Connection):
        raise TypeError("A execução exige uma conexão Psycopg válida.")
    if not isinstance(permitir_referencias_pendentes, bool):
        raise TypeError("permitir_referencias_pendentes deve ser booleano.")
    definicoes = _definicoes("PADRAO")
    resultados: list[ResultadoExecucaoCriterio] = []
    with conexao.transaction():
        with conexao.cursor() as cursor:
            cursor.execute(
                "SELECT c.id_criterio, c.codigo, c.assinatura_funcao, c.id_grupo, "
                "p.id_padrao FROM criterios_validacao c "
                "JOIN padroes_subgrupo p ON p.id_grupo = c.id_grupo "
                "AND p.padrao_cod = SUBSTRING(c.codigo FROM 5) "
                "WHERE c.categoria = 'PADRAO' AND c.ativo ORDER BY c.codigo FOR UPDATE OF c"
            )
            criterios = cursor.fetchall()
            if not criterios or {linha[1] for linha in criterios} != set(definicoes):
                raise ErroExecucaoValidacao(
                    "CATALOGO_DIVERGENTE",
                    "O catálogo de padrões diverge do registro de produção.",
                )
            for id_criterio, codigo, assinatura_banco, id_grupo, id_padrao in criterios:
                definicao = definicoes[codigo]
                if assinatura_banco.strip() != definicao.assinatura_funcao:
                    raise ErroExecucaoValidacao(
                        "ASSINATURA_DIVERGENTE",
                        f"A assinatura registrada de {codigo} não corresponde ao código atual.",
                    )
                cursor.execute(
                    "SELECT a.id_resultado, a.referencia_conferida, "
                    "a.estado_padrao_esperado, a.id_padrao_esperado, r.data_resultado, "
                    "r.numero_ap, r.res_01, r.res_02, r.res_03, r.res_04, r.res_05, "
                    "r.res_06 FROM avaliacoes_validacao a "
                    "JOIN amostras_validacao am USING (id_resultado) "
                    "JOIN resultados r USING (id_resultado) "
                    "WHERE a.id_criterio = %s AND a.id_grupo = %s AND am.ativo "
                    "ORDER BY am.ordem FOR UPDATE OF a",
                    (id_criterio, id_grupo),
                )
                avaliacoes = cursor.fetchall()
                if not avaliacoes:
                    raise ErroExecucaoValidacao(
                        "AVALIACOES_AUSENTES", f"{codigo} não possui amostras ativas."
                    )
                if any(not linha[1] for linha in avaliacoes):
                    if not permitir_referencias_pendentes:
                        raise ErroExecucaoValidacao(
                            "REFERENCIA_PENDENTE",
                            f"{codigo} possui amostra ativa sem referência conferida.",
                        )
                    cursor.execute(
                        "UPDATE criterios_validacao SET estado = 'PENDENTE', "
                        "atualizado_em = CURRENT_TIMESTAMP WHERE id_criterio = %s",
                        (id_criterio,),
                    )
                    resultados.append(ResultadoExecucaoCriterio(
                        codigo, len(avaliacoes), 0, 0, "PENDENTE"
                    ))
                    continue
                aprovados = 0
                for linha in avaliacoes:
                    entrada = ResultadoEntrada.criar(
                        data_resultado=linha[4], numero_ap=linha[5], resultados=linha[6:12]
                    )
                    estado, id_calculado, aprovado = comparar_resultado_padrao(
                        estado_esperado=linha[2], id_padrao_esperado=linha[3],
                        detectado=definicao.funcao(entrada.resultados),
                        id_padrao_criterio=id_padrao,
                    )
                    cursor.execute(
                        "UPDATE avaliacoes_validacao SET estado_padrao_calculado = %s, "
                        "id_padrao_calculado = %s, executado = TRUE, "
                        "assinatura_executada = %s, aprovado = %s, "
                        "calculado_em = CURRENT_TIMESTAMP WHERE id_resultado = %s "
                        "AND id_criterio = %s",
                        (estado, id_calculado, definicao.assinatura_funcao, aprovado,
                         linha[0], id_criterio),
                    )
                    aprovados += aprovado == "S"
                reprovados = len(avaliacoes) - aprovados
                estado_criterio = "APROVADO" if reprovados == 0 else "REPROVADO"
                cursor.execute(
                    "UPDATE criterios_validacao SET estado = %s, atualizado_em = "
                    "CURRENT_TIMESTAMP WHERE id_criterio = %s",
                    (estado_criterio, id_criterio),
                )
                resultados.append(ResultadoExecucaoCriterio(
                    codigo, len(avaliacoes), aprovados, reprovados, estado_criterio
                ))
            cursor.execute(
                "UPDATE estado_algoritmo_selecao SET atualizado = FALSE, "
                "motivo = 'REFERENCIAS_OU_CALCULOS_PENDENTES', "
                "alterado_em = CURRENT_TIMESTAMP WHERE id_estado = 1"
            )
    return RelatorioExecucaoValidacao(
        categoria="PADRAO", total_criterios=len(resultados),
        total_avaliacoes=sum(item.total for item in resultados),
        aprovadas=sum(item.aprovados for item in resultados),
        reprovadas=sum(item.reprovados for item in resultados),
        criterios=tuple(resultados),
    )
