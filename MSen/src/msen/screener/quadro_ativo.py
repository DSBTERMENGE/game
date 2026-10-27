"""Monta o quadro visual e casos para validação humana do funil ativo."""

from __future__ import annotations

from pathlib import Path
from time import perf_counter

from .ativacao import criar_adaptadores_ativos
from .configuracao import carregar_configuracao_screener
from .gerador import gerar_amostra
from .quadro import executar_ensaio, serializar_quadro_avaliacao


def _casos_validacao(amostra, adaptadores, limite: int) -> list[dict[str, object]]:
    """Expõe decisões obtidas para o usuário informar o resultado esperado."""

    casos: list[dict[str, object]] = []
    for combinacao in amostra[:limite]:
        criterio_decisivo = None
        valores: dict[str, object] = {}
        for adaptador in adaptadores:
            decisao = adaptador.avaliar(combinacao)
            if not decisao.aprovada:
                criterio_decisivo = decisao.codigo_criterio
                valores = dict(decisao.valores)
                break
        obtido = "excluir" if criterio_decisivo else "aprovar"
        casos.append({
            "combinacao": list(combinacao),
            "resultado_esperado": None,
            "resultado_obtido": obtido,
            "criterio_decisivo": criterio_decisivo,
            "motivo": valores,
            "conformidade": None,
        })
    return casos


def gerar_quadro_screener(limite_validacoes: int = 30) -> dict[str, object]:
    """Executa a amostra protegida e serializa quadro e validações sem banco."""

    if isinstance(limite_validacoes, bool) or not 1 <= limite_validacoes <= 200:
        raise ValueError("limite_validacoes deve estar entre 1 e 200")
    raiz = Path(__file__).resolve().parents[3]
    configuracao = carregar_configuracao_screener(
        raiz / "config" / "screener.toml",
        raiz / "config" / "screener.local.toml",
    )
    amostra = gerar_amostra(configuracao)
    adaptadores = criar_adaptadores_ativos(configuracao)
    quadro = executar_ensaio(amostra, adaptadores, configuracao, relogio=perf_counter)
    dados = serializar_quadro_avaliacao(quadro)
    dados["validacoes"] = _casos_validacao(amostra, adaptadores, limite_validacoes)
    dados["aviso"] = (
        "Faixas experimentais; processamento integral bloqueado. "
        "A validação humana não altera banco nem configuração."
    )
    return dados
