"""Confere o catálogo da Etapa 17.1 contra código e esquema existentes."""

from pathlib import Path
import unittest

from msen.calculos import (
    calcular_desvio_padrao_media,
    calcular_media_aritmetica,
    calcular_mediana,
    calcular_soma,
)
from msen.geometria import (
    calcular_area_e_centro_gravidade,
    calcular_extensao_aberta,
    calcular_perimetro_fechado,
)


RAIZ = Path(__file__).resolve().parents[2]
CATALOGO = RAIZ / "docs" / "CATALOGO_PARAMETROS_ANALISE.md"
ESQUEMA = RAIZ / "database" / "schema_postgresql.sql"


class CatalogoParametrosAnaliseTestCase(unittest.TestCase):
    def test_catalogo_relaciona_os_dez_parametros_aprovados(self) -> None:
        texto = CATALOGO.read_text(encoding="utf-8")
        linhas_catalogadas = tuple(
            linha for linha in texto.splitlines() if linha.startswith("| `")
        )
        codigos = (
            "EST_SOMA", "EST_MEDIA", "EST_MEDIANA", "EST_DESVIO_PADRAO",
            "GEO_EXTENSAO_ABERTA", "GEO_PERIMETRO_FECHADO", "GEO_AREA_TOTAL",
            "GEO_QUANTIDADE_REGIOES", "GEO_CENTRO_GRAVIDADE_X",
            "GEO_CENTRO_GRAVIDADE_Y",
        )

        for codigo in codigos:
            with self.subTest(codigo=codigo):
                self.assertEqual(
                    sum(linha.startswith(f"| `{codigo}` |") for linha in linhas_catalogadas),
                    1,
                )

    def test_funcoes_declaradas_no_catalogo_sao_as_funcoes_reais(self) -> None:
        funcoes = (
            calcular_soma, calcular_media_aritmetica, calcular_mediana,
            calcular_desvio_padrao_media, calcular_extensao_aberta,
            calcular_perimetro_fechado, calcular_area_e_centro_gravidade,
        )

        self.assertTrue(all(callable(funcao) for funcao in funcoes))
        texto = CATALOGO.read_text(encoding="utf-8")
        for funcao in funcoes:
            with self.subTest(funcao=funcao.__name__):
                self.assertIn(funcao.__name__, texto)

    def test_colunas_e_precisoes_do_catalogo_correspondem_ao_esquema(self) -> None:
        esquema = ESQUEMA.read_text(encoding="utf-8")
        declaracoes = (
            "soma_res SMALLINT NOT NULL",
            "media_aritmetica_res NUMERIC(10,6) NOT NULL",
            "mediana_res NUMERIC(4,1) NOT NULL",
            "desvio_padrao_media NUMERIC(10,6) NOT NULL",
            "extensao_aberta NUMERIC(20,12) NOT NULL",
            "perimetro_fechado NUMERIC(20,12) NOT NULL",
            "quantidade_regioes SMALLINT NOT NULL",
            "area_total NUMERIC(20,12) NOT NULL",
            "centro_gravidade_x NUMERIC(20,12)",
            "centro_gravidade_y NUMERIC(20,12)",
        )

        for declaracao in declaracoes:
            with self.subTest(declaracao=declaracao):
                self.assertIn(declaracao, esquema)

    def test_catalogo_registra_equivalencia_e_distincao_do_desvio(self) -> None:
        texto = CATALOGO.read_text(encoding="utf-8")

        self.assertIn("linearmente equivalentes", texto)
        self.assertIn("M = S / 6", texto)
        self.assertIn("desvio-padrão populacional **das seis dezenas", texto)
        self.assertIn("não é o\n  desvio-padrão de uma série de médias históricas", texto)


if __name__ == "__main__":
    unittest.main()
