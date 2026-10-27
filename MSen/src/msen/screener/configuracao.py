"""Leitura e validação da configuração experimental do screener."""

from __future__ import annotations

from dataclasses import dataclass
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
class ConfiguracaoScreener:
    """Contrato validado e imutável de um ensaio do screener."""

    versao: int
    modo: str
    semente: int
    limite_combinacoes: int
    confirmacao_processamento_integral: bool
    ordem_filtros: tuple[str, ...]
    criterios: dict[str, ConfiguracaoCriterio]


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


def _validar(dados: dict[str, Any]) -> ConfiguracaoScreener:
    """Transforma a estrutura TOML no contrato seguro das próximas etapas."""

    execucao = dados.get("execucao", {})
    funil = dados.get("funil", {})
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
        tolerancias = {
            chave: _validar_percentual(chave, valor)
            for chave, valor in bruto.items()
            if chave.startswith("tolerancia_")
        }
        criterios[nome] = ConfiguracaoCriterio(habilitado, tolerancias)

    if any(criterio.habilitado for criterio in criterios.values()):
        raise ErroConfiguracaoScreener(
            "CRITERIO_NAO_AUTORIZADO",
            "Os critérios permanecem desabilitados até suas regras serem aprovadas.",
        )
    return ConfiguracaoScreener(1, modo, semente, limite, confirmacao, ordem, criterios)


def carregar_configuracao_screener(
    caminho_padrao: str | Path, caminho_local: str | Path | None = None
) -> ConfiguracaoScreener:
    """Carrega o padrão e aplica, se existir, o arquivo local ignorado pelo Git."""

    padrao = _ler_toml(Path(caminho_padrao), obrigatorio=True)
    local = {} if caminho_local is None else _ler_toml(Path(caminho_local), obrigatorio=False)
    return _validar(_mesclar(padrao, local))
