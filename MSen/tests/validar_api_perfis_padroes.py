"""Valida a API de perfis contra um clone PostgreSQL temporário."""

from dataclasses import replace
import json
import sys

from dotenv import load_dotenv

from msen.api import criar_app
from msen.config import carregar_configuracao_banco
from msen.database import executar_migracoes
from msen.services import (
    calcular_perfil_grupo_sequenciais,
    recalcular_classificacoes_grupo_sequenciais,
)
from suporte_banco_integracao import (
    MIGRACOES,
    _restaurar_backup,
    conectar,
    criar_vazio,
    remover,
    validar_nome,
)


def validar(nome_database: str) -> dict[str, object]:
    """Testa contrato, cortes inclusivos e ausência de escrita pela API GET."""
    nome = validar_nome(nome_database)
    base = carregar_configuracao_banco()
    criar_vazio(base, nome)
    configuracao = replace(base, nome=nome)
    try:
        _restaurar_backup(base, nome)
        executar_migracoes(configuracao, MIGRACOES)
        with conectar(configuracao, nome) as conexao:
            recalcular_classificacoes_grupo_sequenciais(conexao)
            with conexao.cursor() as cursor:
                cursor.execute(
                    "SELECT numero_ap, data_resultado FROM resultados "
                    "ORDER BY numero_ap LIMIT 1 OFFSET 99"
                )
                numero_corte, data_corte = cursor.fetchone()
                cursor.execute(
                    "SELECT padrao_cod, num_oco, intervalo_medio, desv_padrao "
                    "FROM padroes_subgrupo WHERE padrao_cod IN "
                    "('PD_001', 'PD_002', 'PD_003') ORDER BY padrao_cod"
                )
                catalogo_antes = tuple(cursor.fetchall())

        def servico(limite, numero_ap_ate, data_ate):
            with conectar(configuracao, nome) as conexao:
                return calcular_perfil_grupo_sequenciais(
                    conexao,
                    limite_raridade_percentual=limite,
                    numero_ap_ate=numero_ap_ate,
                    data_ate=data_ate,
                    sincronizar_catalogo=False,
                )

        cliente = criar_app({
            "TESTING": True,
            "CALCULAR_PERFIL_PADROES": servico,
        }).test_client()
        completa = cliente.get(
            "/api/grupos-padroes/PG_001/perfil?limite_raridade=10"
        )
        por_numero = cliente.get(
            f"/api/grupos-padroes/PG_001/perfil?numero_ap_ate={numero_corte}"
        )
        por_data = cliente.get(
            "/api/grupos-padroes/PG_001/perfil?data_ate=" + data_corte.isoformat()
        )
        for resposta in (completa, por_numero, por_data):
            if resposta.status_code != 200:
                raise AssertionError(
                    f"API respondeu {resposta.status_code}: {resposta.get_json()}"
                )

        perfil_completo = completa.get_json()["perfil"]
        perfil_numero = por_numero.get_json()["perfil"]
        perfil_data = por_data.get_json()["perfil"]
        if perfil_completo["amostra"]["total_resultados"] != 3069:
            raise AssertionError("O perfil completo não retornou 3.069 resultados.")
        if perfil_completo["raridade"]["padroes_indicados"] != ["PD_002", "PD_003"]:
            raise AssertionError("A API não preservou a indicação histórica.")
        if perfil_numero["amostra"]["total_resultados"] != 100:
            raise AssertionError("O corte pelo centésimo concurso não foi inclusivo.")
        if perfil_data["amostra"]["total_resultados"] != 100:
            raise AssertionError("O corte pela centésima data não foi inclusivo.")

        with conectar(configuracao, nome) as conexao:
            with conexao.cursor() as cursor:
                cursor.execute(
                    "SELECT padrao_cod, num_oco, intervalo_medio, desv_padrao "
                    "FROM padroes_subgrupo WHERE padrao_cod IN "
                    "('PD_001', 'PD_002', 'PD_003') ORDER BY padrao_cod"
                )
                catalogo_depois = tuple(cursor.fetchall())
        if catalogo_depois != catalogo_antes:
            raise AssertionError("A API GET alterou o catálogo global.")

        return {
            "perfil_completo": perfil_completo["amostra"]["total_resultados"],
            "padroes_indicados": perfil_completo["raridade"]["padroes_indicados"],
            "corte_concurso": {
                "numero_ap_ate": numero_corte,
                "resultados": perfil_numero["amostra"]["total_resultados"],
            },
            "corte_data": {
                "data_ate": data_corte.isoformat(),
                "resultados": perfil_data["amostra"]["total_resultados"],
            },
            "get_sem_escrita": True,
        }
    finally:
        remover(base, nome)


def main() -> None:
    load_dotenv()
    if len(sys.argv) != 2:
        raise SystemExit("Uso: validar_api_perfis_padroes.py NOME_TEMPORARIO")
    print(json.dumps(validar(sys.argv[1]), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
