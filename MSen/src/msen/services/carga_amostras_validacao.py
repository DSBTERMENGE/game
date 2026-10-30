"""Carga idempotente das 200 amostras iniciais de homologação."""

from dataclasses import dataclass

import psycopg

from msen.database import RepositorioValidacao


@dataclass(frozen=True, slots=True)
class RelatorioCargaAmostrasValidacao:
    quantidade_planejada: int
    amostras_incluidas: int
    amostras_ja_existentes: int
    avaliacoes_criadas: int
    primeiro_numero_ap: int
    ultimo_numero_ap: int


def carregar_amostras_iniciais_validacao(
    conexao: psycopg.Connection,
    *,
    quantidade: int = 200,
) -> RelatorioCargaAmostrasValidacao:
    """Relaciona os primeiros resultados sem duplicar suas seis dezenas."""

    if not isinstance(conexao, psycopg.Connection):
        raise TypeError("A carga exige uma conexão Psycopg válida.")
    if isinstance(quantidade, bool) or not isinstance(quantidade, int):
        raise TypeError("quantidade deve ser inteira.")
    if quantidade <= 0:
        raise ValueError("quantidade deve ser positiva.")

    with conexao.transaction():
        with conexao.cursor() as cursor:
            cursor.execute(
                "SELECT id_resultado, numero_ap FROM resultados "
                "ORDER BY numero_ap, id_resultado LIMIT %s",
                (quantidade,),
            )
            resultados = tuple(cursor.fetchall())
            if len(resultados) != quantidade:
                raise ValueError(
                    f"A carga exige {quantidade} resultados; encontrados {len(resultados)}."
                )
            cursor.execute(
                "SELECT ordem, id_resultado FROM amostras_validacao "
                "WHERE ordem <= %s ORDER BY ordem",
                (quantidade,),
            )
            existentes = dict(cursor.fetchall())
            esperados = {
                ordem: id_resultado
                for ordem, (id_resultado, _numero_ap) in enumerate(resultados, 1)
            }
            divergentes = tuple(
                ordem for ordem, id_resultado in existentes.items()
                if esperados.get(ordem) != id_resultado
            )
            if divergentes:
                raise RuntimeError(
                    "As posições iniciais já contêm resultados diferentes: "
                    f"{divergentes!r}."
                )
            faltantes = tuple(
                (id_resultado, ordem)
                for ordem, id_resultado in esperados.items()
                if ordem not in existentes
            )
            if faltantes:
                cursor.executemany(
                    "INSERT INTO amostras_validacao (id_resultado, ordem) VALUES (%s, %s)",
                    faltantes,
                )

        avaliacoes = RepositorioValidacao(conexao).sincronizar_avaliacoes_pendentes()
        with conexao.cursor() as cursor:
            cursor.execute(
                "UPDATE estado_algoritmo_selecao SET atualizado = FALSE, "
                "motivo = 'AMOSTRAS_AGUARDANDO_REFERENCIAS_E_CALCULOS', "
                "alterado_em = CURRENT_TIMESTAMP WHERE id_estado = 1"
            )

    return RelatorioCargaAmostrasValidacao(
        quantidade_planejada=quantidade,
        amostras_incluidas=len(faltantes),
        amostras_ja_existentes=len(existentes),
        avaliacoes_criadas=avaliacoes,
        primeiro_numero_ap=resultados[0][1],
        ultimo_numero_ap=resultados[-1][1],
    )
