"""Leitura e validação da configuração experimental do screener."""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any
import tomllib


LIMITE_EXPERIMENTAL = 5_000
ORDEM_CRITERIOS = (
    "padroes_historicos",
    "medidas_estatisticas",
    "medidas_geometricas",
)


class ErroConfiguracaoScreener(ValueError):
    """Indica configuração ausente, malformada ou insegura do screener."""

    def __init__(self, codigo: str, mensagem: str) -> None:
        super().__init__(mensagem)
        self.codigo = codigo


@dataclass(frozen=True, slots=True)
class ConfiguracaoCriterio:
    """Representa um critério ainda inativo e suas tolerâncias experimentais."""

    habilitado: bool
    tolerancias: dict[str, float]


@dataclass(frozen=True, slots=True)
class RegraConfigurada:
    """Registra uma regra individual explicitamente aprovada para o screener."""

    codigo: str
    categoria: str
    modo: str
    tolerancia_percentual: float
    num_ocorrencias: int
    total_resultados: int
    reconciliacao: str


@dataclass(frozen=True, slots=True)
class RegraEstatisticaConfigurada:
    """Registra uma medida estatística aprovada e seus limites."""

    codigo: str
    medida: str
    modo: str
    limite_inferior: float
    limite_superior: float
    referencia: str


@dataclass(frozen=True, slots=True)
class RegraGeometricaConfigurada:
    """Registra uma medida geométrica aprovada e seus limites."""

    codigo: str
    medida: str
    modo: str
    limite_inferior: float
    limite_superior: float
    referencia: str


@dataclass(frozen=True, slots=True)
class ConfiguracaoScreener:
    """Contrato validado e imutável de um ensaio do screener."""

    versao: int
    modo: str
    semente: int
    limite_combinacoes: int
    confirmacao_processamento_integral: bool
    limite_raridade_percentual: Decimal
    ordem_filtros: tuple[str, ...]
    criterios: dict[str, ConfiguracaoCriterio]
    regras: dict[str, RegraConfigurada] = field(default_factory=dict)
    regras_estatisticas: dict[str, RegraEstatisticaConfigurada] = field(
        default_factory=dict
    )
    regras_geometricas: dict[str, RegraGeometricaConfigurada] = field(
        default_factory=dict
    )


def _ler_toml(caminho: Path, *, obrigatorio: bool) -> dict[str, Any]:
    """Lê um TOML e converte falhas em erro funcional sem dados confidenciais."""

    if not caminho.is_file():
        if obrigatorio:
            raise ErroConfiguracaoScreener(
                "ARQUIVO_CONFIGURACAO_AUSENTE",
                f"Arquivo de configuração não encontrado: {caminho.name}.",
            )
        return {}
    try:
        with caminho.open("rb") as arquivo:
            return tomllib.load(arquivo)
    except tomllib.TOMLDecodeError as erro:
        raise ErroConfiguracaoScreener(
            "TOML_INVALIDO", f"O arquivo {caminho.name} possui TOML inválido."
        ) from erro


def _mesclar(base: dict[str, Any], local: dict[str, Any]) -> dict[str, Any]:
    """Aplica substituições locais recursivas sem modificar os dados lidos."""

    resultado = dict(base)
    for chave, valor in local.items():
        anterior = resultado.get(chave)
        if isinstance(anterior, dict) and isinstance(valor, dict):
            resultado[chave] = _mesclar(anterior, valor)
        else:
            resultado[chave] = valor
    return resultado


def _validar_percentual(nome: str, valor: object) -> float:
    """Exige percentual numérico entre zero e cem."""

    if isinstance(valor, bool) or not isinstance(valor, (int, float)):
        raise ErroConfiguracaoScreener("TOLERANCIA_INVALIDA", f"{nome} deve ser numérica.")
    percentual = float(valor)
    if not 0 <= percentual <= 100:
        raise ErroConfiguracaoScreener(
            "TOLERANCIA_INVALIDA", f"{nome} deve estar entre 0 e 100."
        )
    return percentual


def validar_limite_raridade(valor: object) -> Decimal:
    """Normaliza a configuração única de raridade com seis casas decimais."""

    if isinstance(valor, bool) or not isinstance(valor, (int, float, str, Decimal)):
        raise ErroConfiguracaoScreener(
            "LIMITE_RARIDADE_INVALIDO",
            "O limite de raridade deve ser numérico e estar entre 0 e 100.",
        )
    try:
        limite = Decimal(str(valor))
    except InvalidOperation as erro:
        raise ErroConfiguracaoScreener(
            "LIMITE_RARIDADE_INVALIDO",
            "O limite de raridade deve ser numérico e estar entre 0 e 100.",
        ) from erro
    if not limite.is_finite() or not Decimal(0) <= limite <= Decimal(100):
        raise ErroConfiguracaoScreener(
            "LIMITE_RARIDADE_INVALIDO",
            "O limite de raridade deve ser numérico e estar entre 0 e 100.",
        )
    return limite.quantize(Decimal("0.000001"))


def _validar(dados: dict[str, Any]) -> ConfiguracaoScreener:
    """Transforma a estrutura TOML no contrato seguro das próximas etapas."""

    execucao = dados.get("execucao", {})
    funil = dados.get("funil", {})
    raridade = dados.get("raridade", {})
    if dados.get("versao") != 1:
        raise ErroConfiguracaoScreener("VERSAO_INVALIDA", "A versão deve ser 1.")
    modo = execucao.get("modo")
    if modo not in {"amostra", "integral"}:
        raise ErroConfiguracaoScreener("MODO_INVALIDO", "O modo deve ser amostra ou integral.")
    semente = execucao.get("semente")
    if isinstance(semente, bool) or not isinstance(semente, int) or semente < 0:
        raise ErroConfiguracaoScreener("SEMENTE_INVALIDA", "A semente deve ser inteira e não negativa.")
    limite = execucao.get("limite_combinacoes")
    if limite != LIMITE_EXPERIMENTAL:
        raise ErroConfiguracaoScreener(
            "LIMITE_EXPERIMENTAL_INVALIDO",
            "Nesta fase, o limite deve permanecer exatamente em 5.000 combinações.",
        )
    confirmacao = execucao.get("confirmacao_processamento_integral")
    if not isinstance(confirmacao, bool):
        raise ErroConfiguracaoScreener("CONFIRMACAO_INVALIDA", "A confirmação deve ser booleana.")
    limite_raridade = validar_limite_raridade(raridade.get("limite_percentual"))
    ordem = tuple(funil.get("ordem", ()))
    if ordem != ORDEM_CRITERIOS:
        raise ErroConfiguracaoScreener(
            "ORDEM_FILTROS_INVALIDA",
            "A ordem deve ser padrões históricos, estatísticas e geometria.",
        )

    criterios_brutos = dados.get("criterios", {})
    criterios: dict[str, ConfiguracaoCriterio] = {}
    for nome in ORDEM_CRITERIOS:
        bruto = criterios_brutos.get(nome, {})
        habilitado = bruto.get("habilitado")
        if not isinstance(habilitado, bool):
            raise ErroConfiguracaoScreener(
                "CRITERIO_INVALIDO", f"O critério {nome} deve declarar habilitado."
            )
        if habilitado:
            raise ErroConfiguracaoScreener(
                "CRITERIO_NAO_AUTORIZADO",
                "Categorias inteiras não podem ser habilitadas; autorize regras individuais.",
            )
        tolerancias = {
            chave: _validar_percentual(chave, valor)
            for chave, valor in bruto.items()
            if chave.startswith("tolerancia_")
        }
        criterios[nome] = ConfiguracaoCriterio(habilitado, tolerancias)

    regras: dict[str, RegraConfigurada] = {}
    for codigo, bruto in dados.get("regras", {}).items():
        if codigo not in {"PD_002", "PD_003", "PD_005", "PD_006"}:
            raise ErroConfiguracaoScreener(
                "REGRA_NAO_AUTORIZADA", f"A regra {codigo} ainda não foi autorizada."
            )
        categoria = bruto.get("categoria")
        modo_regra = bruto.get("modo")
        tolerancia = _validar_percentual(
            "tolerancia_percentual", bruto.get("tolerancia_percentual")
        )
        ocorrencias = bruto.get("num_ocorrencias")
        total_resultados = bruto.get("total_resultados")
        reconciliacao = bruto.get("reconciliacao")
        if categoria != "padroes_historicos" or modo_regra != "ativo":
            raise ErroConfiguracaoScreener(
                "REGRA_INVALIDA", f"{codigo} deve usar categoria histórica e modo ativo."
            )
        if (
            isinstance(ocorrencias, bool)
            or not isinstance(ocorrencias, int)
            or isinstance(total_resultados, bool)
            or not isinstance(total_resultados, int)
            or not 0 <= ocorrencias <= total_resultados
            or total_resultados == 0
            or not isinstance(reconciliacao, str)
            or not reconciliacao.strip()
        ):
            raise ErroConfiguracaoScreener(
                "EVIDENCIA_REGRA_INVALIDA",
                f"A evidência configurada de {codigo} é inválida.",
            )
        regras[codigo] = RegraConfigurada(
            codigo, categoria, modo_regra, tolerancia, ocorrencias,
            total_resultados, reconciliacao,
        )
    regras_estatisticas: dict[str, RegraEstatisticaConfigurada] = {}
    for codigo, bruto in dados.get("regras_estatisticas", {}).items():
        medidas_autorizadas = {
            "EST_MEDIA_P01_P99": "media_aritmetica",
            "EST_DESVIO_P01_P99": "desvio_padrao_populacional",
            "EST_MEDIANA_P01_P99": "mediana",
        }
        if codigo not in medidas_autorizadas:
            raise ErroConfiguracaoScreener(
                "REGRA_ESTATISTICA_NAO_AUTORIZADA",
                f"A regra estatística {codigo} ainda não foi autorizada.",
            )
        medida = bruto.get("medida")
        modo_regra = bruto.get("modo")
        inferior = bruto.get("limite_inferior")
        superior = bruto.get("limite_superior")
        referencia = bruto.get("referencia")
        if (
            medida != medidas_autorizadas[codigo]
            or modo_regra != "ativo"
            or isinstance(inferior, bool)
            or not isinstance(inferior, (int, float))
            or isinstance(superior, bool)
            or not isinstance(superior, (int, float))
            or float(inferior) > float(superior)
            or not isinstance(referencia, str)
            or not referencia.strip()
        ):
            raise ErroConfiguracaoScreener(
                "REGRA_ESTATISTICA_INVALIDA",
                f"A regra experimental {codigo} possui configuração inválida.",
            )
        regras_estatisticas[codigo] = RegraEstatisticaConfigurada(
            codigo,
            medida,
            modo_regra,
            float(inferior),
            float(superior),
            referencia,
        )
    regras_geometricas: dict[str, RegraGeometricaConfigurada] = {}
    for codigo, bruto in dados.get("regras_geometricas", {}).items():
        if codigo != "GEO_EXTENSAO_P01_P99":
            raise ErroConfiguracaoScreener(
                "REGRA_GEOMETRICA_NAO_AUTORIZADA",
                f"A regra geométrica {codigo} ainda não foi autorizada.",
            )
        medida = bruto.get("medida")
        modo_regra = bruto.get("modo")
        inferior = bruto.get("limite_inferior")
        superior = bruto.get("limite_superior")
        referencia = bruto.get("referencia")
        if (
            medida != "extensao_aberta"
            or modo_regra != "ativo"
            or isinstance(inferior, bool)
            or not isinstance(inferior, (int, float))
            or isinstance(superior, bool)
            or not isinstance(superior, (int, float))
            or float(inferior) > float(superior)
            or not isinstance(referencia, str)
            or not referencia.strip()
        ):
            raise ErroConfiguracaoScreener(
                "REGRA_GEOMETRICA_INVALIDA",
                f"A regra experimental {codigo} possui configuração inválida.",
            )
        regras_geometricas[codigo] = RegraGeometricaConfigurada(
            codigo, medida, modo_regra, float(inferior), float(superior), referencia
        )
    return ConfiguracaoScreener(
        1,
        modo,
        semente,
        limite,
        confirmacao,
        limite_raridade,
        ordem,
        criterios,
        regras,
        regras_estatisticas,
        regras_geometricas,
    )


def carregar_configuracao_screener(
    caminho_padrao: str | Path, caminho_local: str | Path | None = None
) -> ConfiguracaoScreener:
    """Carrega o padrão e aplica, se existir, o arquivo local ignorado pelo Git."""

    padrao = _ler_toml(Path(caminho_padrao), obrigatorio=True)
    local = {} if caminho_local is None else _ler_toml(Path(caminho_local), obrigatorio=False)
    return _validar(_mesclar(padrao, local))
