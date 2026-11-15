"""Ferramentas geométricas para estudar a disposição das dezenas."""

from .caminho import (
    PontoGeometrico,
    SegmentoGeometrico,
    calcular_extensao_aberta,
    calcular_perimetro_fechado,
    construir_caminho_aberto,
    construir_percurso_fechado,
    construir_vertices,
)
from .regioes import (
    RegiaoFechada,
    dividir_segmentos,
    encontrar_intersecoes,
    identificar_regioes_fechadas,
)
from .medidas import (
    MedidaRegiao,
    ResultadoGeometrico,
    calcular_area_e_centro_gravidade,
    consolidar_regioes,
    medir_regiao,
)
from .poligono2_experimental import (
    ArestaExperimental,
    DiagnosticoPoligono2Experimental,
    analisar_poligono2_experimental,
)
from .poligono2 import ResultadoPoligono2, calcular_poligono2

__all__ = [
    "MedidaRegiao", "PontoGeometrico", "RegiaoFechada", "ResultadoGeometrico",
    "SegmentoGeometrico", "calcular_area_e_centro_gravidade",
    "calcular_extensao_aberta",
    "calcular_perimetro_fechado", "construir_caminho_aberto",
    "construir_percurso_fechado", "construir_vertices", "dividir_segmentos",
    "consolidar_regioes", "encontrar_intersecoes",
    "identificar_regioes_fechadas", "medir_regiao",
    "ArestaExperimental", "DiagnosticoPoligono2Experimental",
    "analisar_poligono2_experimental",
    "ResultadoPoligono2", "calcular_poligono2",
]
