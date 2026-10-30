"""Motor incremental das fotografias históricas de frequência."""

from __future__ import annotations

from bisect import insort
from dataclasses import dataclass, field
from decimal import Decimal, ROUND_CEILING, ROUND_FLOOR, ROUND_HALF_UP, localcontext
from typing import Iterable

from msen.modelos import ResultadoEntrada

from .configuracao_frequencia import ConfiguracaoFrequencia


SEIS_CASAS = Decimal("0.000001")
ORDEM_EVENTOS = ("SIMPLES", "2VS", "3VS")


class ErroMotorFrequencia(ValueError):
    def __init__(self, codigo: str, mensagem: str, *, concurso: int | None = None) -> None:
        super().__init__(mensagem)
        self.codigo = codigo
        self.concurso = concurso


@dataclass(frozen=True, slots=True)
class FotografiaFrequencia:
    numero_do_concurso: int
    dezena: int
    tipo_evento: str
    quantidade_ocorrencias: int
    quantidade_intervalos: int
    intervalo_minimo: int | None
    intervalo_maximo: int | None
    media_intervalos: Decimal | None
    mediana_intervalos: Decimal | None
    desvio_padrao_intervalos: Decimal | None
    previsao_central: Decimal | None
    limite_inferior_exato: Decimal | None
    limite_superior_exato: Decimal | None
    concurso_limite_inferior: int | None
    concurso_limite_superior: int | None


@dataclass(slots=True)
class _ResumoEventos:
    quantidade: int = 0
    ultimo_evento: int | None = None
    intervalos_ordenados: list[int] = field(default_factory=list)
    soma_intervalos: int = 0
    soma_quadrados: int = 0
    intervalo_minimo: int | None = None
    intervalo_maximo: int | None = None

    def registrar(self, concurso: int) -> None:
        if self.ultimo_evento is not None:
            intervalo = concurso - self.ultimo_evento
            if intervalo <= 0:
                raise RuntimeError("Eventos devem ser registrados em ordem crescente.")
            insort(self.intervalos_ordenados, intervalo)
            self.soma_intervalos += intervalo
            self.soma_quadrados += intervalo * intervalo
            self.intervalo_minimo = (
                intervalo if self.intervalo_minimo is None
                else min(self.intervalo_minimo, intervalo)
            )
            self.intervalo_maximo = (
                intervalo if self.intervalo_maximo is None
                else max(self.intervalo_maximo, intervalo)
            )
        self.quantidade += 1
        self.ultimo_evento = concurso

    def fotografar(
        self,
        *,
        numero_do_concurso: int,
        dezena: int,
        tipo_evento: str,
        multiplicador_desvio: Decimal,
    ) -> FotografiaFrequencia:
        quantidade_intervalos = len(self.intervalos_ordenados)
        if quantidade_intervalos == 0:
            return FotografiaFrequencia(
                numero_do_concurso, dezena, tipo_evento, self.quantidade, 0,
                None, None, None, None, None, None, None, None, None, None,
            )

        with localcontext() as contexto:
            contexto.prec = 50
            quantidade = Decimal(quantidade_intervalos)
            media_exata = Decimal(self.soma_intervalos) / quantidade
            variancia = (
                Decimal(self.soma_quadrados) / quantidade - media_exata ** 2
            )
            if variancia < 0 and abs(variancia) < Decimal("1e-40"):
                variancia = Decimal(0)
            desvio_exato = variancia.sqrt()
            previsao_exata = Decimal(self.ultimo_evento) + media_exata
            limite_inferior_exato = (
                previsao_exata - multiplicador_desvio * desvio_exato
            )
            limite_superior_exato = (
                previsao_exata + multiplicador_desvio * desvio_exato
            )
            limite_inferior = max(
                self.ultimo_evento + 1,
                int(limite_inferior_exato.to_integral_value(rounding=ROUND_FLOOR)),
            )
            limite_superior = int(
                limite_superior_exato.to_integral_value(rounding=ROUND_CEILING)
            )
            limite_superior = max(limite_superior, limite_inferior)

        meio = quantidade_intervalos // 2
        if quantidade_intervalos % 2:
            mediana_exata = Decimal(self.intervalos_ordenados[meio])
        else:
            mediana_exata = (
                Decimal(self.intervalos_ordenados[meio - 1])
                + Decimal(self.intervalos_ordenados[meio])
            ) / Decimal(2)

        arredondar = lambda valor: valor.quantize(SEIS_CASAS, rounding=ROUND_HALF_UP)
        return FotografiaFrequencia(
            numero_do_concurso=numero_do_concurso,
            dezena=dezena,
            tipo_evento=tipo_evento,
            quantidade_ocorrencias=self.quantidade,
            quantidade_intervalos=quantidade_intervalos,
            intervalo_minimo=self.intervalo_minimo,
            intervalo_maximo=self.intervalo_maximo,
            media_intervalos=arredondar(media_exata),
            mediana_intervalos=arredondar(mediana_exata),
            desvio_padrao_intervalos=arredondar(desvio_exato),
            previsao_central=arredondar(previsao_exata),
            limite_inferior_exato=arredondar(limite_inferior_exato),
            limite_superior_exato=arredondar(limite_superior_exato),
            concurso_limite_inferior=limite_inferior,
            concurso_limite_superior=limite_superior,
        )


class MotorFrequenciaAcumulada:
    """Acumula resultados sem acessar concursos posteriores ao corte atual."""

    def __init__(self, configuracao: ConfiguracaoFrequencia) -> None:
        if not isinstance(configuracao, ConfiguracaoFrequencia):
            raise TypeError("configuracao deve ser ConfiguracaoFrequencia.")
        if configuracao.regra_janela != "INICIO_FIXO_FINAL_EXPANSIVO":
            raise ErroMotorFrequencia(
                "REGRA_JANELA_NAO_SUPORTADA", "A regra de janela não é suportada."
            )
        self.configuracao = configuracao
        self.primeiro_corte = (
            configuracao.concurso_inicial + configuracao.tamanho_inicial - 1
        )
        self._ultimo_concurso: int | None = None
        self._ultima_ocorrencia = [None] * 61
        self._sequencia = [0] * 61
        self._resumos = {
            tipo: [_ResumoEventos() for _ in range(61)] for tipo in ORDEM_EVENTOS
        }

    @property
    def ultimo_concurso_processado(self) -> int | None:
        return self._ultimo_concurso

    def _tipos_solicitados(self) -> tuple[str, ...]:
        if self.configuracao.tipo_evento == "TODOS":
            return ORDEM_EVENTOS
        return (self.configuracao.tipo_evento,)

    def processar(
        self, resultado: ResultadoEntrada, *, emitir: bool = True
    ) -> tuple[FotografiaFrequencia, ...]:
        if not isinstance(resultado, ResultadoEntrada):
            raise TypeError("O motor aceita somente ResultadoEntrada.")
        esperado = (
            self.configuracao.concurso_inicial
            if self._ultimo_concurso is None else self._ultimo_concurso + 1
        )
        if resultado.numero_ap != esperado:
            codigo = (
                "CONCURSO_FORA_DE_ORDEM"
                if resultado.numero_ap < esperado else "LACUNA_HISTORICA"
            )
            raise ErroMotorFrequencia(
                codigo,
                f"Era esperado o concurso {esperado}, recebido {resultado.numero_ap}.",
                concurso=resultado.numero_ap,
            )

        concurso = resultado.numero_ap
        presentes = set(resultado.resultados)
        for dezena in presentes:
            self._resumos["SIMPLES"][dezena].registrar(concurso)
            if self._ultima_ocorrencia[dezena] == concurso - 1:
                self._sequencia[dezena] += 1
            else:
                self._sequencia[dezena] = 1
            self._ultima_ocorrencia[dezena] = concurso
            if self._sequencia[dezena] >= 2:
                self._resumos["2VS"][dezena].registrar(concurso)
            if self._sequencia[dezena] >= 3:
                self._resumos["3VS"][dezena].registrar(concurso)

        self._ultimo_concurso = concurso
        if not emitir or concurso < self.primeiro_corte:
            return ()
        return tuple(
            self._resumos[tipo][dezena].fotografar(
                numero_do_concurso=concurso,
                dezena=dezena,
                tipo_evento=tipo,
                multiplicador_desvio=self.configuracao.parametro_faixa,
            )
            for tipo in self._tipos_solicitados()
            for dezena in range(1, 61)
        )

    def processar_varios(
        self, resultados: Iterable[ResultadoEntrada]
    ) -> tuple[FotografiaFrequencia, ...]:
        fotografias: list[FotografiaFrequencia] = []
        for resultado in resultados:
            fotografias.extend(self.processar(resultado))
        return tuple(fotografias)


def calcular_fotografias_acumuladas(
    resultados: Iterable[ResultadoEntrada],
    configuracao: ConfiguracaoFrequencia,
) -> tuple[FotografiaFrequencia, ...]:
    return MotorFrequenciaAcumulada(configuracao).processar_varios(resultados)
