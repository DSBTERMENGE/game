import csv
import io
import json
import unittest
from datetime import datetime, timezone

from msen.services.exportacao_validacao import (
    COLUNAS, montar_exportacao, serializar_csv, serializar_json, validar_exportacao,
)


class TestExportacaoValidacao(unittest.TestCase):
    def linha(self, **alteracoes):
        dados = dict.fromkeys(COLUNAS)
        dados.update({
            "concurso": 1, "dezenas": "4,5,30,33,41,52", "criterio_codigo": "EST_SOMA",
            "criterio_nome": "Soma", "categoria": "ESTATISTICA", "funcao_python": "modulo:soma",
            "tipo_resultado": "INTEIRO", "esperado_estado": "VALOR_IDENTIFICADO",
            "esperado_valor": "165", "calculado_estado": "VALOR_IDENTIFICADO",
            "calculado_valor": "165", "aprovado": "S", "diferenca": "0",
            "assinatura_funcao": "a" * 64, "assinatura_regra": "b" * 64,
            "assinatura_executada": "a" * 64, "referencia_origem": "IA",
            "referencia_revisor": "oraculo", "referencia_conferida_em": "2026-10-30T00:00:00+00:00",
            "calculado_em": "2026-10-30T00:01:00+00:00",
        })
        dados.update(alteracoes)
        return tuple(dados[campo] for campo in COLUNAS)

    def test_json_reabre_sem_perda_e_detecta_alteracao(self):
        dados = montar_exportacao([self.linha()], gerado_em=datetime(2026, 10, 30, tzinfo=timezone.utc))
        reaberto = json.loads(serializar_json(dados))
        self.assertEqual(dados, reaberto)
        self.assertTrue(validar_exportacao(reaberto))
        reaberto["registros"][0]["calculado_valor"] = "164"
        self.assertFalse(validar_exportacao(reaberto))

    def test_csv_neutraliza_formula_sem_executar_conteudo(self):
        dados = montar_exportacao([self.linha(criterio_nome=" =1+1", referencia_revisor="@SOMA(A1:A2)")])
        texto = serializar_csv(dados)
        linhas = list(csv.DictReader(io.StringIO(texto.lstrip("\ufeff"))))
        self.assertEqual("'=1+1", linhas[0]["criterio_nome"])
        self.assertEqual("'@SOMA(A1:A2)", linhas[0]["referencia_revisor"])
        self.assertEqual("04 05 30 33 41 52", linhas[0]["dezenas"])

    def test_identificador_independe_do_horario_de_exportacao(self):
        primeira = montar_exportacao([self.linha()], gerado_em=datetime(2026, 1, 1, tzinfo=timezone.utc))
        segunda = montar_exportacao([self.linha()], gerado_em=datetime(2026, 2, 1, tzinfo=timezone.utc))
        self.assertEqual(primeira["conjunto_referencias"], segunda["conjunto_referencias"])


if __name__ == "__main__":
    unittest.main()
