import unittest
from pathlib import Path


RAIZ = Path(__file__).resolve().parents[2]


class TestDocumentacao2017(unittest.TestCase):
    def test_documentos_canonicos_e_historicos_existem(self):
        caminhos = (
            "PLANO_ETAPAS_E_TESTES.md", "PLANO_DO_PROJETO.md", "CONTINUIDADE_IA.md",
            "docs/funcionamento.md", "docs/INDICE_DOCUMENTACAO.md",
            "docs/API_VALIDACAO.md", "docs/CONTRATO_HOMOLOGACAO_FUNCOES.md",
            "docs/funcionamento_historico_ate_etapa_19.md",
            "docs/PLANO_DO_PROJETO_HISTORICO.md", "database/schema_postgresql.sql",
        )
        for caminho in caminhos:
            with self.subTest(caminho=caminho):
                self.assertTrue((RAIZ / caminho).is_file())

    def test_rotas_documentadas_existem_no_codigo(self):
        funcionamento = (RAIZ / "docs/funcionamento.md").read_text(encoding="utf-8")
        codigo = "\n".join(
            caminho.read_text(encoding="utf-8")
            for caminho in (RAIZ / "MSen/src/msen/api").glob("*.py")
        )
        rotas = (
            "/api/screener/quadro", "/api/validacao/quadro",
            "/api/validacao/relatorio", "/api/validacao/exportacao",
            "/api/validacao/execucoes",
        )
        for rota in rotas:
            self.assertIn(rota, funcionamento)
            self.assertIn(rota, codigo)

    def test_tabelas_documentadas_existem_no_esquema(self):
        funcionamento = (RAIZ / "docs/funcionamento.md").read_text(encoding="utf-8")
        esquema = (RAIZ / "database/schema_postgresql.sql").read_text(encoding="utf-8")
        for tabela in (
            "resultados", "padroes_grupo", "padroes_subgrupo",
            "resultado_classificacao_padrao", "amostras_validacao",
            "criterios_validacao", "avaliacoes_validacao",
            "estado_algoritmo_selecao", "perfis_operacionais_atuais",
        ):
            self.assertIn(tabela, funcionamento)
            self.assertIn(f"TABLE IF NOT EXISTS {tabela}", esquema)

    def test_documentos_vigentes_nao_repetem_contratos_revogados(self):
        textos = "\n".join(
            (RAIZ / caminho).read_text(encoding="utf-8")
            for caminho in ("PLANO_DO_PROJETO.md", "docs/funcionamento.md", "docs/visao-geral.md")
        )
        for frase in (
            "ainda não integrada à aplicação Python",
            "nenhuma fórmula definitiva deverá ser codificada",
            "a auditoria ainda será desenvolvida",
            "gravação desses dados depende das etapas de persistência",
        ):
            self.assertNotIn(frase, textos)


if __name__ == "__main__":
    unittest.main()
