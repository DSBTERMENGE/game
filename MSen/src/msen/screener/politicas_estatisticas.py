"""Políticas experimentais para medidas estatísticas das combinações."""

from __future__ import annotations

from collections.abc import Mapping
from decimal import Decimal, ROUND_HALF_UP

from msen.calculos import calcular_desvio_padrao_populacional

from .adaptadores import ResultadoAvaliador
from .gerador import Combinacao


SEIS_CASAS = Decimal("0.000001")
CHAVE_LIMITE_INFERIOR = "limite_inferior_media"
CHAVE_LIMITE_SUPERIOR = "limite_superior_media"
CHAVE_LIMITE_INFERIOR_DESVIO = "limite_inferior_desvio"
CHAVE_LIMITE_SUPERIOR_DESVIO = "limite_superior_desvio"
CHAVE_LIMITE_INFERIOR_MEDIANA = "limite_inferior_mediana"
CHAVE_LIMITE_SUPERIOR_MEDIANA = "limite_superior_mediana"


def media_fora_faixa(
    media: Decimal, limite_inferior: Decimal, limite_superior: Decimal
) -> bool:
    """Informa se a média está estritamente fora dos limites experimentais.

    Parâmetros:
        media: Média aritmética calculada para as seis dezenas.
        limite_inferior: Menor valor ainda aceito pela faixa.
        limite_superior: Maior valor ainda aceito pela faixa.

    Retorno:
        `True` somente para valor menor que o inferior ou maior que o superior.
    """

    if limite_inferior > limite_superior:
        raise ValueError("O limite inferior não pode superar o limite superior.")
    return media < limite_inferior or media > limite_superior


class PoliticaMediaSombra:
    """Marca médias fora da faixa P01/P99 sem reprovar combinações."""

    @staticmethod
    def _limites(tolerancias: Mapping[str, float]) -> tuple[Decimal, Decimal]:
        """Lê e valida os dois limites decimais configurados."""

        valores = (
            tolerancias.get(CHAVE_LIMITE_INFERIOR),
            tolerancias.get(CHAVE_LIMITE_SUPERIOR),
        )
        if any(isinstance(valor, bool) or not isinstance(valor, (int, float)) for valor in valores):
            raise ValueError("Os limites da média devem ser numéricos.")
        inferior, superior = (Decimal(str(valor)) for valor in valores)
        if inferior > superior:
            raise ValueError("O limite inferior não pode superar o limite superior.")
        return inferior, superior

    def __call__(
        self, combinacao: Combinacao, tolerancias: Mapping[str, float]
    ) -> ResultadoAvaliador:
        """Calcula a média e registra a decisão hipotética sem excluir."""

        inferior, superior = self._limites(tolerancias)
        media = (Decimal(sum(combinacao)) / Decimal(6)).quantize(
            SEIS_CASAS, rounding=ROUND_HALF_UP
        )
        marcaria = media_fora_faixa(media, inferior, superior)
        valores = {
            "modo": "sombra",
            "medida": "media_aritmetica",
            "media": str(media),
            "limite_inferior": str(inferior),
            "limite_superior": str(superior),
            "operador": "< inferior ou > superior",
            "marcaria_exclusao": marcaria,
            "decisao_sombra": "marcaria" if marcaria else "passaria",
        }
        return ResultadoAvaliador(True, valores)


class PoliticaMediaAtiva:
    """Converte a marca validada da média em reprovação efetiva."""

    def __init__(self) -> None:
        self._sombra = PoliticaMediaSombra()

    def __call__(
        self, combinacao: Combinacao, tolerancias: Mapping[str, float]
    ) -> ResultadoAvaliador:
        """Reprova somente médias estritamente fora da faixa configurada."""

        sombra = self._sombra(combinacao, tolerancias)
        valores = dict(sombra.valores)
        valores["modo"] = "ativo"
        marcaria = valores["marcaria_exclusao"] is True
        valores["decisao"] = "reprovou" if marcaria else "passou"
        return ResultadoAvaliador(not marcaria, valores)


def desvio_fora_faixa(
    desvio: Decimal, limite_inferior: Decimal, limite_superior: Decimal
) -> bool:
    """Informa se o desvio está estritamente fora da faixa experimental.

    Parâmetros:
        desvio: Desvio-padrão populacional das seis dezenas.
        limite_inferior: Menor valor ainda aceito.
        limite_superior: Maior valor ainda aceito.

    Retorno:
        `True` somente abaixo do limite inferior ou acima do superior.
    """

    return media_fora_faixa(desvio, limite_inferior, limite_superior)


class PoliticaDesvioPadraoSombra:
    """Marca desvios fora da faixa P01/P99 sem reprovar combinações."""

    @staticmethod
    def _limites(tolerancias: Mapping[str, float]) -> tuple[Decimal, Decimal]:
        """Lê e valida os limites experimentais do desvio-padrão."""

        valores = (
            tolerancias.get(CHAVE_LIMITE_INFERIOR_DESVIO),
            tolerancias.get(CHAVE_LIMITE_SUPERIOR_DESVIO),
        )
        if any(isinstance(valor, bool) or not isinstance(valor, (int, float)) for valor in valores):
            raise ValueError("Os limites do desvio-padrão devem ser numéricos.")
        inferior, superior = (Decimal(str(valor)) for valor in valores)
        if inferior > superior:
            raise ValueError("O limite inferior não pode superar o limite superior.")
        return inferior, superior

    def __call__(
        self, combinacao: Combinacao, tolerancias: Mapping[str, float]
    ) -> ResultadoAvaliador:
        """Calcula o desvio e registra a decisão hipotética sem excluir."""

        inferior, superior = self._limites(tolerancias)
        desvio = calcular_desvio_padrao_populacional(combinacao)
        marcaria = desvio_fora_faixa(desvio, inferior, superior)
        return ResultadoAvaliador(
            True,
            {
                "modo": "sombra",
                "medida": "desvio_padrao_populacional",
                "desvio_padrao": str(desvio),
                "limite_inferior": str(inferior),
                "limite_superior": str(superior),
                "operador": "< inferior ou > superior",
                "marcaria_exclusao": marcaria,
                "decisao_sombra": "marcaria" if marcaria else "passaria",
            },
        )


class PoliticaDesvioPadraoAtiva:
    """Converte a marca validada do desvio em reprovação efetiva."""

    def __init__(self) -> None:
        self._sombra = PoliticaDesvioPadraoSombra()

    def __call__(
        self, combinacao: Combinacao, tolerancias: Mapping[str, float]
    ) -> ResultadoAvaliador:
        """Reprova somente desvios estritamente fora da faixa configurada."""

        sombra = self._sombra(combinacao, tolerancias)
        valores = dict(sombra.valores)
        valores["modo"] = "ativo"
        marcaria = valores["marcaria_exclusao"] is True
        valores["decisao"] = "reprovou" if marcaria else "passou"
        return ResultadoAvaliador(not marcaria, valores)


def mediana_fora_faixa(
    mediana: Decimal, limite_inferior: Decimal, limite_superior: Decimal
) -> bool:
    """Informa se a mediana está estritamente fora da faixa experimental.

    Parâmetros:
        mediana: Mediana calculada a partir das seis dezenas.
        limite_inferior: Menor valor ainda aceito.
        limite_superior: Maior valor ainda aceito.

    Retorno:
        `True` somente abaixo do limite inferior ou acima do superior.
    """

    return media_fora_faixa(mediana, limite_inferior, limite_superior)


class PoliticaMedianaSombra:
    """Marca medianas fora da faixa P01/P99 sem reprovar combinações."""

    @staticmethod
    def _limites(tolerancias: Mapping[str, float]) -> tuple[Decimal, Decimal]:
        """Lê e valida os limites experimentais da mediana."""

        valores = (
            tolerancias.get(CHAVE_LIMITE_INFERIOR_MEDIANA),
            tolerancias.get(CHAVE_LIMITE_SUPERIOR_MEDIANA),
        )
        if any(isinstance(valor, bool) or not isinstance(valor, (int, float)) for valor in valores):
            raise ValueError("Os limites da mediana devem ser numéricos.")
        inferior, superior = (Decimal(str(valor)) for valor in valores)
        if inferior > superior:
            raise ValueError("O limite inferior não pode superar o limite superior.")
        return inferior, superior

    def __call__(
        self, combinacao: Combinacao, tolerancias: Mapping[str, float]
    ) -> ResultadoAvaliador:
        """Calcula a mediana e registra a decisão hipotética sem excluir."""

        inferior, superior = self._limites(tolerancias)
        ordenadas = sorted(combinacao)
        mediana = (Decimal(ordenadas[2]) + Decimal(ordenadas[3])) / Decimal(2)
        marcaria = mediana_fora_faixa(mediana, inferior, superior)
        return ResultadoAvaliador(
            True,
            {
                "modo": "sombra",
                "medida": "mediana",
                "mediana": str(mediana),
                "limite_inferior": str(inferior),
                "limite_superior": str(superior),
                "operador": "< inferior ou > superior",
                "marcaria_exclusao": marcaria,
                "decisao_sombra": "marcaria" if marcaria else "passaria",
            },
        )


class PoliticaMedianaAtiva:
    """Converte a marca validada da mediana em reprovação efetiva."""

    def __init__(self) -> None:
        self._sombra = PoliticaMedianaSombra()

    def __call__(
        self, combinacao: Combinacao, tolerancias: Mapping[str, float]
    ) -> ResultadoAvaliador:
        """Reprova somente medianas estritamente fora da faixa configurada."""

        sombra = self._sombra(combinacao, tolerancias)
        valores = dict(sombra.valores)
        valores["modo"] = "ativo"
        marcaria = valores["marcaria_exclusao"] is True
        valores["decisao"] = "reprovou" if marcaria else "passou"
        return ResultadoAvaliador(not marcaria, valores)
