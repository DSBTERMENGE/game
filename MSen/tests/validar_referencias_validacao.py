"""Valida o registro protegido de referências da subetapa 20.7."""

from dataclasses import replace
import json
from pathlib import Path
import sys

from dotenv import load_dotenv

from msen.config import carregar_configuracao_banco
from msen.database import abrir_conexao, executar_migracoes, RepositorioValidacao
from msen.services import (
    ErroReferenciaValidacao,
    aprovar_referencia_numerica,
    aprovar_referencia_padrao,
    sincronizar_criterios_validacao,
)
from msen.validacao import criar_registro_criterios_producao
from suporte_banco_integracao import criar_vazio, remover, validar_nome


MIGRACOES = Path(__file__).resolve().parents[2] / "database" / "migrations"


def _exigir_erro(codigo, operacao):
    try:
        operacao()
    except ErroReferenciaValidacao as erro:
        if erro.codigo != codigo:
            raise
        return
    raise AssertionError(f"A operação não produziu {codigo}.")


def validar(nome_database: str) -> dict[str, object]:
    nome = validar_nome(nome_database)
    base = carregar_configuracao_banco()
    criar_vazio(base, nome)
    configuracao = replace(base, nome=nome)
    try:
        executar_migracoes(configuracao, MIGRACOES)
        with abrir_conexao(configuracao) as conexao:
            with conexao.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO resultados (data_resultado, numero_ap, res_01, res_02, "
                    "res_03, res_04, res_05, res_06, soma_res, media_aritmetica_res, "
                    "mediana_res, desvio_padrao_media, media_coordenada_x, "
                    "media_coordenada_y) VALUES (DATE '2026-10-30', 960001, "
                    "1, 2, 3, 10, 20, 40, 76, 12.666667, 6.5, 14.266783, 2.5, 0) "
                    "RETURNING id_resultado"
                )
                resultado = cursor.fetchone()[0]
            conexao.commit()
            sincronizar_criterios_validacao(
                conexao, criar_registro_criterios_producao()
            )
            conexao.commit()
            RepositorioValidacao(conexao).incluir_amostra(resultado, 1)
            conexao.commit()
            with conexao.cursor() as cursor:
                cursor.execute(
                    "SELECT codigo, id_criterio FROM criterios_validacao WHERE codigo IN "
                    "('EST_SOMA', 'GEO_CENTRO_X', 'PAD_PD_002', 'PAD_PD_003')"
                )
                criterios = dict(cursor.fetchall())
                cursor.execute(
                    "SELECT padrao_cod, id_padrao FROM padroes_subgrupo "
                    "WHERE padrao_cod IN ('PD_002', 'PD_003')"
                )
                padroes = dict(cursor.fetchall())

            numerica = aprovar_referencia_numerica(
                conexao, id_resultado=resultado, id_criterio=criterios["EST_SOMA"],
                valor=76, origem="IA", revisor="cálculo independente 20.7",
                observacao="1 + 2 + 3 + 10 + 20 + 40",
            )
            ausente = aprovar_referencia_numerica(
                conexao, id_resultado=resultado,
                id_criterio=criterios["GEO_CENTRO_X"], valor=None,
                origem="HUMANO", revisor="revisor geométrico",
            )
            detectado = aprovar_referencia_padrao(
                conexao, id_resultado=resultado,
                id_criterio=criterios["PAD_PD_002"], id_padrao=padroes["PD_002"],
                origem="TESTE_AUTOMATIZADO", revisor="oráculo independente",
            )
            nao_detectado = aprovar_referencia_padrao(
                conexao, id_resultado=resultado,
                id_criterio=criterios["PAD_PD_003"], id_padrao=None,
                origem="IA", revisor="análise independente",
            )
            conexao.commit()
            if numerica.valor != 76 or ausente.estado != "SEM_VALOR":
                raise AssertionError("Referência numérica divergente.")
            if detectado.id_padrao != padroes["PD_002"]:
                raise AssertionError("Referência positiva de padrão divergente.")
            if nao_detectado.estado != "SEM_CORRESPONDENCIA":
                raise AssertionError("Ausência de padrão divergente.")

            _exigir_erro(
                "REFERENCIA_PROTEGIDA",
                lambda: aprovar_referencia_numerica(
                    conexao, id_resultado=resultado,
                    id_criterio=criterios["EST_SOMA"], valor=77,
                    origem="IA", revisor="tentativa de sobrescrita",
                ),
            )
            conexao.rollback()
            with conexao.cursor() as cursor:
                cursor.execute(
                    "UPDATE avaliacoes_validacao SET referencia_conferida = FALSE, "
                    "estado_padrao_esperado = NULL, id_padrao_esperado = NULL, "
                    "referencia_origem = NULL, referencia_revisor = NULL, "
                    "referencia_conferida_em = NULL WHERE id_resultado = %s "
                    "AND id_criterio = %s",
                    (resultado, criterios["PAD_PD_003"]),
                )
            conexao.commit()
            _exigir_erro(
                "PADRAO_INCOMPATIVEL",
                lambda: aprovar_referencia_padrao(
                    conexao, id_resultado=resultado,
                    id_criterio=criterios["PAD_PD_003"],
                    id_padrao=padroes["PD_002"], origem="IA",
                    revisor="tentativa incompatível",
                ),
            )
            conexao.rollback()
            with conexao.cursor() as cursor:
                cursor.execute(
                    "SELECT count(*) FROM avaliacoes_validacao "
                    "WHERE referencia_conferida"
                )
                conferidas = cursor.fetchone()[0]
                cursor.execute("SELECT atualizado, motivo FROM estado_algoritmo_selecao")
                estado = cursor.fetchone()
            if conferidas != 3:
                raise AssertionError(f"Total conferido inesperado: {conferidas}.")
            if estado != (False, "REFERENCIAS_OU_CALCULOS_PENDENTES"):
                raise AssertionError(f"Estado global inesperado: {estado!r}")

        return {
            "referencia_numerica": True,
            "valor_ausente": True,
            "padrao_identificado": True,
            "sem_correspondencia": True,
            "origem_e_revisor": True,
            "sobrescrita_rejeitada": True,
            "padrao_incompativel_rejeitado": True,
            "demais_referencias_pendentes": True,
        }
    finally:
        remover(base, nome)


def main() -> None:
    load_dotenv()
    if len(sys.argv) != 2:
        raise SystemExit("Uso: validar_referencias_validacao.py NOME_TEMPORARIO")
    print(json.dumps(validar(sys.argv[1]), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
