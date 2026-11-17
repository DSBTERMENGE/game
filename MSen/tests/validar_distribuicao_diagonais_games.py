"""Compara a distribuição diagonal real com o estudo histórico anterior."""

import json
import sys

from dotenv import load_dotenv

from msen.config import carregar_configuracao_banco
from msen.database import abrir_conexao
from msen.modelos import ResultadoEntrada
from msen.padroes import criar_fotografia_historica_diagonal


TOTAL_ESPERADO = 3069
OCORRENCIAS_ESPERADAS = {
    "0D0E": 2257,
    "0D1E": 1248,
    "0D2E": 178,
    "0D3E": 7,
    "0D4E": 0,
    "0D5E": 0,
    "1D0E": 1305,
    "1D1E": 551,
    "1D2E": 79,
    "1D3E": 2,
    "1D4E": 0,
    "2D0E": 188,
    "2D1E": 59,
    "2D2E": 3,
    "2D3E": 0,
    "3D0E": 8,
    "3D1E": 2,
    "3D2E": 0,
    "4D0E": 0,
    "4D1E": 0,
    "5D0E": 0,
    "SEM_REFERENCIA_LONGA": 23,
}


def validar() -> dict[str, object]:
    """Lê `games` sem alterar dados e compara todas as categorias."""

    configuracao = carregar_configuracao_banco()
    if configuracao.nome != "games":
        raise RuntimeError("A validação exige GAME_DB_NAME=games.")
    with abrir_conexao(configuracao) as conexao, conexao.cursor() as cursor:
        cursor.execute(
            "SELECT data_resultado, numero_ap, res_01, res_02, res_03, "
            "res_04, res_05, res_06 FROM resultados ORDER BY numero_ap"
        )
        resultados = tuple(ResultadoEntrada(*linha) for linha in cursor.fetchall())

    fotografia = criar_fotografia_historica_diagonal(resultados)
    obtidas = {item.codigo: item.ocorrencias for item in fotografia.incidencias}
    if fotografia.total_resultados != TOTAL_ESPERADO:
        raise AssertionError(
            f"Total divergente: {fotografia.total_resultados} != {TOTAL_ESPERADO}."
        )
    if obtidas != OCORRENCIAS_ESPERADAS:
        divergencias = {
            codigo: {
                "esperado": OCORRENCIAS_ESPERADAS.get(codigo),
                "obtido": obtidas.get(codigo),
            }
            for codigo in sorted(set(obtidas) | set(OCORRENCIAS_ESPERADAS))
            if obtidas.get(codigo) != OCORRENCIAS_ESPERADAS.get(codigo)
        }
        raise AssertionError(f"Distribuição divergente: {divergencias!r}.")

    return {
        "identificacao_carga": fotografia.identificacao_carga,
        "versao_calculo": fotografia.versao_calculo,
        "total_resultados": fotografia.total_resultados,
        "categorias": [
            {
                "codigo": item.codigo,
                "ocorrencias": item.ocorrencias,
                "percentual": format(item.percentual, "f"),
            }
            for item in fotografia.incidencias
        ],
        "soma_ocorrencias_nao_exclusivas": sum(
            item.ocorrencias for item in fotografia.incidencias
        ),
        "comparacao_estudo_anterior": "integralmente_igual",
    }


def main() -> None:
    load_dotenv()
    if sys.argv[1:] != ["CONFIRMAR_LEITURA_GAMES"]:
        raise SystemExit(
            "Uso: validar_distribuicao_diagonais_games.py CONFIRMAR_LEITURA_GAMES"
        )
    print(json.dumps(validar(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
