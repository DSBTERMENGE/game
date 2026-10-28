"""Valida o repositório de classificações em PostgreSQL temporário."""

from dataclasses import replace
import json
import sys

from dotenv import load_dotenv

from msen.config import carregar_configuracao_banco
from msen.database import RepositorioClassificacoesPadrao
from msen.modelos import EstadoClassificacaoPadrao
from suporte_banco_integracao import conectar, criar, remover, validar_nome


def _inserir_resultado(cursor, numero_ap: int) -> int:
    """Inclui um resultado válido usado somente pelo ensaio integrado."""
    cursor.execute(
        "INSERT INTO resultados ("
        "data_resultado, numero_ap, res_01, res_02, res_03, res_04, res_05, res_06, "
        "soma_res, media_aritmetica_res, mediana_res, desvio_padrao_media, "
        "media_coordenada_x, media_coordenada_y"
        ") VALUES (DATE '2026-10-28', %s, 1, 2, 3, 4, 5, 6, "
        "21, 3.5, 3.5, 1.707825, 2.5, 0) RETURNING id_resultado",
        (numero_ap,),
    )
    return cursor.fetchone()[0]


def validar(nome_database: str) -> dict[str, object]:
    """Testa inserção, atualização e as duas consultas e remove o database."""
    nome = validar_nome(nome_database)
    configuracao_base = carregar_configuracao_banco()
    criar(configuracao_base, nome)
    configuracao = replace(configuracao_base, nome=nome)
    try:
        with conectar(configuracao, nome) as conexao:
            with conexao.cursor() as cursor:
                resultado_1 = _inserir_resultado(cursor, 910001)
                resultado_2 = _inserir_resultado(cursor, 910002)
                cursor.execute(
                    "SELECT g.id_grupo, p.id_padrao FROM padroes_grupo g "
                    "JOIN padroes_subgrupo p USING (id_grupo) "
                    "WHERE g.grupo_cod = 'PG_001' AND p.padrao_cod = 'PD_001'"
                )
                grupo_1, padrao_1 = cursor.fetchone()
                cursor.execute(
                    "SELECT g.id_grupo, p.id_padrao FROM padroes_grupo g "
                    "JOIN padroes_subgrupo p USING (id_grupo) "
                    "WHERE g.grupo_cod = 'PG_001' AND p.padrao_cod = 'PD_002'"
                )
                _, padrao_2 = cursor.fetchone()
                cursor.execute(
                    "SELECT id_grupo FROM padroes_grupo WHERE grupo_cod = 'PG_002'"
                )
                grupo_2 = cursor.fetchone()[0]

            repositorio = RepositorioClassificacoesPadrao(conexao)
            primeira = repositorio.salvar(
                resultado_1,
                grupo_1,
                id_padrao=padrao_1,
                estado=EstadoClassificacaoPadrao.PADRAO_IDENTIFICADO,
            )
            sem_correspondencia = repositorio.salvar(
                resultado_1,
                grupo_2,
                id_padrao=None,
                estado=EstadoClassificacaoPadrao.SEM_CORRESPONDENCIA,
            )
            repositorio.salvar(
                resultado_2,
                grupo_1,
                id_padrao=padrao_1,
                estado=EstadoClassificacaoPadrao.PADRAO_IDENTIFICADO,
            )
            atualizada = repositorio.salvar(
                resultado_1,
                grupo_1,
                id_padrao=padrao_2,
                estado=EstadoClassificacaoPadrao.PADRAO_IDENTIFICADO,
                versao_calculo=2,
            )
            conexao.commit()

            por_resultado = repositorio.listar_por_resultado(resultado_1)
            por_grupo = repositorio.listar_por_grupo(grupo_1)
            if atualizada.id_classificacao != primeira.id_classificacao:
                raise AssertionError("O recálculo criou outra classificação.")
            if atualizada.id_padrao != padrao_2 or atualizada.versao_calculo != 2:
                raise AssertionError("O recálculo não atualizou padrão e versão.")
            if len(por_resultado) != 2 or len(por_grupo) != 2:
                raise AssertionError("As consultas não retornaram as classificações esperadas.")
            if por_resultado[1] != sem_correspondencia:
                raise AssertionError("SEM_CORRESPONDENCIA não foi preservado na consulta.")

            return {
                "insercao": "confirmada",
                "atualizacao_idempotente": "confirmada",
                "classificacoes_do_resultado": len(por_resultado),
                "classificacoes_do_grupo": len(por_grupo),
                "estado_sem_correspondencia": sem_correspondencia.estado.value,
                "versao_atualizada": atualizada.versao_calculo,
            }
    finally:
        remover(configuracao_base, nome)


def main() -> None:
    load_dotenv()
    if len(sys.argv) != 2:
        raise SystemExit("Uso: validar_repositorio_classificacoes_padrao.py NOME_TEMPORARIO")
    print(json.dumps(validar(sys.argv[1]), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
