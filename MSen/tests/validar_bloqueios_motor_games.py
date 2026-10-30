"""Valida bloqueios da 20.11 no games e força rollback de cada cenário."""

import json
import sys

from dotenv import load_dotenv

from msen.config import carregar_configuracao_banco
from msen.database import abrir_conexao
from msen.services import atualizar_validacao_e_auditoria


class _ReverterCenario(Exception):
    pass


def _estado_soma(conexao):
    with conexao.cursor() as cursor:
        cursor.execute(
            "SELECT estado FROM criterios_validacao WHERE codigo = 'EST_SOMA'"
        )
        return cursor.fetchone()[0]


def main() -> None:
    load_dotenv()
    if sys.argv[1:] != ["CONFIRMAR_TESTES_ROLLBACK_20_11"]:
        raise SystemExit(
            "Uso: validar_bloqueios_motor_games.py CONFIRMAR_TESTES_ROLLBACK_20_11"
        )
    configuracao = carregar_configuracao_banco()
    if configuracao.nome != "games":
        raise RuntimeError("A validação exige GAME_DB_NAME=games.")
    resultados = {}
    with abrir_conexao(configuracao) as conexao:
        try:
            with conexao.transaction():
                with conexao.cursor() as cursor:
                    cursor.execute(
                        "UPDATE avaliacoes_validacao SET valor_esperado = "
                        "valor_esperado + 1 WHERE (id_resultado, id_criterio) = ("
                        "SELECT a.id_resultado, a.id_criterio FROM avaliacoes_validacao a "
                        "JOIN criterios_validacao c USING (id_criterio) "
                        "WHERE c.codigo = 'EST_SOMA' ORDER BY a.id_resultado LIMIT 1)"
                    )
                relatorio = atualizar_validacao_e_auditoria(conexao)
                resultados["divergencia"] = {
                    "reprovadas": relatorio.reprovadas,
                    "estado_criterio": _estado_soma(conexao),
                    "motivo": relatorio.motivo_estado_global,
                }
                if resultados["divergencia"] != {
                    "reprovadas": 1, "estado_criterio": "REPROVADO",
                    "motivo": "CRITERIOS_REPROVADOS",
                }:
                    raise AssertionError("Uma divergência não bloqueou a função.")
                raise _ReverterCenario
        except _ReverterCenario:
            pass

        try:
            with conexao.transaction():
                with conexao.cursor() as cursor:
                    cursor.execute(
                        "UPDATE avaliacoes_validacao SET referencia_conferida = FALSE, "
                        "estado_valor_esperado = NULL, valor_esperado = NULL, "
                        "referencia_origem = NULL, referencia_revisor = NULL, "
                        "referencia_observacao = NULL, referencia_conferida_em = NULL, "
                        "aprovado = NULL, diferenca = NULL WHERE "
                        "(id_resultado, id_criterio) = (SELECT a.id_resultado, "
                        "a.id_criterio FROM avaliacoes_validacao a "
                        "JOIN criterios_validacao c USING (id_criterio) "
                        "WHERE c.codigo = 'EST_SOMA' ORDER BY a.id_resultado LIMIT 1)"
                    )
                relatorio = atualizar_validacao_e_auditoria(conexao)
                resultados["pendencia"] = {
                    "pendentes": relatorio.pendentes,
                    "estado_criterio": _estado_soma(conexao),
                    "motivo": relatorio.motivo_estado_global,
                }
                if resultados["pendencia"] != {
                    "pendentes": 200, "estado_criterio": "PENDENTE",
                    "motivo": "REFERENCIAS_PENDENTES",
                }:
                    raise AssertionError("Uma pendência não bloqueou a função.")
                raise _ReverterCenario
        except _ReverterCenario:
            pass

        with conexao.cursor() as cursor:
            cursor.execute(
                "SELECT count(*) FROM avaliacoes_validacao WHERE aprovado = 'S'"
            )
            aprovadas_restauradas = cursor.fetchone()[0]
            cursor.execute(
                "SELECT count(*) FROM criterios_validacao WHERE estado = 'APROVADO'"
            )
            criterios_restaurados = cursor.fetchone()[0]
    if aprovadas_restauradas != 3800 or criterios_restaurados != 19:
        raise AssertionError("O rollback não restaurou a homologação aprovada.")
    resultados["rollback"] = {
        "avaliacoes_aprovadas": aprovadas_restauradas,
        "criterios_aprovados": criterios_restaurados,
    }
    print(json.dumps(resultados, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
