"""Estudo reproduzível da etapa 26.6; não implementa classificador de produção."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from math import sqrt
from random import Random

from dotenv import load_dotenv

from msen.calculos import calcular_desvio_padrao_media, calcular_mediana, calcular_soma
from msen.config import carregar_configuracao_banco
from msen.database import abrir_conexao
from msen.geometria import (
    calcular_area_e_centro_gravidade,
    calcular_extensao_aberta,
    calcular_perimetro_fechado,
)
from msen.modelos import ResultadoEntrada


NOMES = (
    "soma", "mediana", "desvio", "extensao", "perimetro", "regioes", "area"
)


@dataclass
class Momento:
    quantidade: int = 0
    media: float = 0.0
    m2: float = 0.0

    def adicionar(self, valor: float) -> None:
        self.quantidade += 1
        delta = valor - self.media
        self.media += delta / self.quantidade
        self.m2 += delta * (valor - self.media)

    @property
    def desvio(self) -> float:
        return sqrt(self.m2 / self.quantidade) if self.quantidade else 0.0


def _vetor(dezenas: tuple[int, ...]) -> tuple[float, ...]:
    resultado = ResultadoEntrada.criar(
        data_resultado=date(2000, 1, 1), numero_ap=1, resultados=dezenas
    )
    figura = calcular_area_e_centro_gravidade(dezenas)
    return (
        float(calcular_soma(resultado)),
        float(calcular_mediana(resultado)),
        float(calcular_desvio_padrao_media(resultado)),
        float(calcular_extensao_aberta(dezenas)),
        float(calcular_perimetro_fechado(dezenas)),
        float(len(figura.regioes)),
        float(figura.area_total),
    )


def _indice(vetor: tuple[float, ...], momentos: list[Momento]) -> float:
    z2 = [
        ((valor - momento.media) / momento.desvio) ** 2
        for valor, momento in zip(vetor, momentos)
        if momento.desvio > 0
    ]
    estatistica = sum(z2[:3]) / 3
    geometria = sum(z2[3:]) / 4
    distancia = (estatistica + geometria) / 2
    return 1 / (1 + distancia)


def main() -> None:
    load_dotenv(".env")
    with abrir_conexao(carregar_configuracao_banco()) as conexao, conexao.cursor() as cursor:
        cursor.execute(
            "SELECT numero_ap, res_01, res_02, res_03, res_04, res_05, res_06 "
            "FROM resultados ORDER BY numero_ap"
        )
        resultados = [(linha[0], tuple(linha[1:])) for linha in cursor.fetchall()]

    momentos = [Momento() for _ in NOMES]
    comparados = 0
    soma_percentis = 0.0
    acima_mediana = 0
    amostras_por_concurso = 20

    for numero, dezenas in resultados:
        vetor_real = _vetor(dezenas)
        if numero >= 500:
            indice_real = _indice(vetor_real, momentos)
            aleatorio = Random(numero)
            indices_controle = [
                _indice(_vetor(tuple(sorted(aleatorio.sample(range(1, 61), 6)))), momentos)
                for _ in range(amostras_por_concurso)
            ]
            menores_ou_iguais = sum(item <= indice_real for item in indices_controle)
            percentil = menores_ou_iguais / amostras_por_concurso
            soma_percentis += percentil
            acima_mediana += percentil > 0.5
            comparados += 1
        for momento, valor in zip(momentos, vetor_real):
            momento.adicionar(valor)

    print(f"concursos_avaliados={comparados}")
    print(f"controles_por_concurso={amostras_por_concurso}")
    print(f"percentil_medio_real={soma_percentis / comparados:.6f}")
    print(f"reais_acima_mediana_controle={acima_mediana / comparados:.6f}")
    print("observacao=medidas de cada alvo usam somente concursos anteriores")


if __name__ == "__main__":
    main()
