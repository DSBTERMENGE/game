"""Valida o recálculo sequencial controlado e no histórico clonado."""

from dataclasses import replace
from datetime import date
import json
import sys

from dotenv import load_dotenv
import psycopg
from psycopg import sql

from msen.calculos import calcular_resultado
from msen.config import carregar_configuracao_banco
from msen.database import RepositorioResultados, executar_migracoes
from msen.modelos import ResultadoEntrada
from msen.services import recalcular_classificacoes_grupo_sequenciais
from suporte_banco_integracao import (
    MIGRACOES,
    _restaurar_backup,
    conectar,
    criar,
    criar_vazio,
    remover,
    validar_nome,
)


RESULTADOS_CONTROLADOS = (
    (1, (1, 3, 5, 7, 9, 11)),
    (2, (10, 25, 26, 38, 50, 58)),
    (3, (10, 25, 26, 27, 50, 58)),
    (4, (1, 2, 3, 4, 20, 40)),
)


def _contagens(relatorio) -> dict[str, int]:
    """Converte o resumo imutável para uma estrutura serializável."""
    return {
        "SEM_CORRESPONDENCIA" if item.padrao_cod is None else item.padrao_cod:
        item.quantidade
        for item in relatorio.contagens
    }


def _ids_classificacoes(conexao) -> tuple[tuple[int, int], ...]:
    """Lê os identificadores para confirmar que o recálculo não duplica linhas."""
    with conexao.cursor() as cursor:
        cursor.execute(
            "SELECT id_resultado, id_classificacao "
            "FROM resultado_classificacao_padrao ORDER BY id_resultado"
        )
        return tuple(cursor.fetchall())


def validar_controlado(nome_database: str) -> dict[str, object]:
    """Valida atomicidade, contagens, idempotência e troca de versão."""
    nome = validar_nome(nome_database)
    base = carregar_configuracao_banco()
    criar(base, nome)
    configuracao = replace(base, nome=nome)
    try:
        with conectar(configuracao, nome) as conexao:
            repositorio = RepositorioResultados(conexao)
            ids_resultados = []
            for numero_ap, dezenas in RESULTADOS_CONTROLADOS:
                entrada = ResultadoEntrada.criar(
                    data_resultado=date(2026, 10, 20 + numero_ap),
                    numero_ap=numero_ap,
                    resultados=dezenas,
                )
                persistido = repositorio.inserir(calcular_resultado(entrada))
                ids_resultados.append(persistido.id_resultado)

            with conexao.transaction():
                with conexao.cursor() as cursor:
                    cursor.execute(
                        sql.SQL(
                            "CREATE FUNCTION falhar_recalculo_16_6() RETURNS trigger "
                            "LANGUAGE plpgsql AS $$ BEGIN "
                            "IF NEW.id_resultado = {} THEN "
                            "RAISE EXCEPTION 'falha controlada'; "
                            "END IF; RETURN NEW; END $$"
                        ).format(sql.Literal(ids_resultados[2]))
                    )
                    cursor.execute(
                        "CREATE TRIGGER tg_falhar_recalculo_16_6 "
                        "BEFORE INSERT OR UPDATE ON resultado_classificacao_padrao "
                        "FOR EACH ROW EXECUTE FUNCTION falhar_recalculo_16_6()"
                    )
            try:
                recalcular_classificacoes_grupo_sequenciais(conexao)
            except psycopg.errors.RaiseException:
                pass
            else:
                raise AssertionError("A falha controlada não interrompeu o recálculo.")
            with conexao.cursor() as cursor:
                cursor.execute("SELECT count(*) FROM resultado_classificacao_padrao")
                if cursor.fetchone()[0] != 0:
                    raise AssertionError("O recálculo com falha deixou gravações parciais.")
            with conexao.transaction():
                with conexao.cursor() as cursor:
                    cursor.execute(
                        "DROP TRIGGER tg_falhar_recalculo_16_6 "
                        "ON resultado_classificacao_padrao"
                    )
                    cursor.execute("DROP FUNCTION falhar_recalculo_16_6()")

            primeiro = recalcular_classificacoes_grupo_sequenciais(conexao)
            ids_primeiro = _ids_classificacoes(conexao)
            segundo = recalcular_classificacoes_grupo_sequenciais(conexao)
            ids_segundo = _ids_classificacoes(conexao)
            terceira = recalcular_classificacoes_grupo_sequenciais(
                conexao, versao_calculo=2
            )
            ids_terceira = _ids_classificacoes(conexao)
            if ids_primeiro != ids_segundo or ids_primeiro != ids_terceira:
                raise AssertionError("O recálculo alterou as identidades persistidas.")
            esperado = {
                "PD_001": 1,
                "PD_002": 1,
                "PD_003": 1,
                "SEM_CORRESPONDENCIA": 1,
            }
            if _contagens(primeiro) != esperado or _contagens(segundo) != esperado:
                raise AssertionError("As contagens controladas divergiram.")
            with conexao.cursor() as cursor:
                cursor.execute(
                    "SELECT count(*) FROM resultado_classificacao_padrao "
                    "WHERE versao_calculo = 2"
                )
                if cursor.fetchone()[0] != 4:
                    raise AssertionError("A nova versão não alcançou todas as linhas.")
            return {
                "resultados": terceira.resultados_analisados,
                "contagens": _contagens(terceira),
                "rollback_integral": True,
                "identidades_preservadas": True,
                "versao_final": terceira.versao_calculo,
            }
    finally:
        remover(base, nome)


def validar_historico_clonado(nome_database: str) -> dict[str, object]:
    """Restaura o histórico real em clone, migra, classifica duas vezes e remove."""
    nome = validar_nome(nome_database)
    base = carregar_configuracao_banco()
    criar_vazio(base, nome)
    configuracao = replace(base, nome=nome)
    try:
        _restaurar_backup(base, nome)
        executar_migracoes(configuracao, MIGRACOES)
        with conectar(configuracao, nome) as conexao:
            primeiro = recalcular_classificacoes_grupo_sequenciais(conexao)
            ids_primeiro = _ids_classificacoes(conexao)
            segundo = recalcular_classificacoes_grupo_sequenciais(conexao)
            ids_segundo = _ids_classificacoes(conexao)
            if ids_primeiro != ids_segundo:
                raise AssertionError("O segundo recálculo histórico alterou identidades.")
            contagens = _contagens(segundo)
            if sum(contagens.values()) != segundo.resultados_analisados:
                raise AssertionError("As classes não reconciliam com o histórico.")
            return {
                "resultados": segundo.resultados_analisados,
                "classificacoes": len(ids_segundo),
                "contagens": contagens,
                "recalculo_idempotente": True,
            }
    finally:
        remover(base, nome)


def main() -> None:
    load_dotenv()
    if len(sys.argv) != 3 or sys.argv[1] not in {"controlado", "historico"}:
        raise SystemExit(
            "Uso: validar_recalculo_classificacao_padroes.py "
            "controlado|historico NOME_TEMPORARIO"
        )
    funcao = validar_controlado if sys.argv[1] == "controlado" else validar_historico_clonado
    print(json.dumps(funcao(sys.argv[2]), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
