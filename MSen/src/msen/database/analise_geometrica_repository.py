"""Persistência das medidas geométricas individuais dos resultados."""

from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
from typing import Any

import psycopg


DOZE_CASAS = Decimal("0.000000000001")
COLUNAS_ANALISE = (
    "id_resultado, extensao_aberta, perimetro_fechado, quantidade_regioes, "
    "area_total, centro_gravidade_x, centro_gravidade_y, versao_calculo"
)


@dataclass(frozen=True, slots=True)
class AnaliseGeometricaPersistida:
    """Representa as medidas geométricas armazenadas para um resultado."""

    id_resultado: int
    extensao_aberta: Decimal
    perimetro_fechado: Decimal
    quantidade_regioes: int
    area_total: Decimal
    centro_gravidade_x: Decimal | None
    centro_gravidade_y: Decimal | None
    versao_calculo: int


def _linha_para_analise(linha: tuple[Any, ...]) -> AnaliseGeometricaPersistida:
    if len(linha) != 8:
        raise ValueError("A consulta geométrica deve retornar exatamente 8 colunas.")
    return AnaliseGeometricaPersistida(*linha)


def _decimal(nome: str, valor: Decimal | int, *, positivo: bool = False) -> Decimal:
    if isinstance(valor, bool) or not isinstance(valor, (Decimal, int)):
        raise TypeError(f"{nome} deve ser Decimal ou inteiro.")
    convertido = Decimal(valor)
    if not convertido.is_finite() or convertido < 0 or (positivo and convertido == 0):
        raise ValueError(f"{nome} possui valor inválido.")
    return convertido.quantize(DOZE_CASAS, rounding=ROUND_HALF_UP)


class RepositorioAnaliseGeometrica:
    """Consulta e grava uma análise geométrica por resultado."""

    def __init__(self, conexao: psycopg.Connection) -> None:
        """Associa o repositório a uma conexão Psycopg válida."""

        if not isinstance(conexao, psycopg.Connection):
            raise TypeError("O repositório exige uma conexão Psycopg válida.")
        self._conexao = conexao

    def buscar(self, id_resultado: int) -> AnaliseGeometricaPersistida | None:
        """Busca as medidas do resultado ou retorna nulo quando não existem.

        Args:
            id_resultado: Identificador positivo da tabela `resultados`.

        Returns:
            A análise persistida ou `None`.
        """

        if isinstance(id_resultado, bool) or not isinstance(id_resultado, int):
            raise TypeError("id_resultado deve ser inteiro.")
        if id_resultado <= 0:
            raise ValueError("id_resultado deve ser positivo.")
        with self._conexao.cursor() as cursor:
            cursor.execute(
                f"SELECT {COLUNAS_ANALISE} FROM analise_geometrica_resultado "
                "WHERE id_resultado = %s",
                (id_resultado,),
            )
            linha = cursor.fetchone()
        return None if linha is None else _linha_para_analise(linha)

    def salvar(
        self,
        id_resultado: int,
        *,
        extensao_aberta: Decimal,
        perimetro_fechado: Decimal,
        quantidade_regioes: int,
        area_total: Decimal,
        centro_gravidade_x: Decimal | None,
        centro_gravidade_y: Decimal | None,
        versao_calculo: int = 1,
    ) -> AnaliseGeometricaPersistida:
        """Insere ou substitui atomicamente as medidas calculadas.

        Args:
            id_resultado: Resultado existente ao qual pertencem as medidas.
            extensao_aberta: Soma positiva dos cinco segmentos.
            perimetro_fechado: Extensão acrescida do fechamento.
            quantidade_regioes: Número de faces limitadas encontradas.
            area_total: Soma positiva das áreas das faces.
            centro_gravidade_x: Coordenada horizontal ou nula sem área.
            centro_gravidade_y: Coordenada vertical ou nula sem área.
            versao_calculo: Versão positiva do algoritmo geométrico.

        Returns:
            As medidas persistidas, já arredondadas para doze casas.
        """

        if isinstance(id_resultado, bool) or not isinstance(id_resultado, int):
            raise TypeError("id_resultado deve ser inteiro.")
        if id_resultado <= 0:
            raise ValueError("id_resultado deve ser positivo.")
        if isinstance(quantidade_regioes, bool) or not isinstance(quantidade_regioes, int):
            raise TypeError("quantidade_regioes deve ser inteira.")
        if quantidade_regioes < 0:
            raise ValueError("quantidade_regioes não pode ser negativa.")
        if isinstance(versao_calculo, bool) or not isinstance(versao_calculo, int):
            raise TypeError("versao_calculo deve ser inteira.")
        if versao_calculo <= 0:
            raise ValueError("versao_calculo deve ser positiva.")

        extensao = _decimal("extensao_aberta", extensao_aberta, positivo=True)
        perimetro = _decimal("perimetro_fechado", perimetro_fechado, positivo=True)
        area = _decimal("area_total", area_total)
        if perimetro < extensao:
            raise ValueError("O perímetro não pode ser menor que a extensão aberta.")
        if (quantidade_regioes == 0) != (area == 0):
            raise ValueError("Quantidade de regiões e área total são incoerentes.")
        if (centro_gravidade_x is None) != (centro_gravidade_y is None):
            raise ValueError("As duas coordenadas do centro devem existir juntas.")
        if (area == 0) != (centro_gravidade_x is None):
            raise ValueError("Área e centro de gravidade são incoerentes.")

        centro_x = None if centro_gravidade_x is None else _decimal("centro_gravidade_x", centro_gravidade_x)
        centro_y = None if centro_gravidade_y is None else _decimal("centro_gravidade_y", centro_gravidade_y)
        if centro_x is not None and not Decimal(0) <= centro_x <= Decimal(9):
            raise ValueError("centro_gravidade_x deve estar entre 0 e 9.")
        if centro_y is not None and not Decimal(0) <= centro_y <= Decimal(5):
            raise ValueError("centro_gravidade_y deve estar entre 0 e 5.")

        with self._conexao.cursor() as cursor:
            cursor.execute(
                "INSERT INTO analise_geometrica_resultado "
                "(id_resultado, extensao_aberta, perimetro_fechado, "
                "quantidade_regioes, area_total, centro_gravidade_x, "
                "centro_gravidade_y, versao_calculo) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s) "
                "ON CONFLICT (id_resultado) DO UPDATE SET "
                "extensao_aberta = EXCLUDED.extensao_aberta, "
                "perimetro_fechado = EXCLUDED.perimetro_fechado, "
                "quantidade_regioes = EXCLUDED.quantidade_regioes, "
                "area_total = EXCLUDED.area_total, "
                "centro_gravidade_x = EXCLUDED.centro_gravidade_x, "
                "centro_gravidade_y = EXCLUDED.centro_gravidade_y, "
                "versao_calculo = EXCLUDED.versao_calculo, "
                "atualizado_em = CURRENT_TIMESTAMP "
                f"RETURNING {COLUNAS_ANALISE}",
                (
                    id_resultado, extensao, perimetro, quantidade_regioes, area,
                    centro_x, centro_y, versao_calculo,
                ),
            )
            return _linha_para_analise(cursor.fetchone())
