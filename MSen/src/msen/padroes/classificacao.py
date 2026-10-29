"""Classificadores exclusivos dos resultados dentro dos grupos de padrões."""

from dataclasses import dataclass
from collections.abc import Sequence

from .iniciais import (
    CODIGO_DUAS_SEQUENCIAIS,
    CODIGO_MAIS_DE_TRES_SEQUENCIAIS,
    CODIGO_TRES_SEQUENCIAIS,
)
from .sequenciais import AnaliseSequencial, analisar_dezenas_sequenciais


CODIGO_GRUPO_SEQUENCIAIS = "PG_001"


@dataclass(frozen=True, slots=True)
class ClassificacaoGrupoSequenciais:
    """Decisão exclusiva do grupo PG_001 acompanhada de sua evidência."""

    grupo_cod: str
    padrao_cod: str | None
    evidencia: AnaliseSequencial


def classificar_grupo_dezenas_sequenciais(
    dezenas: Sequence[int],
) -> ClassificacaoGrupoSequenciais:
    """Classifica as seis dezenas pelo maior bloco consecutivo do grupo PG_001.

    Retorna `PD_001` para maior bloco de dois, `PD_002` para três e `PD_003`
    para quatro, cinco ou seis. Quando o maior bloco possui somente uma dezena,
    não identifica padrão. A dezena 60 não é consecutiva da dezena 01.
    """

    evidencia = analisar_dezenas_sequenciais(dezenas)
    codigos_por_tamanho = {
        2: CODIGO_DUAS_SEQUENCIAIS,
        3: CODIGO_TRES_SEQUENCIAIS,
    }
    if evidencia.maior_tamanho > 3:
        padrao_cod = CODIGO_MAIS_DE_TRES_SEQUENCIAIS
    else:
        padrao_cod = codigos_por_tamanho.get(evidencia.maior_tamanho)
    return ClassificacaoGrupoSequenciais(
        grupo_cod=CODIGO_GRUPO_SEQUENCIAIS,
        padrao_cod=padrao_cod,
        evidencia=evidencia,
    )
