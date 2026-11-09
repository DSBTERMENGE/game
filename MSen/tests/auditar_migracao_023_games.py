"""Audita, sem alterar dados, a aplicação da migração 023 no banco games."""

import json

from dotenv import load_dotenv

from msen.config import carregar_configuracao_banco
from msen.database import abrir_conexao


def main() -> None:
    """Confere registro, colunas e cardinalidades após a migração."""

    load_dotenv()
    configuracao = carregar_configuracao_banco()
    if configuracao.nome != "games":
        raise RuntimeError("A auditoria exige GAME_DB_NAME=games.")

    with abrir_conexao(configuracao) as conexao:
        with conexao.cursor() as cursor:
            cursor.execute(
                "SELECT column_name, column_default, is_nullable "
                "FROM information_schema.columns "
                "WHERE table_schema = 'public' "
                "AND table_name = 'configuracoes_pesquisa_selecao' "
                "AND column_name IN ('horizonte_concursos', 'versao_assinatura') "
                "ORDER BY column_name"
            )
            colunas = cursor.fetchall()
            cursor.execute(
                "SELECT count(*) FROM schema_migrations WHERE versao = '023'"
            )
            migracao_registrada = cursor.fetchone()[0]
            cursor.execute("SELECT count(*) FROM configuracoes_pesquisa_selecao")
            configuracoes = cursor.fetchone()[0]
            cursor.execute("SELECT count(*) FROM execucoes_pesquisa_selecao")
            execucoes = cursor.fetchone()[0]

    esperado = [("versao_assinatura", "2", "NO")]
    if colunas != esperado or migracao_registrada != 1:
        raise RuntimeError(
            "A estrutura do banco não corresponde ao estado esperado da migração 023."
        )
    print(
        json.dumps(
            {
                "migracao_023_registrada": True,
                "horizonte_removido": True,
                "versao_assinatura": {
                    "padrao": 2,
                    "aceita_nulo": False,
                },
                "configuracoes": configuracoes,
                "execucoes": execucoes,
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
