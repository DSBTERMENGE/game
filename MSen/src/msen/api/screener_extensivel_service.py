"""Orquestra o ensaio protegido do novo screener sem persistir dados."""

from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import date
from decimal import Decimal
from pathlib import Path
from time import perf_counter
from typing import Callable

from msen.screener import (
    FaixaEstatistica,
    FaixaGeometrica,
    DecisaoFiltro,
    DefinicaoFamilia,
    DefinicaoFiltro,
    CONFIRMACAO_INTEGRAL,
    TOTAL_COMBINACOES,
    criar_adaptadores_ativos,
    criar_familia_estatistica,
    criar_familia_geometrica,
    criar_fotografia_configuracao,
    criar_quadro_consolidado,
    envelopar_fotografia,
    executar_funil,
    executar_funil_extensivel,
    gerar_amostra,
    serializar_quadro_consolidado,
)
from msen.screener.configuracao import carregar_configuracao_screener
from msen.config import carregar_configuracao_banco
from msen.database import abrir_conexao
from msen.padroes import resolver_funcao_detectora
from msen.services.executor_filtros_validacao_nova import criar_executor_filtro_validacao
from msen.services.entradas_motor_screener import (
    adaptar_aplicacao_integral,
    adaptar_teste_5000,
)

from .distribuicoes import calcular_distribuicoes_no_banco


class ErroEnsaioExtensivel(RuntimeError):
    """Indica ausência ou inconsistência de uma entrada necessária ao ensaio."""

    def __init__(self, codigo: str, mensagem: str) -> None:
        super().__init__(mensagem)
        self.codigo = codigo


@dataclass(frozen=True, slots=True)
class PlanoFiltrosScreener:
    """Famílias e referências prontas para qualquer coleção de combinações."""

    familias: tuple
    parametros: dict[str, object]
    padroes_ativos: tuple


@dataclass(frozen=True, slots=True)
class PadraoAtivoScreener:
    id_padrao: int
    padrao_cod: str
    padrao_nome: str
    grupo_cod: str
    grupo_nome: str
    detector: Callable


def _carregar_padroes_ativos() -> tuple[PadraoAtivoScreener, ...]:
    """Carrega todos os detectores booleanos cadastrados, sem corte de raridade."""

    with abrir_conexao(carregar_configuracao_banco()) as conexao, conexao.cursor() as cursor:
        cursor.execute(
            "SELECT p.id_padrao, p.padrao_cod, p.padrao_nome, "
            "g.grupo_cod, g.grupo_nome, p.funcao_detectora "
            "FROM padroes_subgrupo p JOIN padroes_grupo g USING (id_grupo) "
            "WHERE p.funcao_detectora IS NOT NULL "
            "ORDER BY lower(g.grupo_nome), lower(p.padrao_nome), p.id_padrao",
        )
        linhas = cursor.fetchall()
    return tuple(
        PadraoAtivoScreener(
            id_padrao=linha[0], padrao_cod=linha[1], padrao_nome=linha[2],
            grupo_cod=linha[3], grupo_nome=linha[4],
            detector=criar_executor_filtro_validacao(
                resolver_funcao_detectora(linha[5])
            ),
        )
        for linha in linhas
    )


def _criar_familia_padroes_ativos(
    padroes: tuple[PadraoAtivoScreener, ...], ordem: int = 3,
) -> DefinicaoFamilia:
    filtros = []
    for posicao, padrao in enumerate(padroes, 1):
        codigo_filtro = f"PAD_{padrao.padrao_cod}"

        def avaliar(combinacao, *, item=padrao, codigo=codigo_filtro):
            detectado = item.detector(combinacao)
            if not isinstance(detectado, bool):
                raise ErroEnsaioExtensivel(
                    "DETECCAO_INVALIDA",
                    f"O detector {item.padrao_nome} não retornou True ou False.",
                )
            return DecisaoFiltro.criar(
                codigo_filtro=codigo,
                aprovada=not detectado,
                motivo="PADRAO_DETECTADO" if detectado else "PADRAO_NAO_DETECTADO",
                evidencias={
                    "id_padrao": item.id_padrao,
                    "id_grupo_logico": item.grupo_cod,
                    "detectado": detectado,
                },
            )

        filtros.append(DefinicaoFiltro(
            codigo_filtro, padrao.padrao_nome, posicao, avaliar
        ))
    return DefinicaoFamilia("PADROES", "Padrões", ordem, tuple(filtros))


def _detalhar_padroes_ativos(*, padroes, familia_serializada):
    filtros = {
        item["codigo"].removeprefix("PAD_"): item
        for item in familia_serializada["filtros"]
        if item["codigo"] != "PAD_PG_004"
    }
    grupos = []
    saldo_grupo = familia_serializada["entrada"]
    for grupo_cod in dict.fromkeys(item.grupo_cod for item in padroes):
        itens = tuple(item for item in padroes if item.grupo_cod == grupo_cod)
        entrada_grupo = saldo_grupo
        linhas = []
        for item in itens:
            filtro = filtros[item.padrao_cod]
            saldo_grupo = filtro["saldo"]
            linhas.append({
                "id_padrao": item.id_padrao,
                "padrao_cod": item.padrao_cod,
                "padrao_nome": item.padrao_nome,
                "avaliacoes": filtro["avaliacoes"],
                "exclusoes": filtro["exclusoes"],
                "saldo": filtro["saldo"],
            })
        grupos.append({
            "grupo_cod": grupo_cod,
            "grupo_nome": itens[0].grupo_nome,
            "entrada": entrada_grupo,
            "exclusoes": entrada_grupo - saldo_grupo,
            "saldo": saldo_grupo,
            "padroes": linhas,
        })
    return {"grupos": grupos}


def _perfil_por_codigo(distribuicoes: dict[str, object], codigo: str) -> dict[str, object]:
    item = next(
        (valor for valor in distribuicoes["parametros"] if valor["codigo"] == codigo),
        None,
    )
    if item is None or item.get("perfil") is None and item.get("media") is None:
        raise ErroEnsaioExtensivel(
            "PERFIL_AUSENTE", f"O perfil {codigo} não está disponível."
        )
    return item


def _faixa(distribuicoes: dict[str, object], codigo: str) -> tuple[Decimal, Decimal]:
    item = _perfil_por_codigo(distribuicoes, codigo)
    faixa = item["faixa"]
    return Decimal(faixa["limite_inferior"]), Decimal(faixa["limite_superior"])


def montar_plano_filtros_screener() -> PlanoFiltrosScreener:
    """Monta uma vez o plano comum, sem depender da origem das combinações."""

    distribuicoes = calcular_distribuicoes_no_banco(
        None, None, 10, "desvio_padrao", Decimal(1), Decimal(1)
    )
    padroes_ativos = _carregar_padroes_ativos()

    soma = _faixa(distribuicoes, "EST_SOMA")
    mediana = _faixa(distribuicoes, "EST_MEDIANA")
    desvio = _faixa(distribuicoes, "EST_DESVIO_PADRAO")
    familia_estatistica = criar_familia_estatistica(
        faixa_soma=FaixaEstatistica.criar(*soma),
        faixa_mediana=FaixaEstatistica.criar(*mediana),
        faixa_desvio_padrao=FaixaEstatistica.criar(*desvio),
    )
    codigos_geo = {
        "faixa_extensao": "GEO_EXTENSAO_ABERTA",
        "faixa_perimetro": "GEO_PERIMETRO_FECHADO",
        "faixa_area": "GEO_AREA_TOTAL",
        "faixa_quantidade_regioes": "GEO_QUANTIDADE_REGIOES",
        "faixa_centro_x": "GEO_CENTRO_GRAVIDADE_X",
        "faixa_centro_y": "GEO_CENTRO_GRAVIDADE_Y",
    }
    faixas_geo = {
        nome: FaixaGeometrica.criar(*_faixa(distribuicoes, codigo))
        for nome, codigo in codigos_geo.items()
    }
    familia_geometrica = criar_familia_geometrica(
        **faixas_geo, politica_centro_ausente="excluir"
    )
    familia_padroes = _criar_familia_padroes_ativos(padroes_ativos)
    familias = (familia_estatistica, familia_geometrica, familia_padroes)

    parametros = {
        "EST_SOMA_MEDIA": {
            "limite_inferior_soma": soma[0], "limite_superior_soma": soma[1]
        },
        "EST_MEDIANA": {
            "limite_inferior": mediana[0], "limite_superior": mediana[1]
        },
        "EST_DESVIO_PADRAO": {
            "limite_inferior": desvio[0], "limite_superior": desvio[1]
        },
        **{
            filtro.codigo: {
                "limite_inferior": faixa.limite_inferior,
                "limite_superior": faixa.limite_superior,
                **(
                    {"politica_centro_ausente": "excluir"}
                    if filtro.codigo == "GEO_CENTRO_GRAVIDADE" else {}
                ),
            }
            for filtro, faixa in zip(
                familia_geometrica.filtros,
                (
                    faixas_geo["faixa_extensao"], faixas_geo["faixa_perimetro"],
                    faixas_geo["faixa_area"], faixas_geo["faixa_quantidade_regioes"],
                    faixas_geo["faixa_centro_x"],
                ),
            )
        },
        **{
            f"PAD_{item.padrao_cod}": {
                "id_padrao": item.id_padrao,
                "grupo_cod": item.grupo_cod,
                "padrao_cod": item.padrao_cod,
            }
            for item in padroes_ativos
        },
    }
    parametros["GEO_CENTRO_GRAVIDADE"].update({
        "limite_inferior_y": faixas_geo["faixa_centro_y"].limite_inferior,
        "limite_superior_y": faixas_geo["faixa_centro_y"].limite_superior,
    })
    return PlanoFiltrosScreener(
        familias, parametros, padroes_ativos,
    )


def gerar_quadro_screener_extensivel(
    informar_progresso: Callable[[str, int, int], None] | None = None,
    cancelado: Callable[[], bool] | None = None,
    *,
    processamento_integral: bool = False,
) -> dict[str, object]:
    """Executa a amostra ou o universo integral sem persistir resultados."""

    progresso = informar_progresso or (lambda _etapa, _concluido, _total: None)
    foi_cancelado = cancelado or (lambda: False)
    total_processamento = TOTAL_COMBINACOES if processamento_integral else 10_000
    progresso("Preparando filtros do Screener", 0, total_processamento)
    if foi_cancelado():
        raise InterruptedError("Processamento do Screener cancelado.")
    raiz = Path(__file__).resolve().parents[3]
    configuracao = carregar_configuracao_screener(
        raiz / "config" / "screener.toml", raiz / "config" / "screener.local.toml"
    )
    if (
        configuracao.modo != "amostra"
        or configuracao.limite_combinacoes != 5_000
        or configuracao.confirmacao_processamento_integral
    ):
        raise ErroEnsaioExtensivel(
            "PROTECAO_INTEGRAL_INVALIDA",
            "O novo screener exige amostra de 5.000 e processamento integral bloqueado.",
        )
    configuracao_execucao = (
        replace(
            configuracao, modo="integral",
            confirmacao_processamento_integral=True,
        )
        if processamento_integral else configuracao
    )

    plano = montar_plano_filtros_screener()
    familias = plano.familias
    parametros = plano.parametros
    padroes_ativos = plano.padroes_ativos
    fotografia = criar_fotografia_configuracao(
        familias=familias,
        parametros_filtros=parametros,
        grupos_padroes=(),
        versoes_calculo={
            "estatistica": 1,
            "geometria": 1,
            "padroes": 1,
        },
        modo="integral" if processamento_integral else "amostra",
        semente=configuracao.semente,
        limite_combinacoes=(
            TOTAL_COMBINACOES if processamento_integral
            else configuracao.limite_combinacoes
        ),
        data_fotografia=date.today(),
    )
    envelope = envelopar_fotografia(fotografia)
    combinacoes = (
        adaptar_aplicacao_integral(
            configuracao_execucao,
            confirmacao_integral=CONFIRMACAO_INTEGRAL,
        )
        if processamento_integral else adaptar_teste_5000(configuracao_execucao)
    )
    total_execucao = TOTAL_COMBINACOES if processamento_integral else 5_000

    inicio = perf_counter()
    relatorio_novo = executar_funil_extensivel(
        combinacoes,
        familias,
        informar_progresso=lambda concluido, _total: progresso(
            "Aplicando os filtros atuais", concluido, total_processamento
        ),
        cancelado=foi_cancelado,
        total_combinacoes=total_execucao,
        guardar_aprovadas=not processamento_integral,
        intervalo_progresso=10_000 if processamento_integral else 25,
    )
    duracao = perf_counter() - inicio
    quadro = criar_quadro_consolidado(
        relatorio_novo,
        tipo_escopo="integral" if processamento_integral else "amostra",
    )
    dados = serializar_quadro_consolidado(quadro)
    familia_padroes_serializada = next(
        item for item in dados["familias"] if item["codigo"] == "PADROES"
    )
    dados["detalhes_padroes"] = _detalhar_padroes_ativos(
        padroes=padroes_ativos,
        familia_serializada=familia_padroes_serializada,
    )

    dados.update({
        "duracao_segundos": duracao,
        "fotografia": {
            "checksum_sha256": envelope.checksum_sha256,
            "conteudo_json": envelope.conteudo_json,
        },
        "protecao": {
            "limite_combinacoes": total_execucao,
            "processamento_integral_bloqueado": not processamento_integral,
            "confirmacao_processamento_integral": processamento_integral,
        },
        "aviso": (
            "Aplicação integral concluída sem persistir combinações."
            if processamento_integral
            else "Ensaio experimental de 5.000; processamento integral bloqueado."
        ),
    })
    if not processamento_integral:
        relatorio_anterior = executar_funil(
            gerar_amostra(configuracao_execucao),
            criar_adaptadores_ativos(configuracao),
            informar_progresso=lambda concluido, _total: progresso(
                "Comparando com o resultado anterior", 5_000 + concluido, 10_000
            ),
            cancelado=foi_cancelado,
            total_combinacoes=5_000,
        )
        dados["comparacao"] = {
            "mesma_amostra": True,
            "semente": configuracao.semente,
            "anterior": {
                "total_aprovado": relatorio_anterior.total_aprovado,
                "total_excluido": relatorio_anterior.total_recebido - relatorio_anterior.total_aprovado,
            },
            "novo": {
                "total_aprovado": relatorio_novo.total_aprovado,
                "total_excluido": relatorio_novo.total_excluido,
            },
            "diferenca_aprovadas": relatorio_novo.total_aprovado - relatorio_anterior.total_aprovado,
            "motivos_divergencia": [
                "ordem nova: estatística, geometria e grupos de padrões",
                "faixas novas: média histórica ± 1 desvio-padrão para todas as medidas",
                "geometria nova: cinco filtros, contra apenas extensão no funil anterior",
                "padrões novos: todos os detectores cadastrados são aplicados",
            ],
        }
    return dados


def gerar_quadro_screener_integral(
    informar_progresso: Callable[[str, int, int], None] | None = None,
    cancelado: Callable[[], bool] | None = None,
) -> dict[str, object]:
    return gerar_quadro_screener_extensivel(
        informar_progresso, cancelado,
        processamento_integral=True,
    )
