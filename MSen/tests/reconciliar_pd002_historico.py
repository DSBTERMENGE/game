"""Reconcilia PD_002 com o histórico local sem realizar qualquer escrita."""

from __future__ import annotations

import json

from dotenv import load_dotenv

from msen.config import carregar_configuracao_banco
from msen.database import abrir_conexao
from msen.modelos import ResultadoEntrada
from msen.padroes import calcular_estatistica_padrao, detectar_tres_dezenas_sequenciais


def main() -> None:
    """Compara o recálculo de PD_002 com os valores persistidos."""

    load_dotenv()
    with abrir_conexao(carregar_configuracao_banco()) as conexao:
        with conexao.cursor() as cursor:
            cursor.execute(
                "SELECT data_resultado, numero_ap, res_01, res_02, res_03, "
                "res_04, res_05, res_06 FROM resultados ORDER BY numero_ap"
            )
            resultados = tuple(ResultadoEntrada(*linha) for linha in cursor.fetchall())
            cursor.execute(
                "SELECT num_oco, intervalo_medio, desv_padrao "
                "FROM padroes_subgrupo WHERE padrao_cod = 'PD_002'"
            )
            persistido = cursor.fetchone()

    calculado = calcular_estatistica_padrao(
        "PD_002", detectar_tres_dezenas_sequenciais, resultados
    )
    num_persistido, media_persistida, desvio_persistido = persistido
    comparacoes = {
        "num_oco": num_persistido == calculado.num_oco,
        "intervalo_medio": media_persistida == calculado.intervalo_medio,
        "desv_padrao": desvio_persistido == calculado.desv_padrao,
    }
    saida = {
        "criterio": "PD_002",
        "total_resultados_avaliados": len(resultados),
        "primeira_ocorrencia": calculado.ocorrencias[0],
        "ultima_ocorrencia": calculado.ocorrencias[-1],
        "calculado": {
            "num_oco": calculado.num_oco,
            "intervalo_medio": str(calculado.intervalo_medio),
            "desv_padrao_populacional": str(calculado.desv_padrao),
        },
        "persistido": {
            "num_oco": num_persistido,
            "intervalo_medio": str(media_persistida),
            "desv_padrao": str(desvio_persistido),
        },
        "comparacoes": comparacoes,
        "reconciliado": all(comparacoes.values()),
    }
    print(json.dumps(saida, ensure_ascii=False, indent=2))
    if not saida["reconciliado"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
