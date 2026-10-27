"""Políticas experimentais para medidas geométricas das combinações."""

from __future__ import annotations

from collections.abc import Mapping
from decimal import Decimal, ROUND_HALF_UP

from msen.geometria import calcular_extensao_aberta

from .adaptadores import ResultadoAvaliador
from .gerador import Combinacao


DOZE_CASAS = Decimal("0.000000000001")
CHAVE_LIMITE_INFERIOR = "limite_inferior_extensao"
CHAVE_LIMITE_SUPERIOR = "limite_superior_extensao"


def extensao_fora_faixa(
    extensao: Decimal, limite_inferior: Decimal, limite_superior: Decimal
) -> bool:
    """Informa se a extensão está estritamente fora da faixa experimental.

    Parâmetros:
        extensao: Soma euclidiana dos cinco segmentos do caminho aberto.
        limite_inferior: Menor extensão ainda aceita.
        limite_superior: Maior extensão ainda aceita.

    Retorno:
        `True` somente abaixo do limite inferior ou acima do superior.
    """

    if limite_inferior > limite_superior:
        raise ValueError("O limite inferior não pode superar o limite superior.")
    return extensao < limite_inferior or extensao > limite_superior


class PoliticaExtensaoSombra:
    """Marca extensões fora da faixa P01/P99 sem reprovar combinações."""

    @staticmethod
    def _limites(tolerancias: Mapping[str, float]) -> tuple[Decimal, Decimal]:
        """Lê e valida os limites experimentais da extensão."""

        valores = (
            tolerancias.get(CHAVE_LIMITE_INFERIOR),
            tolerancias.get(CHAVE_LIMITE_SUPERIOR),
        )
        if any(isinstance(valor, bool) or not isinstance(valor, (int, float)) for valor in valores):
            raise ValueError("Os limites da extensão devem ser numéricos.")
        inferior, superior = (Decimal(str(valor)) for valor in valores)
        if inferior > superior:
            raise ValueError("O limite inferior não pode superar o limite superior.")
        return inferior, superior

    def __call__(
        self, combinacao: Combinacao, tolerancias: Mapping[str, float]
    ) -> ResultadoAvaliador:
        """Calcula a extensão e registra a decisão hipotética sem excluir."""

        inferior, superior = self._limites(tolerancias)
        extensao = calcular_extensao_aberta(combinacao).quantize(
            DOZE_CASAS, rounding=ROUND_HALF_UP
        )
        marcaria = extensao_fora_faixa(extensao, inferior, superior)
        return ResultadoAvaliador(
            True,
            {
                "modo": "sombra",
                "medida": "extensao_aberta",
                "extensao_aberta": str(extensao),
                "limite_inferior": str(inferior),
                "limite_superior": str(superior),
                "operador": "< inferior ou > superior",
                "marcaria_exclusao": marcaria,
                "decisao_sombra": "marcaria" if marcaria else "passaria",
            },
        )


class PoliticaExtensaoAtiva:
    """Exclui combinações cuja extensão aberta está fora da faixa aprovada."""

    def __call__(
        self, combinacao: Combinacao, tolerancias: Mapping[str, float]
    ) -> ResultadoAvaliador:
        """Aplica a mesma medição validada no modo sombra e efetiva a decisão."""

        sombra = PoliticaExtensaoSombra()(combinacao, tolerancias)
        valores = dict(sombra.valores)
        fora_faixa = bool(valores["marcaria_exclusao"])
        valores["modo"] = "ativo"
        valores["decisao"] = "excluir" if fora_faixa else "aprovar"
        return ResultadoAvaliador(not fora_faixa, valores)
