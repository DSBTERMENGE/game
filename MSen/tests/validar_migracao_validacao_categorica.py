"""Valida a migração 035 somente em um database temporário."""

from dataclasses import replace
import json
from pathlib import Path
import sys
import tempfile

from dotenv import load_dotenv
import psycopg

from msen.config import carregar_configuracao_banco
from msen.database import RepositorioValidacao, executar_migracoes
from msen.services import (
    ErroReferenciaValidacao,
    aprovar_referencia_categorica,
    executar_criterio_categorico,
    sincronizar_criterios_validacao,
)
from msen.validacao import (
    RegistroCriteriosValidacao,
    criar_definicao_criterio_diagonal,
    criar_registro_criterios_producao,
)
from suporte_banco_integracao import conectar, criar_vazio, remover, validar_nome
from validar_migracao_arranjos_diagonais import (
    MIGRACOES,
    _copiar_migracoes,
    _preparar_catalogo_anterior,
)


ASSINATURA = "a" * 64
REGRA = "b" * 64


def _categorias_equivalentes(dezenas):
    return criar_definicao_criterio_diagonal().funcao(dezenas)


def _preparar_ate_034(configuracao, nome: str) -> None:
    with tempfile.TemporaryDirectory() as pasta:
        anteriores = Path(pasta)
        _copiar_migracoes(anteriores, 32)
        executar_migracoes(configuracao, anteriores)
    _preparar_catalogo_anterior(configuracao, nome)
    with tempfile.TemporaryDirectory() as pasta:
        ate_034 = Path(pasta)
        _copiar_migracoes(ate_034, 34)
        executar_migracoes(configuracao, ate_034)


def _semear_contratos_existentes(configuracao, nome: str) -> None:
    with conectar(configuracao, nome) as conexao, conexao.cursor() as cursor:
        cursor.execute(
            "INSERT INTO resultados (data_resultado, numero_ap, res_01, res_02, "
            "res_03, res_04, res_05, res_06, soma_res, media_aritmetica_res, "
            "mediana_res, desvio_padrao_media, media_coordenada_x, "
            "media_coordenada_y) VALUES "
            "('2026-01-01', 1, 1, 2, 3, 4, 5, 6, 21, 3.5, 3.5, 1.707825, "
            "2.5, 0) RETURNING id_resultado"
        )
        id_resultado = cursor.fetchone()[0]
        cursor.execute(
            "INSERT INTO amostras_validacao (id_resultado, ordem) VALUES (%s, 1)",
            (id_resultado,),
        )
        cursor.execute(
            "INSERT INTO criterios_validacao (codigo, nome, categoria, "
            "funcao_python, tipo_resultado, assinatura_funcao, assinatura_regra) "
            "VALUES ('EST_TESTE', 'Numérico', 'ESTATISTICA', 'teste.numero', "
            "'INTEIRO', %s, %s) RETURNING id_criterio",
            (ASSINATURA, REGRA),
        )
        id_numerico = cursor.fetchone()[0]
        cursor.execute(
            "SELECT g.id_grupo, p.id_padrao FROM padroes_grupo g "
            "JOIN padroes_subgrupo p USING (id_grupo) "
            "WHERE g.grupo_cod='PG_001' AND p.padrao_cod='PD_001'"
        )
        id_grupo, id_padrao = cursor.fetchone()
        cursor.execute(
            "INSERT INTO criterios_validacao (codigo, nome, categoria, "
            "funcao_python, tipo_resultado, id_grupo, id_padrao, "
            "assinatura_funcao, assinatura_regra) VALUES "
            "('PAD_TESTE', 'Booleano', 'PADRAO', 'teste.booleano', 'PADRAO', "
            "%s, %s, %s, %s) RETURNING id_criterio",
            (id_grupo, id_padrao, ASSINATURA, REGRA),
        )
        id_booleano = cursor.fetchone()[0]
        cursor.execute(
            "INSERT INTO avaliacoes_validacao (id_resultado, id_criterio, "
            "referencia_conferida, estado_valor_esperado, valor_esperado, "
            "estado_valor_calculado, valor_calculado, executado, "
            "assinatura_executada, aprovado, diferenca, calculado_em, "
            "referencia_origem, referencia_revisor, referencia_conferida_em) "
            "VALUES (%s, %s, TRUE, 'VALOR_IDENTIFICADO', 21, "
            "'VALOR_IDENTIFICADO', 21, TRUE, %s, 'S', 0, CURRENT_TIMESTAMP, "
            "'TESTE_AUTOMATIZADO', 'Validador 035', CURRENT_TIMESTAMP)",
            (id_resultado, id_numerico, ASSINATURA),
        )
        cursor.execute(
            "INSERT INTO avaliacoes_validacao (id_resultado, id_criterio, "
            "id_grupo, referencia_conferida, estado_padrao_esperado, "
            "id_padrao_esperado, estado_padrao_calculado, id_padrao_calculado, "
            "executado, assinatura_executada, aprovado, calculado_em, "
            "referencia_origem, referencia_revisor, referencia_conferida_em) "
            "VALUES (%s, %s, %s, TRUE, 'PADRAO_IDENTIFICADO', %s, "
            "'PADRAO_IDENTIFICADO', %s, TRUE, %s, 'S', CURRENT_TIMESTAMP, "
            "'TESTE_AUTOMATIZADO', 'Validador 035', CURRENT_TIMESTAMP)",
            (
                id_resultado,
                id_booleano,
                id_grupo,
                id_padrao,
                id_padrao,
                ASSINATURA,
            ),
        )
        conexao.commit()


def _fotografar_existentes(cursor):
    cursor.execute(
        "SELECT c.codigo, a.id_grupo, a.valor_esperado, a.valor_calculado, "
        "a.estado_padrao_esperado, a.id_padrao_esperado, "
        "a.estado_padrao_calculado, a.id_padrao_calculado, a.aprovado "
        "FROM avaliacoes_validacao a JOIN criterios_validacao c USING "
        "(id_criterio) ORDER BY c.codigo"
    )
    return tuple(cursor.fetchall())


def _exigir_rejeicao(conexao, comando: str, parametros=()) -> None:
    try:
        with conexao.transaction():
            with conexao.cursor() as cursor:
                cursor.execute(comando, parametros)
    except psycopg.IntegrityError:
        return
    raise AssertionError("O PostgreSQL aceitou uma combinação categórica inválida.")


def _validar_restricoes(configuracao, nome: str, preservados) -> dict[str, object]:
    definicao = criar_definicao_criterio_diagonal()
    with conectar(configuracao, nome) as conexao, conexao.cursor() as cursor:
        if _fotografar_existentes(cursor) != preservados:
            raise AssertionError("A migração alterou avaliações existentes.")
        cursor.execute(
            "SELECT id_resultado FROM amostras_validacao WHERE ativo ORDER BY ordem LIMIT 1"
        )
        id_resultado = cursor.fetchone()[0]
        cursor.execute("SELECT id_grupo FROM padroes_grupo WHERE grupo_cod='PG_004'")
        id_grupo = cursor.fetchone()[0]
        cursor.execute(
            "INSERT INTO criterios_validacao (codigo, nome, categoria, "
            "funcao_python, tipo_resultado, id_grupo, assinatura_funcao, "
            "assinatura_regra) VALUES (%s, %s, %s, %s, %s, %s, %s, %s) "
            "RETURNING id_criterio",
            (
                definicao.codigo,
                definicao.nome,
                definicao.categoria,
                definicao.funcao_python,
                definicao.tipo_resultado,
                id_grupo,
                definicao.assinatura_funcao,
                definicao.assinatura_regra,
            ),
        )
        id_criterio = cursor.fetchone()[0]
        cursor.execute(
            "INSERT INTO avaliacoes_validacao (id_resultado, id_criterio, "
            "id_grupo, referencia_conferida, categoria_esperada, "
            "referencia_origem, referencia_revisor, referencia_conferida_em) "
            "VALUES (%s, %s, %s, TRUE, '0D0E', "
            "'TESTE_AUTOMATIZADO', 'Validador 035', "
            "CURRENT_TIMESTAMP)",
            (id_resultado, id_criterio, id_grupo),
        )
        conexao.commit()

        relatorio = executar_criterio_categorico(conexao, definicao)

        _exigir_rejeicao(
            conexao,
            "UPDATE avaliacoes_validacao SET "
            "estado_padrao_esperado = 'SEM_CORRESPONDENCIA' "
            "WHERE id_resultado = %s AND id_criterio = %s",
            (id_resultado, id_criterio),
        )
        _exigir_rejeicao(
            conexao,
            "UPDATE avaliacoes_validacao SET categoria_esperada = '   ' "
            "WHERE id_resultado = %s AND id_criterio = %s",
            (id_resultado, id_criterio),
        )
        cursor.execute(
            "SELECT categoria_esperada, categoria_calculada, aprovado "
            "FROM avaliacoes_validacao WHERE id_resultado=%s AND id_criterio=%s",
            (id_resultado, id_criterio),
        )
        categoria = cursor.fetchone()
    return {
        "avaliacoes_preservadas": len(preservados),
        "avaliacao_categorica": categoria,
        "execucao_categorica": {
            "avaliacoes": relatorio.total_avaliacoes,
            "aprovadas": relatorio.aprovadas,
            "reprovadas": relatorio.reprovadas,
        },
    }


def _validar_sincronizacao(configuracao, nome: str) -> dict[str, object]:
    definicao = criar_definicao_criterio_diagonal()
    with conectar(configuracao, nome) as conexao:
        with conexao.cursor() as cursor:
            cursor.execute("DELETE FROM criterios_validacao")
        conexao.commit()
        relatorio = sincronizar_criterios_validacao(
            conexao, RegistroCriteriosValidacao((definicao,))
        )
        conexao.commit()
        with conexao.cursor() as cursor:
            cursor.execute(
                "SELECT c.tipo_resultado, g.grupo_cod, c.id_padrao, "
                "a.id_grupo IS NOT NULL, a.referencia_conferida, "
                "a.categoria_esperada, a.categoria_calculada, a.executado "
                "FROM criterios_validacao c "
                "JOIN padroes_grupo g USING (id_grupo) "
                "JOIN avaliacoes_validacao a USING (id_criterio) "
                "WHERE c.codigo='PAD_PG_004'"
            )
            estado = cursor.fetchone()
    esperado = ("CATEGORICO", "PG_004", None, True, False, None, None, False)
    if estado != esperado:
        raise AssertionError(f"Sincronização categórica divergente: {estado!r}.")
    if relatorio.incluidos != ("PAD_PG_004",) or relatorio.avaliacoes_criadas != 1:
        raise AssertionError(f"Relatório de sincronização divergente: {relatorio!r}.")

    with conectar(configuracao, nome) as conexao:
        with conexao.cursor() as cursor:
            cursor.execute(
                "UPDATE avaliacoes_validacao SET referencia_conferida=TRUE, "
                "categoria_esperada='0D0E', categoria_calculada='0D0E', "
                "executado=TRUE, assinatura_executada=%s, aprovado='S', "
                "calculado_em=CURRENT_TIMESTAMP, referencia_origem="
                "'TESTE_AUTOMATIZADO', referencia_revisor='Validador 035', "
                "referencia_conferida_em=CURRENT_TIMESTAMP",
                (definicao.assinatura_funcao,),
            )
        conexao.commit()
        implementacao = replace(definicao, funcao=_categorias_equivalentes)
        alteracao = sincronizar_criterios_validacao(
            conexao, RegistroCriteriosValidacao((implementacao,))
        )
        conexao.commit()
        with conexao.cursor() as cursor:
            cursor.execute(
                "SELECT referencia_conferida, categoria_esperada, "
                "categoria_calculada, executado FROM avaliacoes_validacao"
            )
            apos_implementacao = cursor.fetchone()
        regra = replace(implementacao, regra=f"{implementacao.regra} Revisada.")
        alteracao_regra = sincronizar_criterios_validacao(
            conexao, RegistroCriteriosValidacao((regra,))
        )
        conexao.commit()
        with conexao.cursor() as cursor:
            cursor.execute(
                "SELECT referencia_conferida, categoria_esperada, "
                "categoria_calculada, executado FROM avaliacoes_validacao"
            )
            apos_regra = cursor.fetchone()
    if alteracao.implementacoes_alteradas != ("PAD_PG_004",):
        raise AssertionError("A alteração da implementação não foi reconhecida.")
    if apos_implementacao != (True, "0D0E", None, False):
        raise AssertionError(f"Limpeza da implementação divergente: {apos_implementacao!r}.")
    if alteracao_regra.regras_alteradas != ("PAD_PG_004",):
        raise AssertionError("A alteração da regra não foi reconhecida.")
    if apos_regra != (False, None, None, False):
        raise AssertionError(f"Limpeza da regra divergente: {apos_regra!r}.")
    with conectar(configuracao, nome) as conexao:
        with conexao.cursor() as cursor:
            cursor.execute(
                "SELECT id_resultado, id_criterio FROM avaliacoes_validacao LIMIT 1"
            )
            id_resultado, id_criterio = cursor.fetchone()
        referencia = aprovar_referencia_categorica(
            conexao,
            id_resultado=id_resultado,
            id_criterio=id_criterio,
            categoria_esperada="0D0E",
            origem="TESTE_AUTOMATIZADO",
            revisor="Validador 035",
        )
        try:
            aprovar_referencia_categorica(
                conexao,
                id_resultado=id_resultado,
                id_criterio=id_criterio,
                categoria_esperada="0D0E",
                origem="TESTE_AUTOMATIZADO",
                revisor="Validador 035",
            )
        except ErroReferenciaValidacao as erro:
            if erro.codigo != "REFERENCIA_PROTEGIDA":
                raise
        else:
            raise AssertionError("A referência categórica conferida foi sobrescrita.")
        avaliacao = RepositorioValidacao(conexao).listar_avaliacoes()[0]
        execucao_final = executar_criterio_categorico(conexao, regra)
    if referencia.categoria != "0D0E" or avaliacao.categoria_esperada != "0D0E":
        raise AssertionError("A referência categórica não foi exposta pelo repositório.")
    if execucao_final.aprovadas != 1:
        raise AssertionError("A referência categórica aprovada divergiu na execução.")
    with conectar(configuracao, nome) as conexao:
        with conexao.cursor() as cursor:
            cursor.execute("DELETE FROM criterios_validacao")
        conexao.commit()
        catalogo_completo = sincronizar_criterios_validacao(
            conexao, criar_registro_criterios_producao()
        )
        conexao.commit()
        with conexao.cursor() as cursor:
            cursor.execute(
                "SELECT count(*), count(*) FILTER (WHERE tipo_resultado='CATEGORICO'), "
                "count(*) FILTER (WHERE codigo='PAD_PG_004' AND id_padrao IS NULL) "
                "FROM criterios_validacao"
            )
            totais_catalogo = cursor.fetchone()
            cursor.execute("SELECT count(*) FROM avaliacoes_validacao")
            total_avaliacoes = cursor.fetchone()[0]
    if totais_catalogo != (20, 1, 1) or total_avaliacoes != 20:
        raise AssertionError(
            f"Catálogo conjunto divergente: {totais_catalogo!r}, {total_avaliacoes}."
        )
    if len(catalogo_completo.incluidos) != 20 or catalogo_completo.avaliacoes_criadas != 20:
        raise AssertionError(f"Sincronização conjunta divergente: {catalogo_completo!r}.")
    return {
        "incluidos": list(relatorio.incluidos),
        "avaliacoes_criadas": relatorio.avaliacoes_criadas,
        "estado_pendente": estado,
        "implementacao_preserva_referencia": True,
        "regra_invalida_referencia": True,
        "referencia_categorica_protegida": True,
        "repositorio_expoe_categoria": True,
        "catalogo_conjunto": {
            "criterios": totais_catalogo[0],
            "categoricos": totais_catalogo[1],
            "avaliacoes": total_avaliacoes,
        },
    }


def validar(nome_database: str) -> dict[str, object]:
    nome = validar_nome(nome_database)
    base = carregar_configuracao_banco()
    criar_vazio(base, nome)
    configuracao = replace(base, nome=nome)
    try:
        _preparar_ate_034(configuracao, nome)
        _semear_contratos_existentes(configuracao, nome)
        with conectar(configuracao, nome) as conexao, conexao.cursor() as cursor:
            preservados = _fotografar_existentes(cursor)
        primeira = executar_migracoes(configuracao, MIGRACOES)
        estado = _validar_restricoes(configuracao, nome, preservados)
        estado["sincronizacao"] = _validar_sincronizacao(configuracao, nome)
        segunda = executar_migracoes(configuracao, MIGRACOES)
        if primeira.aplicadas != ("035",):
            raise AssertionError(f"Primeira execução inesperada: {primeira}.")
        if segunda.aplicadas:
            raise AssertionError(f"A migração foi reaplicada: {segunda}.")
        return {
            "migracao_aplicada": list(primeira.aplicadas),
            "segunda_execucao_sem_reaplicar": True,
            "estado": estado,
        }
    finally:
        remover(base, nome)


def main() -> None:
    load_dotenv()
    if len(sys.argv) != 2:
        raise SystemExit("Uso: validar_migracao_validacao_categorica.py NOME_TEMPORARIO")
    print(json.dumps(validar(sys.argv[1]), ensure_ascii=False, indent=2, default=str))


if __name__ == "__main__":
    main()
