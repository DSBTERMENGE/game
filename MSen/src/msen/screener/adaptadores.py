"""Adaptadores isolados para as três categorias de critério do screener."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from types import MappingProxyType
from typing import TypeAlias

from .configuracao import ConfiguracaoCriterio
from .funil import DecisaoCriterio
from .gerador import Combinacao


class ErroAdaptadorCriterio(ValueError):
    """Indica construção ou resposta inválida de um adaptador de critério."""

    def __init__(self, codigo: str, mensagem: str) -> None:
        super().__init__(mensagem)
        self.codigo = codigo


@dataclass(frozen=True, slots=True)
class ResultadoAvaliador:
    """Resultado neutro produzido pela futura função específica do critério."""

    aprovada: bool
    valores: Mapping[str, object]


AvaliadorCriterio: TypeAlias = Callable[
    [Combinacao, Mapping[str, float]], ResultadoAvaliador
]


class _AdaptadorBase:
    """Converte a resposta de uma função específica no contrato do funil."""

    categoria = ""

    def __init__(
        self,
        codigo: str,
        configuracao: ConfiguracaoCriterio,
        avaliador: AvaliadorCriterio | None = None,
    ) -> None:
        if not isinstance(codigo, str) or not codigo.strip():
            raise ErroAdaptadorCriterio(
                "CODIGO_INVALIDO", "O adaptador deve possuir um código preenchido."
            )
        if not isinstance(configuracao, ConfiguracaoCriterio):
            raise TypeError("configuracao deve ser uma ConfiguracaoCriterio validada")
        if configuracao.habilitado and avaliador is None:
            raise ErroAdaptadorCriterio(
                "AVALIADOR_AUSENTE", "Um critério habilitado exige função avaliadora."
            )
        self.codigo = codigo.strip()
        self.configuracao = configuracao
        self._avaliador = avaliador

    def avaliar(self, combinacao: Combinacao) -> DecisaoCriterio:
        """Avalia ou, quando desabilitado, aprova sem chamar a função futura."""

        if not self.configuracao.habilitado:
            return DecisaoCriterio(
                aprovada=True,
                codigo_criterio=self.codigo,
                valores=MappingProxyType(
                    {"categoria": self.categoria, "habilitado": False}
                ),
            )
        resultado = self._avaliador(combinacao, self.configuracao.tolerancias)
        if not isinstance(resultado, ResultadoAvaliador):
            raise ErroAdaptadorCriterio(
                "RESULTADO_INVALIDO", "O avaliador deve retornar ResultadoAvaliador."
            )
        if not isinstance(resultado.aprovada, bool):
            raise ErroAdaptadorCriterio(
                "DECISAO_INVALIDA", "A decisão do avaliador deve ser booleana."
            )
        valores = dict(resultado.valores)
        valores.setdefault("categoria", self.categoria)
        valores.setdefault("habilitado", True)
        return DecisaoCriterio(
            aprovada=resultado.aprovada,
            codigo_criterio=self.codigo,
            valores=MappingProxyType(valores),
        )


class AdaptadorPadroesHistoricos(_AdaptadorBase):
    """Liga uma função de padrão histórico ao contrato do funil."""

    categoria = "padroes_historicos"


class AdaptadorMedidasEstatisticas(_AdaptadorBase):
    """Liga uma função de medida estatística ao contrato do funil."""

    categoria = "medidas_estatisticas"


class AdaptadorMedidasGeometricas(_AdaptadorBase):
    """Liga uma função de medida geométrica ao contrato do funil."""

    categoria = "medidas_geometricas"
