"""Valida o repositório de grupos exclusivamente em database temporário."""

from dataclasses import replace
import json
import sys

from dotenv import load_dotenv

from msen.config import carregar_configuracao_banco
from msen.database import ErroRepositorioGrupoPadrao, RepositorioGruposPadroes
from suporte_banco_integracao import conectar, validar_nome


def validar_repositorio(nome_database: str) -> dict[str, object]:
    """Exercita CRUD, códigos, duplicidade e proteção de grupo ocupado."""

    nome = validar_nome(nome_database)
    configuracao = replace(carregar_configuracao_banco(), nome=nome)
    with conectar(configuracao, nome) as conexao:
        repositorio = RepositorioGruposPadroes(conexao)
        iniciais = repositorio.listar()
        if tuple(item.grupo_cod for item in iniciais) != ("PG_001", "PG_002"):
            raise AssertionError(f"Catálogo inicial inesperado: {iniciais!r}")
        if not repositorio.possui_padroes("PG_001"):
            raise AssertionError("PG_001 deveria possuir os padrões iniciais.")

        criado = repositorio.criar("Mesma coluna", "Posições na mesma coluna")
        if criado.grupo_cod != "PG_003" or repositorio.possui_padroes("PG_003"):
            raise AssertionError(f"Grupo criado incorretamente: {criado!r}")

        editado = repositorio.atualizar_textos(
            "PG_003", "Mesma coluna da matriz", "Descrição revisada"
        )
        if editado.grupo_nome != "Mesma coluna da matriz":
            raise AssertionError("A edição do grupo não foi persistida.")

        erros: list[str] = []
        try:
            repositorio.criar(" mesma COLUNA da MATRIZ ", "Duplicado")
        except ErroRepositorioGrupoPadrao as erro:
            erros.append(erro.codigo)
        else:
            raise AssertionError("Nome normalizado duplicado foi aceito.")

        try:
            repositorio.excluir("PG_001")
        except ErroRepositorioGrupoPadrao as erro:
            erros.append(erro.codigo)
        else:
            raise AssertionError("Grupo ocupado foi excluído.")

        excluido = repositorio.excluir("PG_003")
        if excluido.grupo_cod != "PG_003":
            raise AssertionError("Grupo vazio incorreto foi excluído.")
        seguinte = repositorio.criar("Distribuição", "Outro conceito")
        if seguinte.grupo_cod != "PG_005":
            raise AssertionError(f"Código foi reutilizado: {seguinte.grupo_cod}")

        try:
            repositorio.possui_padroes("PG_999")
        except ErroRepositorioGrupoPadrao as erro:
            erros.append(erro.codigo)
        else:
            raise AssertionError("Grupo inexistente foi tratado como vazio.")

    return {
        "grupo_inicial": "PG_001",
        "crud": True,
        "codigo_nao_reutilizado": seguinte.grupo_cod,
        "erros_funcionais": erros,
    }


def main() -> None:
    """Executa a validação para o database temporário informado."""

    load_dotenv()
    if len(sys.argv) != 2:
        raise SystemExit(
            "Uso: validar_repositorio_grupos_padroes.py NOME_DATABASE_TEMPORARIO"
        )
    print(json.dumps(validar_repositorio(sys.argv[1]), ensure_ascii=False))


if __name__ == "__main__":
    main()
