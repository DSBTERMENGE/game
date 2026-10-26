"""Gera exclusivamente as pequenas planilhas controladas do Item 3.1."""

from datetime import datetime
from pathlib import Path

from openpyxl import Workbook


PASTA = Path(__file__).resolve().parent
CABECALHO = ["Concurso", "Data", "bola 1", "bola 2", "bola 3", "bola 4", "bola 5", "bola 6"]
METADADO_FIXO = datetime(2026, 1, 1, 0, 0, 0)


def salvar(nome: str, linhas: list[list[object]], cabecalho: list[str] | None = CABECALHO) -> None:
    destino = PASTA / nome
    if destino.parent != PASTA:
        raise ValueError("A planilha deve ser criada dentro da pasta de fixtures.")

    pasta = Workbook()
    folha = pasta.active
    folha.title = "resultados"
    pasta.properties.created = METADADO_FIXO
    pasta.properties.modified = METADADO_FIXO

    for texto in ("Resultados controlados para testes", "", "", "", "", ""):
        folha.append([texto])
    if cabecalho is not None:
        folha.append(cabecalho)
    for linha in linhas:
        folha.append(linha)

    pasta.save(destino)
    pasta.close()


def main() -> None:
    salvar("resultados_validos.xlsx", [
        [100, datetime(2026, 1, 3), 1, 10, 20, 30, 40, 60],
        [101, datetime(2026, 1, 6), 2, 11, 21, 31, 41, 59],
    ])
    salvar("sem_cabecalho.xlsx", [
        [100, datetime(2026, 1, 3), 1, 10, 20, 30, 40, 60],
    ], ["Número", "Dia", "A", "B", "C", "D", "E", "F"])
    salvar("linha_invalida.xlsx", [
        [100, datetime(2026, 1, 3), 1, 10, 20, 30, 40, 60],
        [101, "data inválida", 2, 2, 21, 31, 41, 61],
    ])
    salvar("linhas_repetidas.xlsx", [
        [100, datetime(2026, 1, 3), 1, 10, 20, 30, 40, 60],
        [100, datetime(2026, 1, 3), 1, 10, 20, 30, 40, 60],
    ])
    salvar("base_existente.xlsx", [
        [100, datetime(2026, 1, 3), 1, 10, 20, 30, 40, 60],
        [101, datetime(2026, 1, 6), 2, 11, 21, 31, 41, 59],
    ])
    salvar("linha_existente_alterada.xlsx", [
        [100, datetime(2026, 1, 3), 1, 10, 20, 30, 40, 60],
        [101, datetime(2026, 1, 6), 3, 12, 22, 32, 42, 58],
        [102, datetime(2026, 1, 8), 4, 13, 23, 33, 43, 57],
    ])


if __name__ == "__main__":
    main()
