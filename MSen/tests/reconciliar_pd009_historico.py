"""Reconcilia PD_009 com o histórico local sem realizar escrita."""

import json
from dotenv import load_dotenv

from msen.config import carregar_configuracao_banco
from msen.database import abrir_conexao
from msen.modelos import ResultadoEntrada
from msen.padroes import calcular_estatistica_padrao, detectar_mais_de_tres_dezenas_na_mesma_linha


def main() -> None:
    """Compara o recálculo de PD_009 com os valores persistidos."""

    load_dotenv()
    with abrir_conexao(carregar_configuracao_banco()) as conexao:
        with conexao.cursor() as cursor:
            cursor.execute(
                "SELECT data_resultado, numero_ap, res_01, res_02, res_03, "
                "res_04, res_05, res_06 FROM resultados ORDER BY numero_ap"
            )
            resultados = tuple(ResultadoEntrada(*linha) for linha in cursor.fetchall())
            cursor.execute(
                "SELECT num_oco, intervalo_medio, desv_padrao FROM "
                "padroes_subgrupo WHERE padrao_cod = 'PD_009'"
            )
            persistido = cursor.fetchone()

    calculado = calcular_estatistica_padrao(
        "PD_009", detectar_mais_de_tres_dezenas_na_mesma_linha, resultados
    )
    esperado = (calculado.num_oco, calculado.intervalo_medio, calculado.desv_padrao)
    saida = {
        "criterio": "PD_009",
        "total_resultados": len(resultados),
        "primeira_ocorrencia": calculado.ocorrencias[0],
        "ultima_ocorrencia": calculado.ocorrencias[-1],
        "calculado": [str(item) for item in esperado],
        "persistido": [str(item) for item in persistido],
        "reconciliado": persistido == esperado,
    }
    print(json.dumps(saida, ensure_ascii=False, indent=2))
    if not saida["reconciliado"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
