import io
import unittest
from pathlib import Path

from msen.api import criar_app
from msen.database import ErroRepositorioResultado
from msen.importacao import ler_linhas_excel
from msen.services import RelatorioImportacaoBanco


FIXTURES = Path(__file__).parent / "fixtures"


def relatorio(*, inseridas=2, iguais=0):
    return RelatorioImportacaoBanco(
        arquivo="fonte.xlsx",
        sha256="a" * 64,
        iniciada_em="2026-10-26T00:00:00+00:00",
        concluida_em="2026-10-26T00:00:01+00:00",
        registros_antes=iguais,
        registros_depois=iguais + inseridas,
        linhas_analisadas=inseridas + iguais,
        novas=inseridas,
        inseridas=inseridas,
        iguais=iguais,
        alteradas=0,
        invalidas=0,
        concursos_inseridos=tuple(range(100, 100 + inseridas)),
        concursos_alterados=(),
        linhas_invalidas=(),
    )


def upload_fixture(nome="resultados_validos.xlsx"):
    return io.BytesIO((FIXTURES / nome).read_bytes()), nome


class ApiImportacaoTestCase(unittest.TestCase):
    def _cliente(self, servico, **configuracao):
        return criar_app({
            "TESTING": True,
            "IMPORTAR_RESULTADOS": servico,
            **configuracao,
        }).test_client()

    def test_importa_arquivo_valido_e_devolve_relatorio(self):
        caminhos = []

        def importar(caminho):
            caminhos.append(Path(caminho))
            self.assertTrue(Path(caminho).is_file())
            return relatorio()

        resposta = self._cliente(importar).post(
            "/api/resultados/importar",
            data={"arquivo": upload_fixture()},
            content_type="multipart/form-data",
        )

        self.assertEqual(200, resposta.status_code)
        self.assertEqual(2, resposta.get_json()["relatorio"]["inseridas"])
        self.assertEqual("resultados_validos.xlsx", resposta.get_json()["relatorio"]["arquivo"])
        self.assertFalse(caminhos[0].exists())

    def test_reimportacao_incremental_nao_duplica(self):
        respostas = iter((relatorio(inseridas=2), relatorio(inseridas=0, iguais=2)))
        cliente = self._cliente(lambda _caminho: next(respostas))

        primeira = cliente.post("/api/resultados/importar", data={"arquivo": upload_fixture()})
        segunda = cliente.post("/api/resultados/importar", data={"arquivo": upload_fixture()})

        self.assertEqual(2, primeira.get_json()["relatorio"]["inseridas"])
        self.assertEqual(0, segunda.get_json()["relatorio"]["inseridas"])
        self.assertEqual(2, segunda.get_json()["relatorio"]["iguais"])

    def test_rejeita_extensao_incorreta_sem_chamar_servico(self):
        chamado = False

        def importar(_caminho):
            nonlocal chamado
            chamado = True

        resposta = self._cliente(importar).post(
            "/api/resultados/importar",
            data={"arquivo": (io.BytesIO(b"texto"), "dados.csv")},
        )

        self.assertEqual(415, resposta.status_code)
        self.assertEqual("FORMATO_NAO_SUPORTADO", resposta.get_json()["erro"]["codigo"])
        self.assertFalse(chamado)

    def test_rejeita_arquivo_xlsx_corrompido(self):
        resposta = self._cliente(ler_linhas_excel).post(
            "/api/resultados/importar",
            data={"arquivo": (io.BytesIO(b"nao e um zip"), "corrompido.xlsx")},
        )

        self.assertEqual(422, resposta.status_code)
        self.assertEqual("ARQUIVO_INVALIDO", resposta.get_json()["erro"]["codigo"])

    def test_rejeita_arquivo_acima_do_limite(self):
        resposta = self._cliente(
            lambda _caminho: relatorio(), MAX_CONTENT_LENGTH=256
        ).post(
            "/api/resultados/importar",
            data={"arquivo": (io.BytesIO(b"x" * 1024), "grande.xlsx")},
        )

        self.assertEqual(413, resposta.status_code)
        self.assertEqual("ARQUIVO_MUITO_GRANDE", resposta.get_json()["erro"]["codigo"])

    def test_falha_de_persistencia_retorna_erro_seguro_e_remove_temporario(self):
        caminhos = []
        segredo = "senha-que-nao-pode-aparecer"

        def falhar(caminho):
            caminhos.append(Path(caminho))
            raise ErroRepositorioResultado("FALHA_INSERCAO", segredo)

        resposta = self._cliente(falhar).post(
            "/api/resultados/importar", data={"arquivo": upload_fixture()}
        )
        texto = resposta.get_data(as_text=True)

        self.assertEqual(503, resposta.status_code)
        self.assertEqual("IMPORTACAO_INDISPONIVEL", resposta.get_json()["erro"]["codigo"])
        self.assertNotIn(segredo, texto)
        self.assertFalse(caminhos[0].exists())

    def test_rejeita_arquivo_ausente_ou_vazio(self):
        cliente = self._cliente(lambda _caminho: relatorio())
        ausente = cliente.post("/api/resultados/importar")
        vazio = cliente.post(
            "/api/resultados/importar",
            data={"arquivo": (io.BytesIO(b""), "vazio.xlsx")},
        )

        self.assertEqual(400, ausente.status_code)
        self.assertEqual("ARQUIVO_AUSENTE", ausente.get_json()["erro"]["codigo"])
        self.assertEqual(400, vazio.status_code)
        self.assertEqual("ARQUIVO_VAZIO", vazio.get_json()["erro"]["codigo"])


if __name__ == "__main__":
    unittest.main()
