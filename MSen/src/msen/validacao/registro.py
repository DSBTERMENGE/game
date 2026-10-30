"""Registro único e assinaturas automáticas dos critérios executáveis."""

from collections.abc import Callable
from dataclasses import dataclass
import hashlib
import inspect
import json

from msen.calculos import (
    calcular_desvio_padrao_media, calcular_media_aritmetica,
    calcular_mediana, calcular_soma,
)
from msen.geometria import (
    calcular_area_e_centro_gravidade, calcular_extensao_aberta,
    calcular_perimetro_fechado,
)
from msen.padroes import criar_registro_detectores_aprovados

from .criterios import (
    calcular_area_total, calcular_centro_gravidade_x,
    calcular_centro_gravidade_y, calcular_quantidade_regioes,
)


@dataclass(frozen=True, slots=True)
class DefinicaoCriterio:
    codigo: str
    nome: str
    categoria: str
    funcao: Callable
    tipo_resultado: str
    regra: str
    precisao_decimal: int | None = None
    grupo_codigo: str | None = None
    dependencias: tuple[Callable, ...] = ()

    @property
    def funcao_python(self) -> str:
        return f"{self.funcao.__module__}.{self.funcao.__qualname__}"

    @property
    def assinatura_funcao(self) -> str:
        partes = []
        for funcao in (self.funcao, *self.dependencias):
            partes.extend((
                f"{funcao.__module__}.{funcao.__qualname__}",
                inspect.getsource(funcao),
            ))
        return hashlib.sha256("\n".join(partes).encode("utf-8")).hexdigest()

    @property
    def assinatura_regra(self) -> str:
        dados = {
            "codigo": self.codigo, "categoria": self.categoria,
            "tipo_resultado": self.tipo_resultado,
            "precisao_decimal": self.precisao_decimal,
            "grupo_codigo": self.grupo_codigo, "regra": self.regra,
        }
        serializado = json.dumps(dados, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(serializado.encode("utf-8")).hexdigest()


class RegistroCriteriosValidacao:
    def __init__(self, definicoes: tuple[DefinicaoCriterio, ...]) -> None:
        if not isinstance(definicoes, tuple):
            raise TypeError("As definições devem formar uma tupla.")
        codigos = [item.codigo for item in definicoes]
        if len(codigos) != len(set(codigos)):
            raise ValueError("O registro não aceita códigos duplicados.")
        self._definicoes = tuple(sorted(definicoes, key=lambda item: item.codigo))

    def listar(self) -> tuple[DefinicaoCriterio, ...]:
        return self._definicoes


def criar_registro_criterios_producao() -> RegistroCriteriosValidacao:
    definicoes = [
        DefinicaoCriterio("EST_SOMA", "Soma das seis dezenas", "ESTATISTICA", calcular_soma, "INTEIRO", "Soma exata das seis dezenas."),
        DefinicaoCriterio("EST_MEDIA", "Média aritmética das seis dezenas", "ESTATISTICA", calcular_media_aritmetica, "DECIMAL", "Soma das seis dezenas dividida por 6, ROUND_HALF_UP.", 6, dependencias=(calcular_soma,)),
        DefinicaoCriterio("EST_MEDIANA", "Mediana das seis dezenas", "ESTATISTICA", calcular_mediana, "DECIMAL", "Média das duas posições centrais das dezenas ordenadas.", 1),
        DefinicaoCriterio("EST_DESVIO_PADRAO", "Desvio-padrão das seis dezenas em relação à média das dezenas", "ESTATISTICA", calcular_desvio_padrao_media, "DECIMAL", "Raiz da variância populacional das seis dezenas.", 6),
        DefinicaoCriterio("GEO_EXTENSAO", "Extensão aberta", "GEOMETRIA", calcular_extensao_aberta, "DECIMAL", "Soma euclidiana dos cinco segmentos do percurso crescente.", 12),
        DefinicaoCriterio("GEO_PERIMETRO", "Perímetro fechado", "GEOMETRIA", calcular_perimetro_fechado, "DECIMAL", "Extensão aberta acrescida do segmento de fechamento.", 12),
        DefinicaoCriterio("GEO_REGIOES", "Quantidade de regiões", "GEOMETRIA", calcular_quantidade_regioes, "INTEIRO", "Quantidade de regiões fechadas da rede planar.", dependencias=(calcular_area_e_centro_gravidade,)),
        DefinicaoCriterio("GEO_AREA", "Área total", "GEOMETRIA", calcular_area_total, "DECIMAL", "Soma exata das áreas das regiões fechadas.", 12, dependencias=(calcular_area_e_centro_gravidade,)),
        DefinicaoCriterio("GEO_CENTRO_X", "Centro de gravidade X", "GEOMETRIA", calcular_centro_gravidade_x, "DECIMAL", "Coordenada X do centroide ponderado; nula sem área positiva.", 12, dependencias=(calcular_area_e_centro_gravidade,)),
        DefinicaoCriterio("GEO_CENTRO_Y", "Centro de gravidade Y", "GEOMETRIA", calcular_centro_gravidade_y, "DECIMAL", "Coordenada Y do centroide ponderado; nula sem área positiva.", 12, dependencias=(calcular_area_e_centro_gravidade,)),
    ]
    detectores = criar_registro_detectores_aprovados()
    grupos = {
        "PD_001": "PG_001", "PD_002": "PG_001", "PD_003": "PG_001",
        "PD_004": "PG_002", "PD_005": "PG_002", "PD_006": "PG_002",
        "PD_007": "PG_003", "PD_008": "PG_003", "PD_009": "PG_003",
    }
    for codigo in detectores.codigos_registrados():
        definicoes.append(DefinicaoCriterio(
            f"PAD_{codigo}", f"Detector {codigo}", "PADRAO",
            detectores.obter(codigo), "PADRAO",
            f"Detecta exclusivamente a condição cadastrada como {codigo}.",
            grupo_codigo=grupos[codigo],
        ))
    return RegistroCriteriosValidacao(tuple(definicoes))
