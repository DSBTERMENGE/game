"""Registro que associa códigos estáveis às funções detectoras de padrões."""

import re

from .contratos import DetectorPadrao


PADRAO_CODIGO = re.compile(r"PD_[0-9]{3,}")


class CodigoPadraoInvalido(ValueError):
    """Indica que um código não segue o formato estável `PD_001`."""


class DetectorJaRegistrado(ValueError):
    """Indica tentativa de substituir silenciosamente um detector existente."""


class DetectorNaoRegistrado(LookupError):
    """Indica que ainda não existe função detectora para o código solicitado."""


class RegistroDetectores:
    """Mantém a associação explícita entre `padrao_cod` e detector Python."""

    def __init__(self) -> None:
        """Cria um registro vazio, sem antecipar detectores ainda não aprovados."""

        self._detectores: dict[str, DetectorPadrao] = {}

    def registrar(self, codigo: str, detector: DetectorPadrao) -> None:
        """Associa um código válido a um detector sem permitir substituição.

        Parâmetros:
            codigo: Código estável no formato `PD_001`.
            detector: Função que recebe as dezenas e devolve um booleano.

        Retorno:
            Nenhum. A associação fica disponível nesta instância do registro.

        Regra:
            Códigos inválidos, objetos não chamáveis e códigos já registrados
            são rejeitados para impedir vínculos ambíguos.
        """

        self._validar_codigo(codigo)
        if not callable(detector):
            raise TypeError("O detector de padrão deve ser uma função chamável.")
        if codigo in self._detectores:
            raise DetectorJaRegistrado(
                f"O código {codigo} já possui um detector registrado."
            )
        self._detectores[codigo] = detector

    def obter(self, codigo: str) -> DetectorPadrao:
        """Devolve o detector associado ao código informado.

        Parâmetros:
            codigo: Código estável no formato `PD_001`.

        Retorno:
            A função detectora anteriormente registrada.

        Regra:
            Um código válido, mas ainda sem função, produz erro explícito em vez
            de ser tratado como padrão que nunca ocorre.
        """

        self._validar_codigo(codigo)
        try:
            return self._detectores[codigo]
        except KeyError:
            raise DetectorNaoRegistrado(
                f"O código {codigo} ainda não possui detector Python."
            ) from None

    def contem(self, codigo: str) -> bool:
        """Informa se um código válido já possui detector registrado.

        Parâmetros:
            codigo: Código estável no formato `PD_001`.

        Retorno:
            `True` quando há detector e `False` quando ele está pendente.

        Regra:
            O formato do código é validado antes da consulta.
        """

        self._validar_codigo(codigo)
        return codigo in self._detectores

    def codigos_registrados(self) -> tuple[str, ...]:
        """Lista em ordem os códigos que já possuem detector.

        Retorno:
            Tupla ordenada de códigos. Um registro vazio devolve tupla vazia.
        """

        return tuple(sorted(self._detectores))

    @staticmethod
    def _validar_codigo(codigo: str) -> None:
        if not isinstance(codigo, str) or PADRAO_CODIGO.fullmatch(codigo) is None:
            raise CodigoPadraoInvalido(
                "O código do padrão deve seguir o formato PD_001."
            )
