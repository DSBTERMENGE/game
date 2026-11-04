import unittest
from pathlib import Path


RAIZ = Path(__file__).resolve().parents[2]


class TestDocumentacao2313(unittest.TestCase):
    def test_documentos_canonicos_da_selecao_existem(self):
        caminhos = (
            "docs/CONTRATO_SELECAO_DEZENAS.md",
            "docs/CONTRATO_BACKTEST_SELECAO_DEZENAS.md",
            "docs/MODELO_PESQUISA_SELECAO_DEZENAS.md",
            "docs/API_SELECAO_DEZENAS.md",
            "docs/funcionamento.md",
            "frontend/selecao-dezenas.html",
            "MSen/src/msen/api/selecao_dezenas.py",
        )
        for caminho in caminhos:
            with self.subTest(caminho=caminho):
                self.assertTrue((RAIZ / caminho).is_file())

    def test_ajuda_expoe_formula_fluxo_custo_e_cautela(self):
        ajuda = (RAIZ / "frontend/selecao-dezenas.html").read_text(encoding="utf-8")
        for trecho in (
            "última ocorrência + média dos intervalos + j × desvio-padrão",
            "k × desvio-padrão",
            "C(N,6)",
            "Fluxo recomendado",
            "não garante desempenho futuro",
        ):
            self.assertIn(trecho, ajuda)

    def test_funcionamento_e_rotas_estao_sincronizados(self):
        funcionamento = (RAIZ / "docs/funcionamento.md").read_text(encoding="utf-8")
        codigo = (RAIZ / "MSen/src/msen/api/selecao_dezenas.py").read_text(encoding="utf-8")
        self.assertIn("selecao-dezenas.html", funcionamento)
        for rota in (
            "/api/selecao-dezenas/configuracoes",
            "/api/selecao-dezenas/previa",
            "/api/selecao-dezenas/backtests",
            "/api/selecao-dezenas/previsoes",
            "/api/selecao-dezenas/alvos/",
        ):
            self.assertIn(rota, funcionamento)
            self.assertIn(rota, codigo)

    def test_tabelas_documentadas_existem_no_esquema(self):
        modelo = (RAIZ / "docs/MODELO_PESQUISA_SELECAO_DEZENAS.md").read_text(encoding="utf-8")
        esquema = (RAIZ / "database/schema_postgresql.sql").read_text(encoding="utf-8")
        for tabela in (
            "configuracoes_pesquisa_selecao",
            "execucoes_pesquisa_selecao",
            "alvos_pesquisa_selecao",
            "avaliacoes_dezenas_pesquisa",
            "lotes_jogos_selecao",
            "jogos_selecao_dezenas",
        ):
            self.assertIn(tabela, modelo)
            self.assertIn(f"CREATE TABLE {tabela}", esquema)

    def test_modelo_nao_contem_decisoes_superadas(self):
        modelo = (RAIZ / "docs/MODELO_PESQUISA_SELECAO_DEZENAS.md").read_text(encoding="utf-8")
        for trecho in (
            "Não será criada nesta etapa uma tabela com todas as combinações de seis",
            "futuras restrições, mas não executa DDL",
        ):
            self.assertNotIn(trecho, modelo)


if __name__ == "__main__":
    unittest.main()
