import json
import tempfile
import unittest
from pathlib import Path

from msen.calculos import calcular_resultado
from msen.modelos import ResultadoEntrada
from msen.services.importacao_banco import (
    RelatorioImportacaoBanco,
    _como_entrada,
    salvar_relatorio_importacao,
)


class ImportacaoBancoTestCase(unittest.TestCase):
    def test_converte_calculado_para_entrada_sem_perder_dados(self):
        entrada = ResultadoEntrada.criar(
            numero_ap=1, data_resultado="11/03/1996",
            resultados=[41, 5, 4, 52, 30, 33],
        )
        convertido = _como_entrada(calcular_resultado(entrada))
        self.assertEqual(entrada, convertido)

    def test_salva_relatorio_json_sem_credenciais(self):
        relatorio = RelatorioImportacaoBanco(
            arquivo="fonte.xlsx", sha256="a" * 64,
            iniciada_em="2026-10-26T00:00:00+00:00",
            concluida_em="2026-10-26T00:00:01+00:00",
            registros_antes=0, registros_depois=1, linhas_analisadas=1,
            novas=1, inseridas=1, iguais=0, alteradas=0, invalidas=0,
            concursos_inseridos=(1,), concursos_alterados=(), linhas_invalidas=(),
        )
        with tempfile.TemporaryDirectory() as pasta:
            destino = salvar_relatorio_importacao(relatorio, Path(pasta) / "relatorio.json")
            dados = json.loads(destino.read_text(encoding="utf-8"))
        self.assertEqual("fonte.xlsx", dados["arquivo"])
        self.assertEqual([1], dados["concursos_inseridos"])
        self.assertNotIn("password", dados)
        self.assertNotIn("senha", dados)

    def test_rejeita_objeto_que_nao_seja_relatorio(self):
        with tempfile.TemporaryDirectory() as pasta:
            with self.assertRaises(TypeError):
                salvar_relatorio_importacao(object(), Path(pasta) / "relatorio.json")


if __name__ == "__main__":
    unittest.main()
