"""Políticas em modo sombra que observam sem excluir combinações."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP

from msen.padroes.contratos import DetectorPadrao

from .adaptadores import ResultadoAvaliador
from .gerador import Combinacao


SEIS_CASAS = Decimal("0.000001")
CHAVE_TOLERANCIA = "tolerancia_ocorrencia_percentual"


class ErroPoliticaSombra(ValueError):
    """Indica dados inválidos ao preparar ou executar uma política sombra."""

    def __init__(self, codigo: str, mensagem: str) -> None:
        super().__init__(mensagem)
        self.codigo = codigo


@dataclass(frozen=True, slots=True)
class EvidenciaHistoricaPadrao:
    """Identifica a estatística reconciliada usada pela política de um padrão."""

    padrao_cod: str
    num_ocorrencias: int
    total_resultados: int
    reconciliada: bool
    identificacao: str

    def __post_init__(self) -> None:
        if not self.padrao_cod or not self.identificacao:
            raise ErroPoliticaSombra(
                "EVIDENCIA_INCOMPLETA", "Código e identificação são obrigatórios."
            )
        if self.total_resultados < 0 or not 0 <= self.num_ocorrencias <= self.total_resultados:
            raise ErroPoliticaSombra(
                "EVIDENCIA_INVALIDA", "Ocorrências e total histórico são inválidos."
            )


class PoliticaPadraoSombra:
    """Marca hipoteticamente baixa ocorrência, mas sempre aprova no funil."""

    def __init__(self, detector: DetectorPadrao, evidencia: EvidenciaHistoricaPadrao) -> None:
        if not callable(detector):
            raise TypeError("detector deve ser uma função chamável")
        if not isinstance(evidencia, EvidenciaHistoricaPadrao):
            raise TypeError("evidencia deve ser uma EvidenciaHistoricaPadrao")
        self._detector = detector
        self._evidencia = evidencia

    @staticmethod
    def _tolerancia(tolerancias: Mapping[str, float]) -> Decimal:
        """Valida e converte a tolerância percentual sem herdar erro binário."""

        valor = tolerancias.get(CHAVE_TOLERANCIA)
        if isinstance(valor, bool) or not isinstance(valor, (int, float)):
            raise ErroPoliticaSombra(
                "TOLERANCIA_AUSENTE", "A tolerância percentual é obrigatória."
            )
        decimal = Decimal(str(valor))
        if not Decimal("0") <= decimal <= Decimal("100"):
            raise ErroPoliticaSombra(
                "TOLERANCIA_INVALIDA", "A tolerância deve estar entre 0 e 100."
            )
        return decimal

    def __call__(
        self, combinacao: Combinacao, tolerancias: Mapping[str, float]
    ) -> ResultadoAvaliador:
        """Avalia a hipótese e registra a marca, sem reprovar a combinação."""

        tolerancia = self._tolerancia(tolerancias)
        evidencia = self._evidencia
        valores: dict[str, object] = {
            "padrao_cod": evidencia.padrao_cod,
            "modo": "sombra",
            "operador": "<=",
            "tolerancia_percentual": str(tolerancia),
            "num_ocorrencias": evidencia.num_ocorrencias,
            "total_resultados": evidencia.total_resultados,
            "reconciliacao": evidencia.identificacao,
            "reconciliada": evidencia.reconciliada,
            "marcaria_exclusao": False,
        }
        if not evidencia.reconciliada or evidencia.total_resultados == 0:
            valores.update(
                decisao_sombra="nao_avaliavel",
                motivo="Evidência histórica ausente ou não reconciliada.",
                detector_encontrou=None,
                percentual_historico=None,
            )
            return ResultadoAvaliador(True, valores)

        detectado = self._detector(combinacao)
        if not isinstance(detectado, bool):
            raise ErroPoliticaSombra(
                "RESPOSTA_DETECTOR_INVALIDA", "O detector deve devolver booleano."
            )
        percentual = (
            Decimal(evidencia.num_ocorrencias)
            * Decimal("100")
            / Decimal(evidencia.total_resultados)
        )
        marcaria = detectado and (
            Decimal(evidencia.num_ocorrencias) * Decimal("100")
            <= tolerancia * Decimal(evidencia.total_resultados)
        )
        valores.update(
            detector_encontrou=detectado,
            percentual_historico=str(
                percentual.quantize(SEIS_CASAS, rounding=ROUND_HALF_UP)
            ),
            marcaria_exclusao=marcaria,
            decisao_sombra="marcaria" if marcaria else "passaria",
            motivo=(
                "Padrão detectado e percentual menor ou igual à tolerância."
                if marcaria
                else "Padrão ausente ou percentual acima da tolerância."
            ),
        )
        return ResultadoAvaliador(True, valores)


class PoliticaPadraoAtiva:
    """Converte a marca validada da política sombra em reprovação efetiva."""

    def __init__(self, detector: DetectorPadrao, evidencia: EvidenciaHistoricaPadrao) -> None:
        self._sombra = PoliticaPadraoSombra(detector, evidencia)

    def __call__(
        self, combinacao: Combinacao, tolerancias: Mapping[str, float]
    ) -> ResultadoAvaliador:
        """Reprova somente quando a mesma avaliação sombra marcaria a combinação."""

        sombra = self._sombra(combinacao, tolerancias)
        valores = dict(sombra.valores)
        valores["modo"] = "ativo"
        marcaria = valores["marcaria_exclusao"] is True
        if valores.get("decisao_sombra") == "nao_avaliavel":
            valores["decisao"] = "nao_avaliavel"
        else:
            valores["decisao"] = "reprovou" if marcaria else "passou"
        return ResultadoAvaliador(not marcaria, valores)
