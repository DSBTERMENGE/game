"""Produz inventário somente de leitura dos padrões e detectores atuais."""

from __future__ import annotations

import json

from dotenv import load_dotenv

from msen.config import carregar_configuracao_banco
from msen.database import abrir_conexao
from msen.padroes import criar_registro_detectores_aprovados


def main() -> None:
    """Lê PostgreSQL e catálogo Python e imprime um inventário em JSON."""

    load_dotenv()
    registro = criar_registro_detectores_aprovados()
    with abrir_conexao(carregar_configuracao_banco()) as conexao:
        with conexao.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM resultados")
            total_resultados = cursor.fetchone()[0]
            cursor.execute(
                "SELECT g.grupo_cod, g.grupo_nome, p.padrao_cod, p.padrao_nome, "
                "p.num_oco, p.intervalo_medio, p.desv_padrao "
                "FROM padroes_grupo g "
                "LEFT JOIN padroes_subgrupo p USING (id_grupo) "
                "ORDER BY g.grupo_cod, p.padrao_cod"
            )
            linhas = cursor.fetchall()

    grupos: dict[str, dict[str, object]] = {}
    codigos_cadastrados: set[str] = set()
    for linha in linhas:
        grupo_cod, grupo_nome, codigo, nome, ocorrencias, intervalo, desvio = linha
        grupo = grupos.setdefault(
            grupo_cod, {"grupo_cod": grupo_cod, "grupo_nome": grupo_nome, "padroes": []}
        )
        if codigo is None:
            continue
        codigos_cadastrados.add(codigo)
        implementado = registro.contem(codigo)
        detector = registro.obter(codigo) if implementado else None
        grupo["padroes"].append(
            {
                "padrao_cod": codigo,
                "padrao_nome": nome,
                "funcao_python": None if detector is None else detector.__name__,
                "implementado": implementado,
                "num_oco": ocorrencias,
                "percentual_historico": (
                    None
                    if ocorrencias is None or total_resultados == 0
                    else round(ocorrencias * 100 / total_resultados, 6)
                ),
                "intervalo_medio": None if intervalo is None else str(intervalo),
                "desv_padrao": None if desvio is None else str(desvio),
            }
        )

    codigos_detectores = set(registro.codigos_registrados())
    inventario = {
        "total_resultados": total_resultados,
        "total_grupos": len(grupos),
        "total_padroes": len(codigos_cadastrados),
        "total_detectores": len(codigos_detectores),
        "detectores_sem_cadastro": sorted(codigos_detectores - codigos_cadastrados),
        "cadastros_sem_detector": sorted(codigos_cadastrados - codigos_detectores),
        "grupos": list(grupos.values()),
    }
    print(json.dumps(inventario, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
