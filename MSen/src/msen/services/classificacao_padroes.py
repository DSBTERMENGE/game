"""Recálculo transacional das classificações históricas por grupo."""

from dataclasses import dataclass
from datetime import date
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

import psycopg

from msen.database import (
    RepositorioClassificacoesPadrao,
    RepositorioGruposPadroes,
    RepositorioPadroes,
    RepositorioResultados,
)
from msen.modelos import ResultadoEntrada
from msen.padroes import (
    CODIGO_DUAS_SEQUENCIAIS,
    CODIGO_GRUPO_SEQUENCIAIS,
    CODIGO_MAIS_DE_TRES_SEQUENCIAIS,
    CODIGO_TRES_SEQUENCIAIS,
    calcular_estatisticas_sequenciais,
    classificar_grupo_dezenas_sequenciais,
)


CODIGOS_SEQUENCIAIS = (
    CODIGO_DUAS_SEQUENCIAIS,
    CODIGO_TRES_SEQUENCIAIS,
    CODIGO_MAIS_DE_TRES_SEQUENCIAIS,
)
SEIS_CASAS = Decimal("0.000001")


class ErroRecalculoClassificacao(RuntimeError):
    """Informa falha funcional segura antes de persistir classificações."""

    def __init__(self, codigo: str, mensagem: str) -> None:
        super().__init__(mensagem)
        self.codigo = codigo


@dataclass(frozen=True, slots=True)
class ContagemClassificacao:
    """Quantidade calculada para um padrão ou para a ausência de correspondência."""

    padrao_cod: str | None
    quantidade: int


@dataclass(frozen=True, slots=True)
class RelatorioRecalculoClassificacao:
    """Resumo imutável de uma execução completa do classificador piloto."""

    grupo_cod: str
    versao_calculo: int
    resultados_analisados: int
    contagens: tuple[ContagemClassificacao, ...]


@dataclass(frozen=True, slots=True)
class ClassePerfilPadrao:
    """Frequência e percentuais de uma classe no espaço amostral analisado."""

    padrao_cod: str | None
    quantidade: int
    percentual_total: Decimal
    percentual_classificados: Decimal | None
    intervalo_medio: Decimal | None
    desvio_padrao: Decimal | None
    raro: bool


@dataclass(frozen=True, slots=True)
class PerfilClassificacaoGrupo:
    """Perfil reconciliado de um grupo, sem ativar qualquer exclusão."""

    grupo_cod: str
    total_resultados: int
    total_classificados: int
    limite_raridade_percentual: Decimal
    operador_raridade: str
    numero_ap_inicial: int | None
    numero_ap_final: int | None
    data_inicial: date | None
    data_final: date | None
    versoes_calculo: tuple[int, ...]
    classes: tuple[ClassePerfilPadrao, ...]
    padroes_raros: tuple[str, ...]


def _listar_todos_resultados(
    repositorio: RepositorioResultados,
) -> tuple:
    """Lê todo o histórico em páginas, preservando a ordem de concurso."""

    pagina = 10_000
    deslocamento = 0
    acumulados = []
    while True:
        lote = repositorio.listar(limite=pagina, deslocamento=deslocamento)
        acumulados.extend(lote)
        if len(lote) < pagina:
            return tuple(acumulados)
        deslocamento += pagina


def _percentual(quantidade: int, denominador: int) -> Decimal:
    """Calcula percentual com seis casas; devolve zero para amostra vazia."""

    if denominador == 0:
        return Decimal(0).quantize(SEIS_CASAS)
    return (
        Decimal(quantidade) * Decimal(100) / Decimal(denominador)
    ).quantize(SEIS_CASAS, rounding=ROUND_HALF_UP)


def _validar_limite_raridade(valor: Decimal | int | str) -> Decimal:
    """Normaliza um limite percentual entre zero e cem com seis casas."""

    if isinstance(valor, bool) or not isinstance(valor, (Decimal, int, str)):
        raise TypeError("O limite de raridade deve ser Decimal, inteiro ou texto numérico.")
    try:
        limite = Decimal(valor)
    except (InvalidOperation, ValueError) as erro:
        raise ValueError("O limite de raridade deve ser numérico.") from erro
    if not limite.is_finite() or not Decimal(0) <= limite <= Decimal(100):
        raise ValueError("O limite de raridade deve estar entre 0 e 100.")
    return limite.quantize(SEIS_CASAS, rounding=ROUND_HALF_UP)


def recalcular_classificacoes_grupo_sequenciais(
    conexao: psycopg.Connection,
    *,
    versao_calculo: int = 1,
) -> RelatorioRecalculoClassificacao:
    """Classifica e persiste todo o histórico no grupo sequencial PG_001.

    O grupo e os três padrões são resolvidos pelos códigos estáveis. Toda a
    leitura, classificação e gravação ocorre em uma transação. Uma falha desfaz
    integralmente a execução. Repetir o processo atualiza as mesmas linhas pelo
    par resultado/grupo, permitindo recalcular com outra versão sem duplicar.
    """

    if not isinstance(conexao, psycopg.Connection):
        raise TypeError("O recálculo exige uma conexão Psycopg válida.")
    if isinstance(versao_calculo, bool) or not isinstance(versao_calculo, int):
        raise TypeError("versao_calculo deve ser inteira.")
    if versao_calculo <= 0:
        raise ValueError("versao_calculo deve ser positiva.")

    resultados_repo = RepositorioResultados(conexao)
    grupos_repo = RepositorioGruposPadroes(conexao)
    padroes_repo = RepositorioPadroes(conexao)
    classificacoes_repo = RepositorioClassificacoesPadrao(conexao)

    with conexao.transaction():
        grupos = {grupo.grupo_cod: grupo for grupo in grupos_repo.listar()}
        grupo = grupos.get(CODIGO_GRUPO_SEQUENCIAIS)
        if grupo is None:
            raise ErroRecalculoClassificacao(
                "GRUPO_AUSENTE", "O grupo sequencial PG_001 não está cadastrado."
            )
        padroes = {
            padrao.padrao_cod: padrao
            for padrao in padroes_repo.listar(CODIGO_GRUPO_SEQUENCIAIS)
        }
        ausentes = tuple(codigo for codigo in CODIGOS_SEQUENCIAIS if codigo not in padroes)
        if ausentes:
            raise ErroRecalculoClassificacao(
                "PADROES_AUSENTES",
                "O grupo sequencial não possui todos os padrões classificáveis.",
            )

        resultados = _listar_todos_resultados(resultados_repo)
        contagens: dict[str | None, int] = {
            CODIGO_DUAS_SEQUENCIAIS: 0,
            CODIGO_TRES_SEQUENCIAIS: 0,
            CODIGO_MAIS_DE_TRES_SEQUENCIAIS: 0,
            None: 0,
        }
        for resultado in resultados:
            decisao = classificar_grupo_dezenas_sequenciais(
                resultado.resultado.resultados
            )
            padrao = None if decisao.padrao_cod is None else padroes[decisao.padrao_cod]
            classificacoes_repo.salvar(
                resultado.id_resultado,
                grupo.id_grupo,
                id_padrao=None if padrao is None else padrao.id_padrao,
                estado=decisao.estado,
                versao_calculo=versao_calculo,
            )
            contagens[decisao.padrao_cod] += 1

    return RelatorioRecalculoClassificacao(
        grupo_cod=CODIGO_GRUPO_SEQUENCIAIS,
        versao_calculo=versao_calculo,
        resultados_analisados=len(resultados),
        contagens=tuple(
            ContagemClassificacao(codigo, contagens[codigo])
            for codigo in (*CODIGOS_SEQUENCIAIS, None)
        ),
    )


def calcular_perfil_grupo_sequenciais(
    conexao: psycopg.Connection,
    *,
    limite_raridade_percentual: Decimal | int | str,
    numero_ap_ate: int | None = None,
    data_ate: date | None = None,
    sincronizar_catalogo: bool = True,
) -> PerfilClassificacaoGrupo:
    """Calcula frequências do PG_001 e apenas indica padrões abaixo do limite.

    O denominador oficial é o total de resultados. A função exige que todos já
    possuam classificação no grupo, reconcilia os totais, sincroniza as
    estatísticas completas de `PD_001`–`PD_003` e não aciona o screener.
    `SEM_CORRESPONDENCIA` participa do fechamento em 100%, mas nunca é raro.
    """

    if not isinstance(conexao, psycopg.Connection):
        raise TypeError("O perfil exige uma conexão Psycopg válida.")
    limite = _validar_limite_raridade(limite_raridade_percentual)
    if numero_ap_ate is not None:
        if isinstance(numero_ap_ate, bool) or not isinstance(numero_ap_ate, int):
            raise TypeError("numero_ap_ate deve ser inteiro ou nulo.")
        if numero_ap_ate <= 0:
            raise ValueError("numero_ap_ate deve ser positivo.")
    if data_ate is not None and not isinstance(data_ate, date):
        raise TypeError("data_ate deve ser date ou nula.")
    if numero_ap_ate is not None and data_ate is not None:
        raise ValueError("Informe somente um tipo de corte histórico.")
    if not isinstance(sincronizar_catalogo, bool):
        raise TypeError("sincronizar_catalogo deve ser booleano.")
    if sincronizar_catalogo and (numero_ap_ate is not None or data_ate is not None):
        raise ValueError("Um perfil com corte não pode substituir o catálogo global.")
    resultados_repo = RepositorioResultados(conexao)
    grupos_repo = RepositorioGruposPadroes(conexao)
    padroes_repo = RepositorioPadroes(conexao)
    classificacoes_repo = RepositorioClassificacoesPadrao(conexao)

    with conexao.transaction():
        grupos = {grupo.grupo_cod: grupo for grupo in grupos_repo.listar()}
        grupo = grupos.get(CODIGO_GRUPO_SEQUENCIAIS)
        if grupo is None:
            raise ErroRecalculoClassificacao(
                "GRUPO_AUSENTE", "O grupo sequencial PG_001 não está cadastrado."
            )
        padroes = {
            padrao.padrao_cod: padrao
            for padrao in padroes_repo.listar(CODIGO_GRUPO_SEQUENCIAIS)
        }
        ausentes = tuple(codigo for codigo in CODIGOS_SEQUENCIAIS if codigo not in padroes)
        if ausentes:
            raise ErroRecalculoClassificacao(
                "PADROES_AUSENTES",
                "O grupo sequencial não possui todos os padrões classificáveis.",
            )

        todos_resultados = _listar_todos_resultados(resultados_repo)
        resultados = tuple(
            item
            for item in todos_resultados
            if (numero_ap_ate is None or item.numero_ap <= numero_ap_ate)
            and (data_ate is None or item.resultado.data_resultado <= data_ate)
        )
        todas_classificacoes = classificacoes_repo.listar_por_grupo(grupo.id_grupo)
        classificacao_por_resultado = {
            item.id_resultado: item for item in todas_classificacoes
        }
        classificacoes = tuple(
            classificacao_por_resultado[item.id_resultado]
            for item in resultados
            if item.id_resultado in classificacao_por_resultado
        )
        if len(classificacoes) != len(resultados):
            raise ErroRecalculoClassificacao(
                "CLASSIFICACAO_INCOMPLETA",
                "Nem todos os resultados possuem classificação no grupo sequencial.",
            )
        codigo_por_id = {padrao.id_padrao: codigo for codigo, padrao in padroes.items()}
        contagens: dict[str | None, int] = {codigo: 0 for codigo in CODIGOS_SEQUENCIAIS}
        contagens[None] = 0
        for classificacao in classificacoes:
            codigo = (
                None
                if classificacao.id_padrao is None
                else codigo_por_id.get(classificacao.id_padrao)
            )
            if classificacao.id_padrao is not None and codigo is None:
                raise ErroRecalculoClassificacao(
                    "PADRAO_FORA_DO_GRUPO",
                    "Uma classificação referencia padrão inesperado para PG_001.",
                )
            contagens[codigo] += 1
        if sum(contagens.values()) != len(resultados):
            raise ErroRecalculoClassificacao(
                "TOTAL_DIVERGENTE", "As classificações não reconciliam com os resultados."
            )

        serie = tuple(
            ResultadoEntrada(
                data_resultado=item.resultado.data_resultado,
                numero_ap=item.resultado.numero_ap,
                res_01=item.resultado.res_01,
                res_02=item.resultado.res_02,
                res_03=item.resultado.res_03,
                res_04=item.resultado.res_04,
                res_05=item.resultado.res_05,
                res_06=item.resultado.res_06,
            )
            for item in resultados
        )
        estatisticas = calcular_estatisticas_sequenciais(serie)
        estatistica_por_codigo = {
            item.padrao_cod: item for item in estatisticas
        }
        for estatistica in estatisticas:
            if estatistica.num_oco != contagens[estatistica.padrao_cod]:
                raise ErroRecalculoClassificacao(
                    "DETECTOR_DIVERGENTE",
                    "A contagem das classificações diverge do detector histórico.",
                )
            if sincronizar_catalogo:
                padroes_repo.atualizar_estatistica(estatistica)

    total = len(resultados)
    total_classificados = total - contagens[None]
    classes = tuple(
        ClassePerfilPadrao(
            padrao_cod=codigo,
            quantidade=contagens[codigo],
            percentual_total=_percentual(contagens[codigo], total),
            percentual_classificados=(
                None if codigo is None else _percentual(contagens[codigo], total_classificados)
            ),
            intervalo_medio=(
                None if codigo is None else estatistica_por_codigo[codigo].intervalo_medio
            ),
            desvio_padrao=(
                None if codigo is None else estatistica_por_codigo[codigo].desv_padrao
            ),
            raro=(
                codigo is not None
                and total > 0
                and _percentual(contagens[codigo], total) < limite
            ),
        )
        for codigo in (*CODIGOS_SEQUENCIAIS, None)
    )
    return PerfilClassificacaoGrupo(
        grupo_cod=CODIGO_GRUPO_SEQUENCIAIS,
        total_resultados=total,
        total_classificados=total_classificados,
        limite_raridade_percentual=limite,
        operador_raridade="<",
        numero_ap_inicial=None if not resultados else resultados[0].numero_ap,
        numero_ap_final=None if not resultados else resultados[-1].numero_ap,
        data_inicial=None if not resultados else resultados[0].resultado.data_resultado,
        data_final=None if not resultados else resultados[-1].resultado.data_resultado,
        versoes_calculo=tuple(sorted({item.versao_calculo for item in classificacoes})),
        classes=classes,
        padroes_raros=tuple(
            item.padrao_cod
            for item in classes
            if item.raro and item.padrao_cod is not None
        ),
    )
