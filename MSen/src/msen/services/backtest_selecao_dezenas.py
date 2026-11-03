"""Execução, consolidação e comparação do backtest de dezenas."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
from typing import Callable

import psycopg

from msen.database.fonte_selecao_dezenas_repository import (
    ErroFonteSelecaoDezenas,
    RepositorioFonteSelecaoDezenas,
)
from msen.database.pesquisa_selecao_repository import (
    AlvoPesquisaEntrada,
    AvaliacaoDezenaPesquisaEntrada,
    RepositorioPesquisaSelecao,
)
from msen.modelos import ResultadoEntrada

from .carga_historico_frequencia import assinatura_resultados
from .configuracao_selecao_dezenas import ConfiguracaoSelecaoDezenas
from .selecao_dezenas import (
    AvaliacaoSelecaoDezena,
    ResultadoSelecaoDezenas,
    selecionar_dezenas_para_alvo,
)


SEIS_CASAS = Decimal("0.000001")


class ErroBacktestSelecao(RuntimeError):
    def __init__(self, codigo: str, mensagem: str) -> None:
        super().__init__(mensagem)
        self.codigo = codigo


@dataclass(frozen=True, slots=True)
class ClasseBacktest:
    classe: int
    quantidade: int
    percentual: Decimal


@dataclass(frozen=True, slots=True)
class ResumoBacktestSelecao:
    id_execucao_selecao: int
    estado: str
    concurso_inicial: int
    concurso_final: int
    primeiro_avaliado: int | None
    ultimo_avaliado: int | None
    fator_k: Decimal
    fator_j: Decimal
    modo_quantidade: str
    quantidade_configurada: int | None
    solicitados: int
    avaliados: int
    pendentes: int
    nao_avaliaveis: int
    classes: tuple[ClasseBacktest, ...]
    minimo_dezenas: int | None
    maximo_dezenas: int | None
    media_dezenas: Decimal | None
    vezes_limite_nao_atingido: int
    total_dezenas_selecionadas: int
    total_dezenas_acertadas: int
    cobertura_sorteadas: Decimal | None
    precisao_selecionadas: Decimal | None
    media_acertos_concurso: Decimal | None
    custo_combinatorio_total: int
    custo_combinatorio_medio: Decimal | None


@dataclass(frozen=True, slots=True)
class RelatorioExecucaoBacktest:
    id_execucao_selecao: int
    estado: str
    alvos_processados_agora: int
    alvos_ja_existentes: int
    resumo: ResumoBacktestSelecao


@dataclass(frozen=True, slots=True)
class DetalheAlvoBacktest:
    numero_concurso_alvo: int
    numero_concurso_corte: int
    situacao: str
    dezenas_retornadas: tuple[int, ...]
    quantidade_aprovada: int
    quantidade_retornada: int
    quantidade_acertos: int | None
    classe_acerto: int | None
    quantidade_combinacoes_brutas: int
    limite_nao_atingido: bool
    motivo: str | None


@dataclass(frozen=True, slots=True)
class ComparacaoBacktests:
    comparavel: bool
    ressalvas: tuple[str, ...]
    pesquisas: tuple[ResumoBacktestSelecao, ...]


def _percentual(numerador: int, denominador: int) -> Decimal | None:
    if denominador == 0:
        return None
    return (Decimal(numerador) * Decimal(100) / Decimal(denominador)).quantize(
        SEIS_CASAS, rounding=ROUND_HALF_UP
    )


def _media(total: int, quantidade: int) -> Decimal | None:
    if quantidade == 0:
        return None
    return (Decimal(total) / Decimal(quantidade)).quantize(
        SEIS_CASAS, rounding=ROUND_HALF_UP
    )


def _converter_avaliacao(
    item: AvaliacaoSelecaoDezena,
) -> AvaliacaoDezenaPesquisaEntrada:
    return AvaliacaoDezenaPesquisaEntrada(
        dezena=item.dezena,
        estado_avaliacao=item.estado_avaliacao,
        ultima_ocorrencia=item.ultima_ocorrencia,
        quantidade_intervalos=item.quantidade_intervalos,
        media_intervalos=item.media_intervalos,
        desvio_padrao=item.desvio_padrao,
        centro_original=item.centro_original,
        centro_ajustado=item.centro_ajustado,
        limite_inferior_exato=item.limite_inferior_exato,
        limite_superior_exato=item.limite_superior_exato,
        limite_inferior=item.limite_inferior,
        limite_superior=item.limite_superior,
        distancia_normalizada=item.distancia_normalizada,
        distancia_absoluta=item.distancia_absoluta,
        posicao_ranking=item.posicao_ranking,
        aprovada=item.aprovada,
        retornada=item.retornada,
    )


def _listar_resultados_ate(
    conexao: psycopg.Connection, concurso_final: int
) -> tuple[ResultadoEntrada, ...]:
    with conexao.transaction():
        with conexao.cursor() as cursor:
            cursor.execute(
                "SELECT data_resultado, numero_ap, res_01,res_02,res_03,res_04,res_05,res_06 "
                "FROM resultados WHERE numero_ap <= %s ORDER BY numero_ap",
                (concurso_final,),
            )
            itens = tuple(ResultadoEntrada.criar(
                data_resultado=linha[0], numero_ap=linha[1], resultados=linha[2:8]
            ) for linha in cursor.fetchall())
    if len(itens) != concurso_final or any(
        item.numero_ap != indice for indice, item in enumerate(itens, start=1)
    ):
        raise ErroBacktestSelecao(
            "LACUNA_HISTORICA",
            f"Os resultados de 1 a {concurso_final} não formam uma sequência completa.",
        )
    return itens


def _buscar_resultado_alvo(
    conexao: psycopg.Connection, concurso: int
) -> tuple[int, frozenset[int]]:
    with conexao.transaction():
        with conexao.cursor() as cursor:
            cursor.execute(
                "SELECT id_resultado,res_01,res_02,res_03,res_04,res_05,res_06 "
                "FROM resultados WHERE numero_ap=%s",
                (concurso,),
            )
            linha = cursor.fetchone()
    if linha is None:
        raise ErroBacktestSelecao("RESULTADO_AUSENTE", "O resultado do alvo não existe.")
    return linha[0], frozenset(linha[1:7])


def executar_backtest_selecao(
    conexao: psycopg.Connection,
    configuracao: ConfiguracaoSelecaoDezenas,
    *,
    concurso_inicial: int = 500,
    concurso_final: int | None = None,
    cancelamento_solicitado: Callable[[], bool] | None = None,
    informar_progresso: Callable[[int, int], None] | None = None,
) -> RelatorioExecucaoBacktest:
    if not isinstance(conexao, psycopg.Connection):
        raise TypeError("conexao deve ser Psycopg Connection.")
    if concurso_inicial < 500:
        raise ValueError("O backtest deve iniciar no concurso 500 ou posterior.")
    with conexao.transaction():
        with conexao.cursor() as cursor:
            cursor.execute("SELECT MAX(numero_ap) FROM resultados")
            ultimo = cursor.fetchone()[0]
    final = ultimo if concurso_final is None else concurso_final
    if ultimo is None or final > ultimo or final < concurso_inicial:
        raise ValueError("Período de backtest inválido para os resultados existentes.")

    resultados_origem = _listar_resultados_ate(conexao, final)
    assinatura = assinatura_resultados(resultados_origem)
    repositorio = RepositorioPesquisaSelecao(conexao)
    fonte = RepositorioFonteSelecaoDezenas(conexao)
    configuracao_persistida = repositorio.criar_ou_buscar_configuracao(configuracao)
    execucao = repositorio.criar_ou_buscar_execucao(
        configuracao_persistida,
        tipo_execucao="BACKTEST",
        assinatura_resultados=assinatura,
        concurso_corte_origem=final,
        concurso_alvo_inicial=concurso_inicial,
        concurso_alvo_final=final,
    )
    existentes = repositorio.alvos_ja_persistidos(execucao.id_execucao_selecao)
    estado = repositorio.iniciar_ou_retomar_execucao(execucao.id_execucao_selecao)
    if estado == "CONCLUIDA":
        return RelatorioExecucaoBacktest(
            execucao.id_execucao_selecao, estado, 0, len(existentes),
            resumir_backtest(conexao, execucao.id_execucao_selecao),
        )
    if estado != "EXECUTANDO":
        raise ErroBacktestSelecao("ESTADO_INVALIDO", "A execução não pode ser processada.")

    processados = 0
    try:
        for alvo in range(concurso_inicial, final + 1):
            if alvo in existentes:
                continue
            if (
                (cancelamento_solicitado is not None and cancelamento_solicitado())
                or repositorio.estado_execucao(execucao.id_execucao_selecao)
                == "CANCELAMENTO_SOLICITADO"
            ):
                repositorio.solicitar_cancelamento(execucao.id_execucao_selecao)
                repositorio.finalizar_cancelamento(execucao.id_execucao_selecao)
                break

            try:
                estatisticas = fonte.carregar_estatisticas_corte(alvo - 1)
                selecao = selecionar_dezenas_para_alvo(
                    estatisticas, configuracao,
                    numero_concurso_alvo=alvo,
                    numero_concurso_corte=alvo - 1,
                )
            except ErroFonteSelecaoDezenas as erro:
                raise ErroBacktestSelecao(erro.codigo, str(erro)) from erro

            id_resultado, dezenas_reais = _buscar_resultado_alvo(conexao, alvo)
            acertos = len(set(selecao.dezenas_retornadas) & dezenas_reais)
            situacao = "AVALIADO" if selecao.avaliavel else "NAO_AVALIAVEL"
            repositorio.salvar_alvo(
                execucao.id_execucao_selecao,
                AlvoPesquisaEntrada(
                    numero_concurso_alvo=alvo,
                    numero_concurso_corte=alvo - 1,
                    id_resultado=id_resultado,
                    situacao=situacao,
                    quantidade_configurada=selecao.quantidade_configurada,
                    quantidade_acertos=acertos if selecao.avaliavel else None,
                    motivo=selecao.motivo,
                ),
                tuple(_converter_avaliacao(item) for item in selecao.avaliacoes),
            )
            processados += 1
            if informar_progresso is not None:
                informar_progresso(len(existentes) + processados, final - concurso_inicial + 1)
        else:
            repositorio.concluir_execucao(execucao.id_execucao_selecao)
    except Exception as erro:
        codigo = getattr(erro, "codigo", "FALHA_BACKTEST")
        repositorio.registrar_falha(execucao.id_execucao_selecao, codigo, str(erro))
        raise

    estado_final = repositorio.estado_execucao(execucao.id_execucao_selecao)
    return RelatorioExecucaoBacktest(
        execucao.id_execucao_selecao,
        estado_final,
        processados,
        len(existentes),
        resumir_backtest(conexao, execucao.id_execucao_selecao),
    )


def resumir_backtest(
    conexao: psycopg.Connection, id_execucao_selecao: int
) -> ResumoBacktestSelecao:
    with conexao.transaction():
        with conexao.cursor() as cursor:
            cursor.execute(
                "SELECT e.estado,e.concurso_alvo_inicial,e.concurso_alvo_final,"
                "e.total_alvos,c.fator_k,c.fator_j,c.modo_quantidade,c.quantidade_dezenas "
                "FROM execucoes_pesquisa_selecao e "
                "JOIN configuracoes_pesquisa_selecao c "
                "ON c.id_configuracao_selecao=e.id_configuracao_selecao "
                "WHERE e.id_execucao_selecao=%s",
                (id_execucao_selecao,),
            )
            execucao = cursor.fetchone()
            if execucao is None:
                raise ErroBacktestSelecao("EXECUCAO_NAO_ENCONTRADA", "Execução inexistente.")
            cursor.execute(
                "SELECT situacao,quantidade_retornada,quantidade_acertos,"
                "limite_nao_atingido,quantidade_combinacoes_brutas "
                "FROM alvos_pesquisa_selecao WHERE id_execucao_selecao=%s",
                (id_execucao_selecao,),
            )
            alvos = cursor.fetchall()
    avaliados = [linha for linha in alvos if linha[0] == "AVALIADO"]
    pendentes = sum(linha[0] == "PENDENTE" for linha in alvos)
    nao_avaliaveis = sum(linha[0] == "NAO_AVALIAVEL" for linha in alvos)
    classes_quantidade = {classe: 0 for classe in range(7)}
    for linha in avaliados:
        classes_quantidade[linha[2]] += 1
    quantidades = [linha[1] for linha in avaliados]
    total_selecionadas = sum(quantidades)
    total_acertos = sum(linha[2] for linha in avaliados)
    custo_total = sum(linha[4] for linha in avaliados)
    quantidade_avaliados = len(avaliados)
    with conexao.transaction():
        with conexao.cursor() as cursor:
            cursor.execute(
                "SELECT MIN(numero_concurso_alvo),MAX(numero_concurso_alvo) "
                "FROM alvos_pesquisa_selecao WHERE id_execucao_selecao=%s "
                "AND situacao='AVALIADO'",
                (id_execucao_selecao,),
            )
            primeiro_avaliado, ultimo_avaliado = cursor.fetchone()
    return ResumoBacktestSelecao(
        id_execucao_selecao=id_execucao_selecao,
        estado=execucao[0], concurso_inicial=execucao[1], concurso_final=execucao[2],
        primeiro_avaliado=primeiro_avaliado, ultimo_avaliado=ultimo_avaliado,
        fator_k=execucao[4], fator_j=execucao[5], modo_quantidade=execucao[6],
        quantidade_configurada=execucao[7],
        solicitados=execucao[3], avaliados=quantidade_avaliados,
        pendentes=pendentes, nao_avaliaveis=nao_avaliaveis,
        classes=tuple(ClasseBacktest(
            classe, quantidade, _percentual(quantidade, quantidade_avaliados) or Decimal(0)
        ) for classe, quantidade in classes_quantidade.items()),
        minimo_dezenas=min(quantidades) if quantidades else None,
        maximo_dezenas=max(quantidades) if quantidades else None,
        media_dezenas=_media(total_selecionadas, quantidade_avaliados),
        vezes_limite_nao_atingido=sum(linha[3] for linha in avaliados),
        total_dezenas_selecionadas=total_selecionadas,
        total_dezenas_acertadas=total_acertos,
        cobertura_sorteadas=_percentual(total_acertos, 6 * quantidade_avaliados),
        precisao_selecionadas=_percentual(total_acertos, total_selecionadas),
        media_acertos_concurso=_media(total_acertos, quantidade_avaliados),
        custo_combinatorio_total=custo_total,
        custo_combinatorio_medio=_media(custo_total, quantidade_avaliados),
    )


def detalhar_backtest(
    conexao: psycopg.Connection, id_execucao_selecao: int
) -> tuple[DetalheAlvoBacktest, ...]:
    """Retorna os alvos preservados sem copiar as dezenas reais de resultados."""
    with conexao.transaction():
        with conexao.cursor() as cursor:
            cursor.execute(
                "SELECT a.numero_concurso_alvo,a.numero_concurso_corte,a.situacao,"
                "COALESCE(ARRAY_AGG(d.dezena ORDER BY d.dezena) "
                "FILTER (WHERE d.retornada),ARRAY[]::SMALLINT[]),"
                "a.quantidade_aprovada,a.quantidade_retornada,a.quantidade_acertos,"
                "a.classe_acerto,a.quantidade_combinacoes_brutas,"
                "a.limite_nao_atingido,a.motivo "
                "FROM alvos_pesquisa_selecao a "
                "LEFT JOIN avaliacoes_dezenas_pesquisa d "
                "ON d.id_alvo_selecao=a.id_alvo_selecao "
                "WHERE a.id_execucao_selecao=%s "
                "GROUP BY a.id_alvo_selecao ORDER BY a.numero_concurso_alvo",
                (id_execucao_selecao,),
            )
            return tuple(DetalheAlvoBacktest(
                numero_concurso_alvo=linha[0], numero_concurso_corte=linha[1],
                situacao=linha[2], dezenas_retornadas=tuple(linha[3]),
                quantidade_aprovada=linha[4], quantidade_retornada=linha[5],
                quantidade_acertos=linha[6], classe_acerto=linha[7],
                quantidade_combinacoes_brutas=linha[8],
                limite_nao_atingido=linha[9], motivo=linha[10],
            ) for linha in cursor.fetchall())


def comparar_backtests(
    conexao: psycopg.Connection, ids_execucoes: tuple[int, ...]
) -> ComparacaoBacktests:
    if len(ids_execucoes) < 2 or len(set(ids_execucoes)) != len(ids_execucoes):
        raise ValueError("Informe ao menos duas execuções distintas.")
    marcadores: list[tuple[str, int, int, int, int]] = []
    with conexao.transaction():
        with conexao.cursor() as cursor:
            for identificador in ids_execucoes:
                cursor.execute(
                    "SELECT assinatura_resultados,concurso_alvo_inicial,"
                    "concurso_alvo_final,versao_calculo," 
                    "(SELECT COUNT(1) FROM alvos_pesquisa_selecao a "
                    "WHERE a.id_execucao_selecao=e.id_execucao_selecao "
                    "AND a.situacao='NAO_AVALIAVEL') "
                    "FROM execucoes_pesquisa_selecao e WHERE id_execucao_selecao=%s",
                    (identificador,),
                )
                linha = cursor.fetchone()
                if linha is None:
                    raise ErroBacktestSelecao("EXECUCAO_NAO_ENCONTRADA", "Execução inexistente.")
                marcadores.append((linha[0].strip(), linha[1], linha[2], linha[3], linha[4]))
    ressalvas: list[str] = []
    if len({item[0] for item in marcadores}) != 1:
        ressalvas.append("As pesquisas usam assinaturas de resultados diferentes.")
    if len({item[1:3] for item in marcadores}) != 1:
        ressalvas.append("As pesquisas usam períodos diferentes.")
    if len({item[3] for item in marcadores}) != 1:
        ressalvas.append("As pesquisas usam versões de cálculo diferentes.")
    if len({item[4] for item in marcadores}) != 1:
        ressalvas.append("As pesquisas possuem coberturas não avaliáveis diferentes.")
    return ComparacaoBacktests(
        comparavel=not ressalvas,
        ressalvas=tuple(ressalvas),
        pesquisas=tuple(resumir_backtest(conexao, item) for item in ids_execucoes),
    )
