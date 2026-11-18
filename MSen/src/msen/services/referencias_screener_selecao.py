"""Trava de atualização das referências usadas pelo Screener da seleção."""

from collections.abc import Callable

from .homologacao_screener import (
    PERFIS_OBRIGATORIOS,
    EstadoHomologacaoScreener,
    consultar_homologacao_screener_no_banco,
)


class ReferenciasScreenerDesatualizadas(RuntimeError):
    """Impede o Screener de usar referências incompatíveis com os resultados."""

    def __init__(self, codigo: str, mensagem: str) -> None:
        super().__init__(mensagem)
        self.codigo = codigo


def _recusar(codigo: str, mensagem: str) -> None:
    raise ReferenciasScreenerDesatualizadas(codigo, mensagem)


def verificar_referencias_atualizadas(
    consultar_estado: Callable[[], EstadoHomologacaoScreener] | None = None,
) -> dict[str, object]:
    """Consulta e valida o estado completo antes da montagem do pacote."""

    consulta = consultar_estado or consultar_homologacao_screener_no_banco
    if not callable(consulta):
        raise TypeError("consultar_estado deve ser uma função ou nulo.")
    estado = consulta()
    if not isinstance(estado, EstadoHomologacaoScreener):
        raise TypeError("A consulta não retornou EstadoHomologacaoScreener.")
    if estado.total_resultados <= 0:
        _recusar("RESULTADOS_AUSENTES", "Não existem resultados históricos.")
    if not estado.atualizado:
        _recusar(
            "REFERENCIAS_DESATUALIZADAS",
            f"As referências estão desatualizadas: {estado.motivo}.",
        )
    if estado.quantidade_resultados != estado.total_resultados:
        _recusar(
            "QUANTIDADE_RESULTADOS_DIVERGENTE",
            "As referências não correspondem à quantidade atual de resultados.",
        )
    if not estado.criterios:
        _recusar("FILTROS_AUSENTES", "Não existem filtros homologados.")
    for criterio in estado.criterios:
        if (
            criterio.estado != "APROVADO"
            or criterio.exigidas <= 0
            or criterio.aprovadas != criterio.exigidas
            or criterio.pendentes != 0
            or criterio.assinaturas_divergentes != 0
        ):
            _recusar(
                "FILTRO_NAO_HOMOLOGADO",
                f"O filtro {criterio.codigo} não está integralmente aprovado.",
            )
    perfis = dict(estado.perfis)
    if set(perfis) != PERFIS_OBRIGATORIOS or any(
        quantidade != estado.total_resultados for quantidade in perfis.values()
    ):
        _recusar(
            "PERFIS_HISTORICOS_DESATUALIZADOS",
            "Os perfis históricos não correspondem aos resultados atuais.",
        )
    return {
        "atualizado": True,
        "motivo": estado.motivo,
        "quantidade_resultados": estado.total_resultados,
        "quantidade_filtros": len(estado.criterios),
        "quantidade_perfis": len(estado.perfis),
    }
