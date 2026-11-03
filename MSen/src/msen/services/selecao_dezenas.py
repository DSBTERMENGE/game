"""Motor puro do primeiro screener: seleção de dezenas por concurso-alvo."""

from __future__ import annotations

from dataclasses import dataclass, replace
from decimal import Decimal, ROUND_CEILING, ROUND_FLOOR, ROUND_HALF_UP, localcontext
from typing import Iterable

from .configuracao_selecao_dezenas import ConfiguracaoSelecaoDezenas


SEIS_CASAS = Decimal("0.000001")
DOZE_CASAS = Decimal("0.000000000001")


class ErroSelecaoDezenas(ValueError):
    def __init__(self, codigo: str, mensagem: str) -> None:
        super().__init__(mensagem)
        self.codigo = codigo


@dataclass(frozen=True, slots=True)
class EstatisticaDezenaCorte:
    dezena: int
    ultima_ocorrencia: int | None
    quantidade_intervalos: int
    media_intervalos: Decimal | None
    desvio_padrao: Decimal | None


@dataclass(frozen=True, slots=True)
class AvaliacaoSelecaoDezena:
    dezena: int
    estado_avaliacao: str
    ultima_ocorrencia: int | None
    quantidade_intervalos: int
    media_intervalos: Decimal | None
    desvio_padrao: Decimal | None
    centro_original: Decimal | None
    centro_ajustado: Decimal | None
    limite_inferior_exato: Decimal | None
    limite_superior_exato: Decimal | None
    limite_inferior: int | None
    limite_superior: int | None
    distancia_normalizada: Decimal | None
    distancia_absoluta: Decimal | None
    posicao_ranking: int | None
    aprovada: bool
    retornada: bool

    @property
    def motivo_decisao(self) -> str:
        if self.estado_avaliacao == "SEM_BASE":
            return "Sem intervalos simples suficientes para calcular a faixa."
        if self.estado_avaliacao == "FORA_FAIXA":
            return "O concurso-alvo está fora da faixa operacional da dezena."
        if self.estado_avaliacao == "APROVADA_NAO_RETORNADA":
            return "Aprovada pela faixa, mas excedeu a quantidade fixa configurada."
        return "Aprovada pela faixa e incluída no conjunto retornado."


@dataclass(frozen=True, slots=True)
class ResultadoSelecaoDezenas:
    numero_concurso_alvo: int
    numero_concurso_corte: int
    avaliacoes: tuple[AvaliacaoSelecaoDezena, ...]
    dezenas_aprovadas: tuple[int, ...]
    dezenas_retornadas: tuple[int, ...]
    quantidade_configurada: int | None
    limite_nao_atingido: bool
    avaliavel: bool
    motivo: str | None


def _validar_estatisticas(
    estatisticas: Iterable[EstatisticaDezenaCorte],
) -> tuple[EstatisticaDezenaCorte, ...]:
    itens = tuple(estatisticas)
    if len(itens) != 60 or {item.dezena for item in itens} != set(range(1, 61)):
        raise ErroSelecaoDezenas(
            "COBERTURA_INCOMPLETA",
            "O corte deve fornecer exatamente uma estatística para cada dezena de 1 a 60.",
        )
    for item in itens:
        sem_base = item.quantidade_intervalos == 0
        if sem_base and any((
            item.ultima_ocorrencia is not None,
            item.media_intervalos is not None,
            item.desvio_padrao is not None,
        )):
            raise ErroSelecaoDezenas("ESTATISTICA_INCOERENTE", "Estado sem base incoerente.")
        if not sem_base and (
            item.quantidade_intervalos < 0
            or item.ultima_ocorrencia is None
            or item.media_intervalos is None
            or item.desvio_padrao is None
            or item.media_intervalos <= 0
            or item.desvio_padrao < 0
        ):
            raise ErroSelecaoDezenas("ESTATISTICA_INCOERENTE", "Estatística de intervalo incoerente.")
    return tuple(sorted(itens, key=lambda item: item.dezena))


def _quantizar(valor: Decimal) -> Decimal:
    return valor.quantize(SEIS_CASAS, rounding=ROUND_HALF_UP)


def selecionar_dezenas_para_alvo(
    estatisticas: Iterable[EstatisticaDezenaCorte],
    configuracao: ConfiguracaoSelecaoDezenas,
    *,
    numero_concurso_alvo: int,
    numero_concurso_corte: int,
) -> ResultadoSelecaoDezenas:
    """Avalia as 60 dezenas sem receber nem consultar o resultado do alvo."""

    if not isinstance(configuracao, ConfiguracaoSelecaoDezenas):
        raise TypeError("configuracao deve ser ConfiguracaoSelecaoDezenas.")
    if (
        isinstance(numero_concurso_alvo, bool)
        or not isinstance(numero_concurso_alvo, int)
        or isinstance(numero_concurso_corte, bool)
        or not isinstance(numero_concurso_corte, int)
        or numero_concurso_corte <= 0
        or numero_concurso_alvo <= numero_concurso_corte
    ):
        raise ErroSelecaoDezenas("CORTE_INVALIDO", "O alvo deve ser posterior ao corte positivo.")

    itens = _validar_estatisticas(estatisticas)
    calculadas: list[AvaliacaoSelecaoDezena] = []
    chaves_ranking: dict[int, tuple[Decimal, Decimal, int]] = {}
    with localcontext() as contexto:
        contexto.prec = 50
        alvo_decimal = Decimal(numero_concurso_alvo)
        for item in itens:
            if item.quantidade_intervalos == 0:
                calculadas.append(AvaliacaoSelecaoDezena(
                    dezena=item.dezena,
                    estado_avaliacao="SEM_BASE",
                    ultima_ocorrencia=None,
                    quantidade_intervalos=0,
                    media_intervalos=None,
                    desvio_padrao=None,
                    centro_original=None,
                    centro_ajustado=None,
                    limite_inferior_exato=None,
                    limite_superior_exato=None,
                    limite_inferior=None,
                    limite_superior=None,
                    distancia_normalizada=None,
                    distancia_absoluta=None,
                    posicao_ranking=None,
                    aprovada=False,
                    retornada=False,
                ))
                continue

            media = item.media_intervalos
            desvio = item.desvio_padrao
            centro_original_exato = Decimal(item.ultima_ocorrencia) + media
            centro_ajustado_exato = centro_original_exato + configuracao.fator_j * desvio
            meia_largura = configuracao.fator_k * desvio
            inferior_exato = centro_ajustado_exato - meia_largura
            superior_exato = centro_ajustado_exato + meia_largura
            inferior = int(inferior_exato.to_integral_value(rounding=ROUND_FLOOR))
            superior = int(superior_exato.to_integral_value(rounding=ROUND_CEILING))
            distancia_absoluta = abs(alvo_decimal - centro_ajustado_exato)
            distancia_normalizada = (
                distancia_absoluta / desvio if desvio > 0
                else (Decimal(0) if distancia_absoluta == 0 else None)
            )
            aprovada = inferior <= numero_concurso_alvo <= superior
            calculadas.append(AvaliacaoSelecaoDezena(
                dezena=item.dezena,
                estado_avaliacao=("APROVADA_NAO_RETORNADA" if aprovada else "FORA_FAIXA"),
                ultima_ocorrencia=item.ultima_ocorrencia,
                quantidade_intervalos=item.quantidade_intervalos,
                media_intervalos=media,
                desvio_padrao=desvio,
                centro_original=_quantizar(centro_original_exato),
                centro_ajustado=_quantizar(centro_ajustado_exato),
                limite_inferior_exato=_quantizar(inferior_exato),
                limite_superior_exato=_quantizar(superior_exato),
                limite_inferior=inferior,
                limite_superior=superior,
                distancia_normalizada=(
                    None if distancia_normalizada is None
                    else distancia_normalizada.quantize(DOZE_CASAS, rounding=ROUND_HALF_UP)
                ),
                distancia_absoluta=_quantizar(distancia_absoluta),
                posicao_ranking=None,
                aprovada=aprovada,
                retornada=False,
            ))
            chaves_ranking[item.dezena] = (
                distancia_normalizada if distancia_normalizada is not None else Decimal("Infinity"),
                distancia_absoluta,
                item.dezena,
            )

    ordem = sorted(chaves_ranking, key=chaves_ranking.__getitem__)
    ranking = {dezena: posicao for posicao, dezena in enumerate(ordem, start=1)}
    calculadas = [
        item if item.dezena not in ranking
        else replace(item, posicao_ranking=ranking[item.dezena])
        for item in calculadas
    ]
    aprovadas_ordenadas = sorted(
        (item for item in calculadas if item.aprovada),
        key=lambda item: chaves_ranking[item.dezena],
    )
    quantidade = configuracao.quantidade_dezenas
    retornadas_ordenadas = (
        aprovadas_ordenadas if quantidade is None else aprovadas_ordenadas[:quantidade]
    )
    retornadas = {item.dezena for item in retornadas_ordenadas}
    calculadas = [
        replace(
            item,
            estado_avaliacao="APROVADA_RETORNADA",
            retornada=True,
        ) if item.dezena in retornadas else item
        for item in calculadas
    ]
    tem_base = bool(chaves_ranking)
    limite_nao_atingido = quantidade is not None and len(aprovadas_ordenadas) < quantidade
    return ResultadoSelecaoDezenas(
        numero_concurso_alvo=numero_concurso_alvo,
        numero_concurso_corte=numero_concurso_corte,
        avaliacoes=tuple(calculadas),
        dezenas_aprovadas=tuple(sorted(item.dezena for item in aprovadas_ordenadas)),
        dezenas_retornadas=tuple(sorted(retornadas)),
        quantidade_configurada=quantidade,
        limite_nao_atingido=limite_nao_atingido,
        avaliavel=tem_base,
        motivo=None if tem_base else "Nenhuma dezena possui intervalo simples suficiente no corte.",
    )
