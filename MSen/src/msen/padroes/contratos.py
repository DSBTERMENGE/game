"""Contratos de tipos compartilhados pelas funções detectoras de padrões."""

from typing import Protocol


class DetectorPadrao(Protocol):
    """Representa uma função que informa se seis dezenas possuem um padrão."""

    def __call__(self, dezenas: tuple[int, ...]) -> bool:
        """Recebe as dezenas e devolve verdadeiro quando o padrão é detectado."""

        ...
