"""Teste de aceitação somente leitura da fonte real do Item 3.5."""

import hashlib
import unittest
from datetime import date
from pathlib import Path

from msen.importacao import ler_linhas_excel


class PlanilhaRealTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fonte = (
            Path(__file__).parents[1]
            / "dados"
            / "fontes"
            / "Resultados_ate_concurso_3069_sorteio.xlsx"
        )
        cls.hash_antes = hashlib.sha256(cls.fonte.read_bytes()).hexdigest()
        cls.tamanho_antes = cls.fonte.stat().st_size
        cls.linhas = ler_linhas_excel(cls.fonte)
        cls.hash_depois = hashlib.sha256(cls.fonte.read_bytes()).hexdigest()
        cls.tamanho_depois = cls.fonte.stat().st_size
        cls.validas = tuple(linha for linha in cls.linhas if linha.resultado is not None)
        cls.invalidas = tuple(linha for linha in cls.linhas if linha.erro is not None)

    def test_quantidade_e_relatorio_de_validade(self):
        self.assertEqual(3069, len(self.linhas))
        self.assertEqual(3069, len(self.validas))
        self.assertEqual(0, len(self.invalidas))

    def test_primeiro_concurso(self):
        linha = self.validas[0]
        resultado = linha.resultado
        self.assertEqual(8, linha.numero_linha)
        self.assertEqual(3069, resultado.numero_ap)
        self.assertEqual(date(2026, 10, 11), resultado.data_resultado)
        self.assertEqual((47, 5, 22, 44, 57, 19), resultado.resultados)

    def test_ultimo_concurso(self):
        linha = self.validas[-1]
        resultado = linha.resultado
        self.assertEqual(3076, linha.numero_linha)
        self.assertEqual(1, resultado.numero_ap)
        self.assertEqual(date(1996, 3, 11), resultado.data_resultado)
        self.assertEqual((41, 5, 4, 52, 30, 33), resultado.resultados)

    def test_concursos_sao_unicos_e_cobrem_de_1_a_3069(self):
        concursos = tuple(linha.resultado.numero_ap for linha in self.validas)
        self.assertEqual(3069, len(set(concursos)))
        self.assertEqual(set(range(1, 3070)), set(concursos))

    def test_arquivo_permanece_identico_apos_leitura(self):
        self.assertEqual(self.tamanho_antes, self.tamanho_depois)
        self.assertEqual(self.hash_antes, self.hash_depois)
        self.assertEqual(
            "027726f33a89738ad9dc95fac9a7eccd390609f5c63cacbb2f00b3873724ce67",
            self.hash_depois,
        )


if __name__ == "__main__":
    unittest.main()
