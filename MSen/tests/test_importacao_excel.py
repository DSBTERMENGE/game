import hashlib
import tempfile
import unittest
from datetime import date, datetime
from pathlib import Path

from openpyxl import Workbook

from msen.importacao import ErroLeituraExcel, ler_resultados_excel


CABECALHO = ["Concurso", "Data", "bola 1", "bola 2", "bola 3", "bola 4", "bola 5", "bola 6"]


class ImportacaoExcelTestCase(unittest.TestCase):
    def setUp(self):
        self._temporario = tempfile.TemporaryDirectory()
        self.pasta = Path(self._temporario.name)

    def tearDown(self):
        self._temporario.cleanup()

    def _planilha(self, nome, linhas, *, cabecalho=CABECALHO, linha_cabecalho=7):
        caminho = self.pasta / nome
        pasta = Workbook()
        folha = pasta.active
        for _ in range(linha_cabecalho - 1):
            folha.append(["apresentação"])
        folha.append(cabecalho)
        for linha in linhas:
            folha.append(linha)
        pasta.save(caminho)
        pasta.close()
        return caminho

    def test_le_arquivo_real_com_cabecalho_na_linha_sete_sem_modifica_lo(self):
        fonte = Path(__file__).parents[1] / "dados" / "fontes" / "Resultados_ate_concurso_3069_sorteio.xlsx"
        hash_antes = hashlib.sha256(fonte.read_bytes()).hexdigest()
        resultados = ler_resultados_excel(fonte)
        hash_depois = hashlib.sha256(fonte.read_bytes()).hexdigest()
        self.assertEqual(3069, len(resultados))
        self.assertEqual(3069, resultados[0].numero_ap)
        self.assertEqual(date(2026, 10, 11), resultados[0].data_resultado)
        self.assertEqual((47, 5, 22, 44, 57, 19), resultados[0].resultados)
        self.assertEqual(hash_antes, hash_depois)

    def test_localiza_cabecalho_deslocado_e_normaliza_data_do_excel(self):
        caminho = self._planilha("deslocado.xlsx", [[42, datetime(2026, 2, 1), 1, 2, 3, 4, 5, 6]], linha_cabecalho=4)
        resultado = ler_resultados_excel(caminho)[0]
        self.assertEqual(42, resultado.numero_ap)
        self.assertEqual(date(2026, 2, 1), resultado.data_resultado)

    def test_aceita_espacos_maiusculas_e_colunas_em_outra_ordem(self):
        cabecalho = [" DATA ", "BOLA 2", " concurso", "bola 1", "bola 3", "bola 4", "bola 5", "bola 6"]
        caminho = self._planilha("ordem.xlsx", [["01/02/2026", 2, 42, 1, 3, 4, 5, 6]], cabecalho=cabecalho)
        self.assertEqual((1, 2, 3, 4, 5, 6), ler_resultados_excel(caminho)[0].resultados)

    def test_rejeita_coluna_ausente_ou_renomeada(self):
        cabecalho = CABECALHO.copy()
        cabecalho[-1] = "última bola"
        caminho = self._planilha("coluna_ausente.xlsx", [], cabecalho=cabecalho)
        with self.assertRaises(ErroLeituraExcel) as contexto:
            ler_resultados_excel(caminho)
        self.assertEqual("CABECALHO_NAO_ENCONTRADO", contexto.exception.codigo)
        self.assertIn("bola 6", contexto.exception.valor)

    def test_rejeita_celula_vazia_e_informa_linha_e_campo(self):
        caminho = self._planilha("vazia.xlsx", [[42, "01/02/2026", 1, 2, None, 4, 5, 6]])
        with self.assertRaises(ErroLeituraExcel) as contexto:
            ler_resultados_excel(caminho)
        self.assertEqual("LINHA_INVALIDA", contexto.exception.codigo)
        self.assertEqual(8, contexto.exception.linha)
        self.assertEqual("res_03", contexto.exception.campo)

    def test_rejeita_data_invalida_e_informa_linha(self):
        caminho = self._planilha("data_invalida.xlsx", [[42, "31/02/2026", 1, 2, 3, 4, 5, 6]])
        with self.assertRaises(ErroLeituraExcel) as contexto:
            ler_resultados_excel(caminho)
        self.assertEqual("LINHA_INVALIDA", contexto.exception.codigo)
        self.assertEqual(8, contexto.exception.linha)
        self.assertEqual("data_resultado", contexto.exception.campo)

    def test_ignora_linhas_totalmente_vazias(self):
        caminho = self._planilha("linha_vazia.xlsx", [[42, "01/02/2026", 1, 2, 3, 4, 5, 6], [None] * 8])
        self.assertEqual(1, len(ler_resultados_excel(caminho)))


if __name__ == "__main__":
    unittest.main()
