"""Processamento independente dos filtros da nova validação e auditoria."""

from collections.abc import Callable, Iterable
from dataclasses import dataclass
from decimal import Decimal

import psycopg

from msen.database.resultados_teste_repository import RepositorioResultadosTeste

from .catalogo_filtros_validacao_nova import (
    FiltroExecutavelValidacao,
    GrupoFiltrosValidacao,
    carregar_catalogo_filtros_validacao,
)
from .executor_filtros_validacao_nova import (
    Combinacao,
    ExecutorFiltroValidacao,
    carregar_executor_filtro_validacao,
)


CriadorExecutor = Callable[[int], ExecutorFiltroValidacao]
InformarProgresso = Callable[[int, int, str, str], None]
CancelamentoSolicitado = Callable[[], bool]


class ErroProcessamentoValidacaoNova(RuntimeError):
    def __init__(self, codigo: str, mensagem: str) -> None:
        super().__init__(mensagem)
        self.codigo = codigo


class OperacaoValidacaoNovaCancelada(RuntimeError):
    """Interrompe o teste em um ponto seguro, sem produzir relatório parcial."""


@dataclass(frozen=True, slots=True)
class OcorrenciaFiltroValidacaoNova:
    id_grupo: int
    nome_grupo: str
    id_filtro: int
    nome_filtro: str
    indice_combinacao: int
    combinacao: Combinacao
    desenho: dict[str, object] | None = None


@dataclass(frozen=True, slots=True)
class ResultadoFiltroValidacaoNova:
    id_grupo: int
    nome_grupo: str
    id_filtro: int
    nome_filtro: str
    total_testado: int
    ocorrencias: int
    incidencia_percentual: Decimal


@dataclass(frozen=True, slots=True)
class RelatorioValidacaoNova:
    total_combinacoes: int
    total_filtros: int
    total_avaliacoes: int
    resultados: tuple[ResultadoFiltroValidacaoNova, ...]


def _selecionar_filtros(
    catalogo: Iterable[GrupoFiltrosValidacao],
    ids_filtros: Iterable[int] | None,
) -> tuple[tuple[GrupoFiltrosValidacao, FiltroExecutavelValidacao], ...]:
    disponiveis = tuple(
        (grupo, filtro)
        for grupo in catalogo
        for filtro in grupo.filtros
    )
    if ids_filtros is None:
        return disponiveis

    ids = tuple(ids_filtros)
    if not ids:
        raise ErroProcessamentoValidacaoNova(
            "SELECAO_VAZIA", "Selecione ao menos um filtro para realizar o teste."
        )
    if any(isinstance(item, bool) or not isinstance(item, int) or item <= 0 for item in ids):
        raise ErroProcessamentoValidacaoNova(
            "IDENTIFICADOR_INVALIDO", "A seleção contém identificador de filtro inválido."
        )
    if len(set(ids)) != len(ids):
        raise ErroProcessamentoValidacaoNova(
            "FILTRO_REPETIDO", "Um mesmo filtro não pode ser selecionado mais de uma vez."
        )
    por_id = {filtro.id_filtro: (grupo, filtro) for grupo, filtro in disponiveis}
    ausentes = tuple(item for item in ids if item not in por_id)
    if ausentes:
        raise ErroProcessamentoValidacaoNova(
            "FILTRO_INDISPONIVEL", "A seleção contém filtro inexistente ou não executável."
        )
    return tuple(por_id[item] for item in ids)


def processar_colecao_validacao_nova(
    combinacoes: Iterable[Combinacao],
    catalogo: Iterable[GrupoFiltrosValidacao],
    criar_executor: CriadorExecutor,
    *,
    ids_filtros: Iterable[int] | None = None,
    informar_progresso: InformarProgresso | None = None,
    cancelamento_solicitado: CancelamentoSolicitado | None = None,
    informar_ocorrencia: Callable[[OcorrenciaFiltroValidacaoNova], None] | None = None,
    construir_desenho: Callable[[int, Combinacao], dict[str, object]] | None = None,
) -> RelatorioValidacaoNova:
    """Aplica cada filtro à coleção inteira, sem funil e sem excluir combinações."""

    if not callable(criar_executor):
        raise TypeError("O criador de executores deve ser chamável.")
    if informar_progresso is not None and not callable(informar_progresso):
        raise TypeError("O informador de progresso deve ser chamável ou nulo.")
    if cancelamento_solicitado is not None and not callable(cancelamento_solicitado):
        raise TypeError("O verificador de cancelamento deve ser chamável ou nulo.")
    if informar_ocorrencia is not None and not callable(informar_ocorrencia):
        raise TypeError("O informador de ocorrência deve ser chamável ou nulo.")
    if construir_desenho is not None and not callable(construir_desenho):
        raise TypeError("O construtor do desenho deve ser chamável ou nulo.")
    colecao = tuple(combinacoes)
    if not colecao:
        raise ErroProcessamentoValidacaoNova(
            "COLECAO_VAZIA", "A coleção de combinações não pode estar vazia."
        )
    selecionados = _selecionar_filtros(catalogo, ids_filtros)
    if not selecionados:
        raise ErroProcessamentoValidacaoNova(
            "SEM_FILTROS", "Não há filtros executáveis para realizar o teste."
        )

    resultados = []
    total = len(colecao)
    total_avaliacoes = total * len(selecionados)
    concluidas = 0
    progresso = informar_progresso or (lambda _feito, _total, _grupo, _filtro: None)
    cancelado = cancelamento_solicitado or (lambda: False)
    for grupo, filtro in selecionados:
        progresso(concluidas, total_avaliacoes, grupo.nome, filtro.nome)
        executor = criar_executor(filtro.id_filtro)
        ocorrencias = 0
        for indice, combinacao in enumerate(colecao, start=1):
            if cancelado():
                raise OperacaoValidacaoNovaCancelada(
                    "O teste foi cancelado pelo usuário."
                )
            detectada = executor(combinacao)
            ocorrencias += int(detectada)
            concluidas += 1
            progresso(concluidas, total_avaliacoes, grupo.nome, filtro.nome)
            if detectada and len(selecionados) == 1 and informar_ocorrencia is not None:
                informar_ocorrencia(OcorrenciaFiltroValidacaoNova(
                    id_grupo=grupo.id_grupo,
                    nome_grupo=grupo.nome,
                    id_filtro=filtro.id_filtro,
                    nome_filtro=filtro.nome,
                    indice_combinacao=indice,
                    combinacao=combinacao,
                    desenho=(
                        None if construir_desenho is None
                        else construir_desenho(filtro.id_filtro, combinacao)
                    ),
                ))
        resultados.append(ResultadoFiltroValidacaoNova(
            id_grupo=grupo.id_grupo,
            nome_grupo=grupo.nome,
            id_filtro=filtro.id_filtro,
            nome_filtro=filtro.nome,
            total_testado=total,
            ocorrencias=ocorrencias,
            incidencia_percentual=(Decimal(ocorrencias) * 100 / Decimal(total)).quantize(
                Decimal("0.000001")
            ),
        ))
    return RelatorioValidacaoNova(
        total_combinacoes=total,
        total_filtros=len(resultados),
        total_avaliacoes=total_avaliacoes,
        resultados=tuple(resultados),
    )


def processar_validacao_nova_no_banco(
    conexao: psycopg.Connection,
    *,
    ids_filtros: Iterable[int] | None = None,
    fotografia_diagonal=None,
    informar_progresso: InformarProgresso | None = None,
    cancelamento_solicitado: CancelamentoSolicitado | None = None,
    informar_ocorrencia: Callable[[OcorrenciaFiltroValidacaoNova], None] | None = None,
    construir_desenho: Callable[[int, Combinacao], dict[str, object]] | None = None,
) -> RelatorioValidacaoNova:
    """Carrega catálogo e coleção fixa e executa o relatório sem persistir resultados."""

    if not isinstance(conexao, psycopg.Connection):
        raise TypeError("O processamento exige uma conexão Psycopg válida.")
    catalogo = carregar_catalogo_filtros_validacao(conexao)
    colecao = RepositorioResultadosTeste(conexao).listar_colecao_fixa()
    return processar_colecao_validacao_nova(
        colecao,
        catalogo,
        lambda id_filtro: carregar_executor_filtro_validacao(
            conexao,
            id_filtro,
            fotografia_diagonal=fotografia_diagonal,
        ),
        ids_filtros=ids_filtros,
        informar_progresso=informar_progresso,
        cancelamento_solicitado=cancelamento_solicitado,
        informar_ocorrencia=informar_ocorrencia,
        construir_desenho=construir_desenho,
    )
