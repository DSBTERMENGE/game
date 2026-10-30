"""Sincroniza o registro executável com o catálogo persistido de validação."""

from dataclasses import dataclass

import psycopg

from msen.database import RepositorioValidacao
from msen.validacao import RegistroCriteriosValidacao


class ExclusaoCriteriosNaoConfirmada(RuntimeError):
    def __init__(self, codigos: tuple[str, ...]) -> None:
        super().__init__("A exclusão de critérios exige confirmação explícita.")
        self.codigos = codigos


@dataclass(frozen=True, slots=True)
class ResultadoSincronizacaoCriterios:
    incluidos: tuple[str, ...]
    implementacoes_alteradas: tuple[str, ...]
    regras_alteradas: tuple[str, ...]
    excluidos: tuple[str, ...]
    avaliacoes_criadas: int

    @property
    def houve_alteracao(self) -> bool:
        return any((
            self.incluidos, self.implementacoes_alteradas,
            self.regras_alteradas, self.excluidos,
        ))


def sincronizar_criterios_validacao(
    conexao: psycopg.Connection,
    registro: RegistroCriteriosValidacao,
    *,
    confirmar_exclusoes: bool = False,
) -> ResultadoSincronizacaoCriterios:
    if not isinstance(conexao, psycopg.Connection):
        raise TypeError("A sincronização exige uma conexão Psycopg válida.")
    if not isinstance(registro, RegistroCriteriosValidacao):
        raise TypeError("registro deve ser RegistroCriteriosValidacao.")
    if not isinstance(confirmar_exclusoes, bool):
        raise TypeError("confirmar_exclusoes deve ser booleano.")

    definicoes = {item.codigo: item for item in registro.listar()}
    incluidos: list[str] = []
    implementacoes: list[str] = []
    regras: list[str] = []
    excluidos: list[str] = []

    with conexao.transaction():
        with conexao.cursor() as cursor:
            cursor.execute("SELECT id_grupo, grupo_cod FROM padroes_grupo")
            grupos = {codigo: identificador for identificador, codigo in cursor.fetchall()}
            faltantes = sorted({
                item.grupo_codigo for item in definicoes.values()
                if item.grupo_codigo is not None and item.grupo_codigo not in grupos
            })
            if faltantes:
                raise ValueError(f"Grupos do registro não cadastrados: {faltantes!r}")

            cursor.execute(
                "SELECT id_criterio, codigo, assinatura_funcao, assinatura_regra, "
                "categoria, tipo_resultado, precisao_decimal, id_grupo "
                "FROM criterios_validacao ORDER BY codigo"
            )
            existentes = {
                linha[1]: {
                    "id": linha[0], "funcao": linha[2].strip(),
                    "regra": linha[3].strip(),
                    "categoria": linha[4], "tipo": linha[5],
                    "precisao": linha[6], "id_grupo": linha[7],
                }
                for linha in cursor.fetchall()
            }
            ausentes_registro = tuple(sorted(set(existentes) - set(definicoes)))
            if ausentes_registro and not confirmar_exclusoes:
                raise ExclusaoCriteriosNaoConfirmada(ausentes_registro)

            for codigo, definicao in definicoes.items():
                id_grupo = (
                    None if definicao.grupo_codigo is None
                    else grupos[definicao.grupo_codigo]
                )
                atual = existentes.get(codigo)
                if atual is None:
                    cursor.execute(
                        "INSERT INTO criterios_validacao "
                        "(codigo, nome, categoria, funcao_python, tipo_resultado, "
                        "precisao_decimal, id_grupo, assinatura_funcao, "
                        "assinatura_regra, estado) VALUES "
                        "(%s, %s, %s, %s, %s, %s, %s, %s, %s, 'PENDENTE')",
                        (
                            definicao.codigo, definicao.nome, definicao.categoria,
                            definicao.funcao_python, definicao.tipo_resultado,
                            definicao.precisao_decimal, id_grupo,
                            definicao.assinatura_funcao, definicao.assinatura_regra,
                        ),
                    )
                    incluidos.append(codigo)
                    continue

                regra_mudou = atual["regra"] != definicao.assinatura_regra
                implementacao_mudou = atual["funcao"] != definicao.assinatura_funcao
                if not regra_mudou and not implementacao_mudou:
                    continue
                estrutura_atual = (
                    atual["categoria"], atual["tipo"],
                    atual["precisao"], atual["id_grupo"],
                )
                estrutura_nova = (
                    definicao.categoria, definicao.tipo_resultado,
                    definicao.precisao_decimal, id_grupo,
                )
                if estrutura_atual != estrutura_nova:
                    raise ValueError(
                        f"O critério {codigo} mudou de estrutura; use novo código estável."
                    )
                cursor.execute(
                    "UPDATE criterios_validacao SET nome = %s, categoria = %s, "
                    "funcao_python = %s, tipo_resultado = %s, precisao_decimal = %s, "
                    "id_grupo = %s, assinatura_funcao = %s, assinatura_regra = %s, "
                    "estado = 'PENDENTE', atualizado_em = CURRENT_TIMESTAMP "
                    "WHERE id_criterio = %s",
                    (
                        definicao.nome, definicao.categoria, definicao.funcao_python,
                        definicao.tipo_resultado, definicao.precisao_decimal, id_grupo,
                        definicao.assinatura_funcao, definicao.assinatura_regra,
                        atual["id"],
                    ),
                )
                if regra_mudou:
                    cursor.execute(
                        "UPDATE avaliacoes_validacao SET referencia_conferida = FALSE, "
                        "estado_valor_esperado = NULL, valor_esperado = NULL, "
                        "estado_padrao_esperado = NULL, "
                        "id_padrao_esperado = NULL, valor_calculado = NULL, "
                        "estado_valor_calculado = NULL, "
                        "estado_padrao_calculado = NULL, id_padrao_calculado = NULL, "
                        "executado = FALSE, assinatura_executada = NULL, aprovado = NULL, "
                        "diferenca = NULL, calculado_em = NULL, referencia_origem = NULL, "
                        "referencia_revisor = NULL, referencia_observacao = NULL, "
                        "referencia_conferida_em = NULL WHERE id_criterio = %s",
                        (atual["id"],),
                    )
                    regras.append(codigo)
                else:
                    cursor.execute(
                        "UPDATE avaliacoes_validacao SET estado_valor_calculado = NULL, "
                        "valor_calculado = NULL, "
                        "estado_padrao_calculado = NULL, id_padrao_calculado = NULL, "
                        "executado = FALSE, assinatura_executada = NULL, aprovado = NULL, "
                        "diferenca = NULL, calculado_em = NULL WHERE id_criterio = %s",
                        (atual["id"],),
                    )
                    implementacoes.append(codigo)

            for codigo in ausentes_registro:
                cursor.execute(
                    "DELETE FROM criterios_validacao WHERE id_criterio = %s",
                    (existentes[codigo]["id"],),
                )
                excluidos.append(codigo)

        criadas = RepositorioValidacao(conexao).sincronizar_avaliacoes_pendentes()
        if incluidos or implementacoes or regras or excluidos:
            with conexao.cursor() as cursor:
                cursor.execute(
                    "UPDATE estado_algoritmo_selecao SET atualizado = FALSE, "
                    "motivo = 'CATALOGO_DE_CRITERIOS_ALTERADO', "
                    "alterado_em = CURRENT_TIMESTAMP WHERE id_estado = 1"
                )

    return ResultadoSincronizacaoCriterios(
        tuple(incluidos), tuple(implementacoes), tuple(regras), tuple(excluidos), criadas
    )
