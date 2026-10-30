"""Trava de homologação e cobertura antes da execução do Screener."""

from __future__ import annotations

from dataclasses import dataclass

from msen.config import carregar_configuracao_banco
from msen.database import abrir_conexao
from msen.validacao import criar_registro_criterios_producao


PERFIS_OBRIGATORIOS = frozenset({
    "EST_SOMA", "EST_MEDIA", "EST_MEDIANA", "EST_DESVIO_PADRAO",
    "GEO_EXTENSAO", "GEO_PERIMETRO", "GEO_REGIOES", "GEO_AREA",
    "GEO_CENTRO_X", "GEO_CENTRO_Y",
})


class ErroHomologacaoScreener(RuntimeError):
    def __init__(self, codigo: str, mensagem: str) -> None:
        super().__init__(mensagem)
        self.codigo = codigo


@dataclass(frozen=True, slots=True)
class CriterioHomologado:
    codigo: str
    estado: str
    assinatura_funcao: str
    assinatura_regra: str
    exigidas: int
    aprovadas: int
    pendentes: int
    assinaturas_divergentes: int


@dataclass(frozen=True, slots=True)
class EstadoHomologacaoScreener:
    atualizado: bool
    motivo: str
    quantidade_resultados: int | None
    total_resultados: int
    criterios: tuple[CriterioHomologado, ...]
    perfis: tuple[tuple[str, int], ...]


def validar_homologacao_screener(
    estado: EstadoHomologacaoScreener, *, codigos_carregados: set[str],
    codigos_padroes_selecionados: set[str],
) -> None:
    if not estado.atualizado:
        raise ErroHomologacaoScreener(
            "ALGORITMO_DESATUALIZADO", f"Validação e auditoria bloqueada: {estado.motivo}."
        )
    registro = criar_registro_criterios_producao().listar()
    esperado = {item.codigo: item for item in registro}
    encontrados = {item.codigo: item for item in estado.criterios}
    if set(encontrados) != set(esperado):
        raise ErroHomologacaoScreener("CATALOGO_DIVERGENTE", "O catálogo ativo diverge da produção.")
    for codigo, definicao in esperado.items():
        item = encontrados[codigo]
        if (
            item.estado != "APROVADO"
            or item.assinatura_funcao != definicao.assinatura_funcao
            or item.assinatura_regra != definicao.assinatura_regra
            or item.exigidas <= 0
            or item.aprovadas != item.exigidas
            or item.pendentes != 0
            or item.assinaturas_divergentes != 0
        ):
            raise ErroHomologacaoScreener(
                "FUNCAO_NAO_HOMOLOGADA", f"A função {codigo} não está integralmente aprovada."
            )
    padroes_producao = {codigo for codigo in esperado if codigo.startswith("PAD_")}
    if not codigos_padroes_selecionados.issubset(padroes_producao):
        raise ErroHomologacaoScreener(
            "PADRAO_NAO_HOMOLOGADO", "A seleção de raridade retornou padrão desconhecido."
        )
    cobertura_esperada = (set(esperado) - padroes_producao) | codigos_padroes_selecionados
    if codigos_carregados != cobertura_esperada:
        raise ErroHomologacaoScreener(
            "COBERTURA_DIVERGENTE", "Há filtro homologado ausente ou filtro extra no plano do Screener."
        )
    perfis = dict(estado.perfis)
    if (
        estado.quantidade_resultados != estado.total_resultados
        or set(perfis) != PERFIS_OBRIGATORIOS
        or any(quantidade != estado.total_resultados for quantidade in perfis.values())
    ):
        raise ErroHomologacaoScreener(
            "PERFIS_DESATUALIZADOS", "Os perfis operacionais não correspondem aos resultados atuais."
        )


def consultar_homologacao_screener_no_banco() -> EstadoHomologacaoScreener:
    with abrir_conexao(carregar_configuracao_banco()) as conexao, conexao.cursor() as cursor:
        cursor.execute(
            "SELECT atualizado, motivo, quantidade_resultados FROM estado_algoritmo_selecao WHERE id_estado = 1"
        )
        atualizado, motivo, quantidade = cursor.fetchone()
        cursor.execute("SELECT count(*) FROM resultados")
        total_resultados = cursor.fetchone()[0]
        cursor.execute(
            "SELECT c.codigo, c.estado, c.assinatura_funcao, c.assinatura_regra, count(*), "
            "count(*) FILTER (WHERE a.aprovado = 'S'), "
            "count(*) FILTER (WHERE NOT a.referencia_conferida OR NOT a.executado OR a.aprovado IS NULL), "
            "count(*) FILTER (WHERE a.assinatura_executada IS DISTINCT FROM c.assinatura_funcao) "
            "FROM criterios_validacao c JOIN avaliacoes_validacao a ON a.id_criterio = c.id_criterio "
            "JOIN amostras_validacao am ON am.id_resultado = a.id_resultado AND am.ativo "
            "WHERE c.ativo GROUP BY c.id_criterio ORDER BY c.codigo"
        )
        criterios = tuple(CriterioHomologado(
            linha[0], linha[1], linha[2].strip(), linha[3].strip(),
            linha[4], linha[5], linha[6], linha[7],
        ) for linha in cursor.fetchall())
        cursor.execute("SELECT codigo, quantidade_resultados FROM perfis_operacionais_atuais ORDER BY codigo")
        perfis = tuple(cursor.fetchall())
    return EstadoHomologacaoScreener(
        atualizado, motivo, quantidade, total_resultados, criterios, perfis,
    )
