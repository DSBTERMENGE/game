"""Família de grupos de padrões baseada na fotografia histórica."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from types import MappingProxyType

from msen.padroes import classificar_grupo_dezenas_sequenciais

from .contrato_extensivel import DecisaoFiltro, DefinicaoFamilia, DefinicaoFiltro
from .fotografia import GrupoPadroesFotografado
from .gerador import Combinacao


class ErroFamiliaPadroes(ValueError):
    """Indica divergência entre classificador e fotografia histórica."""

    def __init__(self, codigo: str, mensagem: str) -> None:
        super().__init__(mensagem)
        self.codigo = codigo


@dataclass(frozen=True, slots=True)
class ClassificacaoGrupoFunil:
    """Classe exclusiva identificada por um classificador de grupo."""

    grupo_cod: str
    padrao_cod: str | None
    evidencias: Mapping[str, object]

    @classmethod
    def criar(
        cls,
        *,
        grupo_cod: str,
        padrao_cod: str | None,
        evidencias: Mapping[str, object],
    ) -> ClassificacaoGrupoFunil:
        if not isinstance(grupo_cod, str) or not grupo_cod.strip():
            raise ErroFamiliaPadroes("GRUPO_INVALIDO", "O grupo deve possuir código.")
        if padrao_cod is not None and (
            not isinstance(padrao_cod, str) or not padrao_cod.strip()
        ):
            raise ErroFamiliaPadroes(
                "PADRAO_INVALIDO", "O padrão deve possuir código ou ser nulo."
            )
        if not isinstance(evidencias, Mapping):
            raise TypeError("evidencias deve ser um mapeamento.")
        return cls(
            grupo_cod.strip(),
            None if padrao_cod is None else padrao_cod.strip(),
            MappingProxyType(dict(evidencias)),
        )


ClassificadorGrupo = Callable[[Combinacao], ClassificacaoGrupoFunil]


def classificar_sequenciais_para_funil(combinacao: Combinacao) -> ClassificacaoGrupoFunil:
    """Adapta o classificador oficial PG_001 ao contrato genérico do funil."""

    resultado = classificar_grupo_dezenas_sequenciais(combinacao)
    return ClassificacaoGrupoFunil.criar(
        grupo_cod=resultado.grupo_cod,
        padrao_cod=resultado.padrao_cod,
        evidencias={
            "maior_tamanho": resultado.evidencia.maior_tamanho,
            "maiores_blocos": resultado.evidencia.maiores_blocos,
            "estado": resultado.estado.value,
        },
    )


def criar_familia_padroes(
    *,
    grupos_fotografados: tuple[GrupoPadroesFotografado, ...],
    classificadores: Mapping[str, ClassificadorGrupo],
    ordem: int = 3,
) -> DefinicaoFamilia:
    """Cria um filtro por grupo usando somente a política já fotografada."""

    if not isinstance(grupos_fotografados, tuple) or not grupos_fotografados:
        raise ErroFamiliaPadroes("GRUPOS_AUSENTES", "Informe ao menos um grupo.")
    if any(not isinstance(item, GrupoPadroesFotografado) for item in grupos_fotografados):
        raise TypeError("grupos_fotografados aceita somente grupos fotografados.")
    if not isinstance(classificadores, Mapping):
        raise TypeError("classificadores deve ser um mapeamento.")
    codigos = [item.grupo_cod for item in grupos_fotografados]
    if len(codigos) != len(set(codigos)):
        raise ErroFamiliaPadroes("GRUPO_DUPLICADO", "O grupo aparece mais de uma vez.")
    if set(classificadores) != set(codigos):
        raise ErroFamiliaPadroes(
            "CLASSIFICADORES_INCOMPLETOS",
            "Deve existir exatamente um classificador para cada grupo fotografado.",
        )
    if any(not callable(item) for item in classificadores.values()):
        raise TypeError("Cada classificador de grupo deve ser chamável.")

    filtros = []
    for posicao, grupo in enumerate(sorted(grupos_fotografados, key=lambda item: item.grupo_cod), 1):
        classificador = classificadores[grupo.grupo_cod]
        classes = {item.padrao_cod: item for item in grupo.frequencias}
        excludentes = frozenset(grupo.padroes_excludentes)

        def avaliar(
            combinacao: Combinacao,
            *,
            grupo: GrupoPadroesFotografado = grupo,
            classificador: ClassificadorGrupo = classificador,
            classes=classes,
            excludentes=excludentes,
        ) -> DecisaoFiltro:
            classificacao = classificador(combinacao)
            if not isinstance(classificacao, ClassificacaoGrupoFunil):
                raise ErroFamiliaPadroes(
                    "CLASSIFICACAO_INVALIDA",
                    "O classificador deve retornar ClassificacaoGrupoFunil.",
                )
            if classificacao.grupo_cod != grupo.grupo_cod:
                raise ErroFamiliaPadroes(
                    "GRUPO_DIVERGENTE", "O classificador respondeu por outro grupo."
                )
            if classificacao.padrao_cod not in classes:
                raise ErroFamiliaPadroes(
                    "CLASSE_NAO_FOTOGRAFADA",
                    "A classificação não pertence às frequências fotografadas.",
                )
            frequencia = classes[classificacao.padrao_cod]
            excluir = classificacao.padrao_cod in excludentes
            evidencias = dict(classificacao.evidencias)
            evidencias.update({
                "grupo_cod": grupo.grupo_cod,
                "padrao_cod": classificacao.padrao_cod,
                "classe": (
                    "SEM_CORRESPONDENCIA"
                    if classificacao.padrao_cod is None
                    else "PADRAO_IDENTIFICADO"
                ),
                "quantidade_historica": frequencia.quantidade,
                "percentual_historico": format(frequencia.percentual, "f"),
                "limite_raridade": format(grupo.limite_raridade, "f"),
                "operador_raridade": grupo.operador,
                "denominador_historico": grupo.denominador,
                "padroes_excludentes": grupo.padroes_excludentes,
            })
            return DecisaoFiltro.criar(
                codigo_filtro=f"PAD_{grupo.grupo_cod}",
                aprovada=not excluir,
                motivo="PADRAO_RARO_FOTOGRAFADO" if excluir else "CLASSE_ACEITA",
                evidencias=evidencias,
            )

        filtros.append(
            DefinicaoFiltro(
                f"PAD_{grupo.grupo_cod}", f"Grupo {grupo.grupo_cod}", posicao, avaliar
            )
        )
    return DefinicaoFamilia("PADROES", "Padrões históricos", ordem, tuple(filtros))
