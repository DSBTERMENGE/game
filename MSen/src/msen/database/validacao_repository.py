"""Persistência incremental das amostras e avaliações de validação."""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Any

import psycopg


@dataclass(frozen=True, slots=True)
class AmostraValidacao:
    id_resultado: int
    ordem: int
    ativo: bool
    incluido_em: datetime
    numero_ap: int
    dezenas: tuple[int, int, int, int, int, int]


@dataclass(frozen=True, slots=True)
class AvaliacaoValidacaoDetalhada:
    id_resultado: int
    numero_ap: int
    dezenas: tuple[int, int, int, int, int, int]
    id_criterio: int
    codigo_criterio: str
    nome_criterio: str
    categoria: str
    funcao_python: str
    tipo_resultado: str
    assinatura_funcao: str
    estado_criterio: str
    grupo_codigo: str | None
    grupo_nome: str | None
    referencia_conferida: bool
    valor_esperado: Decimal | None
    valor_calculado: Decimal | None
    estado_padrao_esperado: str | None
    subgrupo_esperado_codigo: str | None
    subgrupo_esperado_nome: str | None
    estado_padrao_calculado: str | None
    subgrupo_calculado_codigo: str | None
    subgrupo_calculado_nome: str | None
    executado: bool
    aprovado: str | None


def _id_positivo(nome: str, valor: int) -> int:
    if isinstance(valor, bool) or not isinstance(valor, int):
        raise TypeError(f"{nome} deve ser inteiro.")
    if valor <= 0:
        raise ValueError(f"{nome} deve ser positivo.")
    return valor


def _linha_para_amostra(linha: tuple[Any, ...]) -> AmostraValidacao:
    if len(linha) != 11:
        raise ValueError("A consulta de amostra deve retornar exatamente 11 colunas.")
    return AmostraValidacao(
        id_resultado=linha[0],
        ordem=linha[1],
        ativo=linha[2],
        incluido_em=linha[3],
        numero_ap=linha[4],
        dezenas=(linha[5], linha[6], linha[7], linha[8], linha[9], linha[10]),
    )


def _linha_para_avaliacao(linha: tuple[Any, ...]) -> AvaliacaoValidacaoDetalhada:
    if len(linha) != 29:
        raise ValueError("A consulta de avaliação deve retornar exatamente 29 colunas.")
    return AvaliacaoValidacaoDetalhada(
        id_resultado=linha[0],
        numero_ap=linha[1],
        dezenas=(linha[2], linha[3], linha[4], linha[5], linha[6], linha[7]),
        id_criterio=linha[8],
        codigo_criterio=linha[9],
        nome_criterio=linha[10],
        categoria=linha[11],
        funcao_python=linha[12],
        tipo_resultado=linha[13],
        assinatura_funcao=linha[14].strip(),
        estado_criterio=linha[15],
        grupo_codigo=linha[16],
        grupo_nome=linha[17],
        referencia_conferida=linha[18],
        valor_esperado=linha[19],
        valor_calculado=linha[20],
        estado_padrao_esperado=linha[21],
        subgrupo_esperado_codigo=linha[22],
        subgrupo_esperado_nome=linha[23],
        estado_padrao_calculado=linha[24],
        subgrupo_calculado_codigo=linha[25],
        subgrupo_calculado_nome=linha[26],
        executado=linha[27],
        aprovado=linha[28],
    )


COLUNAS_AMOSTRA = (
    "a.id_resultado, a.ordem, a.ativo, a.incluido_em, r.numero_ap, "
    "r.res_01, r.res_02, r.res_03, r.res_04, r.res_05, r.res_06"
)

COLUNAS_AVALIACAO = (
    "a.id_resultado, r.numero_ap, r.res_01, r.res_02, r.res_03, r.res_04, "
    "r.res_05, r.res_06, c.id_criterio, c.codigo, c.nome, c.categoria, "
    "c.funcao_python, c.tipo_resultado, c.assinatura_funcao, c.estado, "
    "g.grupo_cod, g.grupo_nome, a.referencia_conferida, a.valor_esperado, "
    "a.valor_calculado, a.estado_padrao_esperado, pe.padrao_cod, pe.padrao_nome, "
    "a.estado_padrao_calculado, pc.padrao_cod, pc.padrao_nome, a.executado, "
    "a.aprovado"
)


class RepositorioValidacao:
    """Mantém amostras e a matriz incremental amostra × critério."""

    def __init__(self, conexao: psycopg.Connection) -> None:
        if not isinstance(conexao, psycopg.Connection):
            raise TypeError("O repositório exige uma conexão Psycopg válida.")
        self._conexao = conexao

    def incluir_amostra(self, id_resultado: int, ordem: int) -> AmostraValidacao:
        """Inclui uma amostra e cria avaliações pendentes dos critérios ativos."""

        _id_positivo("id_resultado", id_resultado)
        _id_positivo("ordem", ordem)
        with self._conexao.transaction():
            with self._conexao.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO amostras_validacao (id_resultado, ordem) "
                    "VALUES (%s, %s)",
                    (id_resultado, ordem),
                )
                self._inserir_avaliacoes_faltantes(cursor, id_resultado=id_resultado)
        amostra = self.buscar_amostra(id_resultado)
        if amostra is None:
            raise RuntimeError("A amostra incluída não pôde ser consultada.")
        return amostra

    def sincronizar_avaliacoes_pendentes(self) -> int:
        """Cria somente pares faltantes entre amostras e critérios ativos."""

        with self._conexao.cursor() as cursor:
            return self._inserir_avaliacoes_faltantes(cursor)

    @staticmethod
    def _inserir_avaliacoes_faltantes(
        cursor: psycopg.Cursor, *, id_resultado: int | None = None
    ) -> int:
        filtro = " AND am.id_resultado = %s" if id_resultado is not None else ""
        parametros = (id_resultado,) if id_resultado is not None else ()
        cursor.execute(
            "INSERT INTO avaliacoes_validacao "
            "(id_resultado, id_criterio, id_grupo) "
            "SELECT am.id_resultado, c.id_criterio, c.id_grupo "
            "FROM amostras_validacao am CROSS JOIN criterios_validacao c "
            "WHERE am.ativo AND c.ativo" + filtro + " "
            "ON CONFLICT (id_resultado, id_criterio) DO NOTHING",
            parametros,
        )
        return cursor.rowcount

    def desativar_amostra(self, id_resultado: int) -> bool:
        """Retira a amostra das sincronizações futuras sem apagar avaliações."""

        _id_positivo("id_resultado", id_resultado)
        with self._conexao.cursor() as cursor:
            cursor.execute(
                "UPDATE amostras_validacao SET ativo = FALSE "
                "WHERE id_resultado = %s AND ativo RETURNING id_resultado",
                (id_resultado,),
            )
            return cursor.fetchone() is not None

    def buscar_amostra(self, id_resultado: int) -> AmostraValidacao | None:
        _id_positivo("id_resultado", id_resultado)
        with self._conexao.cursor() as cursor:
            cursor.execute(
                f"SELECT {COLUNAS_AMOSTRA} FROM amostras_validacao a "
                "JOIN resultados r USING (id_resultado) WHERE a.id_resultado = %s",
                (id_resultado,),
            )
            linha = cursor.fetchone()
        return None if linha is None else _linha_para_amostra(linha)

    def listar_amostras(self, *, somente_ativas: bool = False) -> tuple[AmostraValidacao, ...]:
        if not isinstance(somente_ativas, bool):
            raise TypeError("somente_ativas deve ser booleano.")
        filtro = " WHERE a.ativo" if somente_ativas else ""
        with self._conexao.cursor() as cursor:
            cursor.execute(
                f"SELECT {COLUNAS_AMOSTRA} FROM amostras_validacao a "
                "JOIN resultados r USING (id_resultado)" + filtro + " ORDER BY a.ordem"
            )
            return tuple(_linha_para_amostra(linha) for linha in cursor.fetchall())

    def listar_avaliacoes(
        self, *, id_resultado: int | None = None
    ) -> tuple[AvaliacaoValidacaoDetalhada, ...]:
        if id_resultado is not None:
            _id_positivo("id_resultado", id_resultado)
        filtro = " WHERE a.id_resultado = %s" if id_resultado is not None else ""
        parametros = (id_resultado,) if id_resultado is not None else ()
        with self._conexao.cursor() as cursor:
            cursor.execute(
                f"SELECT {COLUNAS_AVALIACAO} FROM avaliacoes_validacao a "
                "JOIN resultados r USING (id_resultado) "
                "JOIN criterios_validacao c USING (id_criterio) "
                "LEFT JOIN padroes_grupo g ON g.id_grupo = a.id_grupo "
                "LEFT JOIN padroes_subgrupo pe ON pe.id_grupo = a.id_grupo "
                "AND pe.id_padrao = a.id_padrao_esperado "
                "LEFT JOIN padroes_subgrupo pc ON pc.id_grupo = a.id_grupo "
                "AND pc.id_padrao = a.id_padrao_calculado" + filtro + " "
                "ORDER BY r.numero_ap, c.categoria, c.codigo",
                parametros,
            )
            return tuple(_linha_para_avaliacao(linha) for linha in cursor.fetchall())
