"""Comparação incremental, em memória, entre planilha e resultados existentes."""

from collections import Counter
from collections.abc import Iterable
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path

from msen.calculos import ResultadoCalculado, calcular_resultado

from .excel import ErroLeituraExcel, ler_linhas_excel


class StatusImportacao(StrEnum):
    NOVA = "NOVA"
    IGUAL = "IGUAL"
    ALTERADA = "ALTERADA"
    INVALIDA = "INVALIDA"


@dataclass(frozen=True, slots=True)
class LinhaComparada:
    numero_linha: int
    numero_ap: object
    status: StatusImportacao
    importado: ResultadoCalculado | None = None
    existente: ResultadoCalculado | None = None
    erro: ErroLeituraExcel | None = None


@dataclass(frozen=True, slots=True)
class ComparacaoImportacao:
    linhas: tuple[LinhaComparada, ...]

    def com_status(self, status: StatusImportacao) -> tuple[LinhaComparada, ...]:
        return tuple(linha for linha in self.linhas if linha.status == status)


def _indexar_existentes(
    existentes: Iterable[ResultadoCalculado],
) -> dict[int, ResultadoCalculado]:
    indice: dict[int, ResultadoCalculado] = {}
    for resultado in existentes:
        if not isinstance(resultado, ResultadoCalculado):
            raise TypeError("Os resultados existentes devem ser ResultadoCalculado.")
        if resultado.numero_ap in indice:
            raise ValueError(f"Concurso existente duplicado: {resultado.numero_ap}.")
        indice[resultado.numero_ap] = resultado
    return indice


def _mesmos_dados_originais(
    importado: ResultadoCalculado, existente: ResultadoCalculado
) -> bool:
    return (
        importado.numero_ap == existente.numero_ap
        and importado.data_resultado == existente.data_resultado
        and importado.resultados == existente.resultados
    )


def comparar_importacao_excel(
    caminho: str | Path,
    existentes: Iterable[ResultadoCalculado],
) -> ComparacaoImportacao:
    """Classifica cada linha sem alterar a planilha nem os dados existentes."""

    linhas = ler_linhas_excel(caminho)
    indice_existentes = _indexar_existentes(existentes)
    contagens = Counter(
        linha.resultado.numero_ap for linha in linhas if linha.resultado is not None
    )
    comparadas: list[LinhaComparada] = []

    for linha in linhas:
        if linha.erro is not None:
            comparadas.append(LinhaComparada(
                linha.numero_linha, linha.numero_ap, StatusImportacao.INVALIDA,
                erro=linha.erro,
            ))
            continue

        assert linha.resultado is not None
        numero_ap = linha.resultado.numero_ap
        if contagens[numero_ap] > 1:
            erro = ErroLeituraExcel(
                "NUMERO_AP_DUPLICADO_NA_PLANILHA",
                f"O concurso {numero_ap} aparece mais de uma vez na planilha.",
                linha=linha.numero_linha, campo="numero_ap", valor=numero_ap,
            )
            comparadas.append(LinhaComparada(
                linha.numero_linha, numero_ap, StatusImportacao.INVALIDA, erro=erro,
            ))
            continue

        importado = calcular_resultado(linha.resultado)
        existente = indice_existentes.get(numero_ap)
        if existente is None:
            status = StatusImportacao.NOVA
        elif _mesmos_dados_originais(importado, existente):
            status = StatusImportacao.IGUAL
        else:
            status = StatusImportacao.ALTERADA
        comparadas.append(LinhaComparada(
            linha.numero_linha, numero_ap, status,
            importado=importado, existente=existente,
        ))

    return ComparacaoImportacao(tuple(comparadas))
