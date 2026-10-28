from datetime import date
from decimal import Decimal
import unittest

from msen.api import criar_app
from msen.services import (
    ClassePerfilPadrao,
    ErroRecalculoClassificacao,
    PerfilClassificacaoGrupo,
)


def perfil_teste() -> PerfilClassificacaoGrupo:
    classes = (
        ClassePerfilPadrao(
            "PD_001", 8, Decimal("80.000000"), Decimal("88.888889"),
            Decimal("2.000000"), Decimal("1.000000"), False,
        ),
        ClassePerfilPadrao(
            "PD_002", 1, Decimal("10.000000"), Decimal("11.111111"),
            None, None, False,
        ),
        ClassePerfilPadrao(
            "PD_003", 0, Decimal("0.000000"), Decimal("0.000000"),
            None, None, True,
        ),
        ClassePerfilPadrao(
            None, 1, Decimal("10.000000"), None, None, None, False,
        ),
    )
    return PerfilClassificacaoGrupo(
        "PG_001",
        10,
        9,
        Decimal("10.000000"),
        "<",
        1,
        10,
        date(2026, 1, 1),
        date(2026, 2, 1),
        (1,),
        classes,
        ("PD_003",),
    )


class ApiPerfisPadroesTestCase(unittest.TestCase):
    def _cliente(self, servico=None):
        return criar_app({
            "TESTING": True,
            "CALCULAR_PERFIL_PADROES": servico or (lambda *_args: perfil_teste()),
        }).test_client()

    def test_retorna_contrato_completo_e_nao_ativa_screener(self):
        resposta = self._cliente().get("/api/grupos-padroes/PG_001/perfil")
        corpo = resposta.get_json()["perfil"]
        self.assertEqual(200, resposta.status_code)
        self.assertEqual(10, corpo["amostra"]["total_resultados"])
        self.assertEqual("2026-01-01", corpo["amostra"]["data_inicial"])
        self.assertEqual(["PD_003"], corpo["raridade"]["padroes_indicados"])
        self.assertFalse(corpo["raridade"]["ativa_no_screener"])
        self.assertEqual("2.000000", corpo["classes"][0]["intervalo_medio"])
        self.assertEqual("SEM_CORRESPONDENCIA", corpo["classes"][-1]["estado"])

    def test_encaminha_corte_por_concurso_inclusivo(self):
        recebidos = []

        def servico(limite, numero, data_corte):
            recebidos.append((limite, numero, data_corte))
            return perfil_teste()

        resposta = self._cliente(servico).get(
            "/api/grupos-padroes/PG_001/perfil?limite_raridade=5.5&numero_ap_ate=100"
        )
        self.assertEqual(200, resposta.status_code)
        self.assertEqual([(Decimal("5.5"), 100, None)], recebidos)

    def test_encaminha_corte_por_data(self):
        recebidos = []

        def servico(limite, numero, data_corte):
            recebidos.append((limite, numero, data_corte))
            return perfil_teste()

        resposta = self._cliente(servico).get(
            "/api/grupos-padroes/PG_001/perfil?data_ate=2026-10-28"
        )
        self.assertEqual(200, resposta.status_code)
        self.assertEqual([(Decimal("10"), None, date(2026, 10, 28))], recebidos)

    def test_rejeita_cortes_conflitantes(self):
        resposta = self._cliente().get(
            "/api/grupos-padroes/PG_001/perfil?numero_ap_ate=10&data_ate=2026-01-01"
        )
        self.assertEqual(400, resposta.status_code)
        self.assertEqual("CORTES_CONFLITANTES", resposta.get_json()["erro"]["codigo"])

    def test_rejeita_parametros_invalidos(self):
        casos = (
            ("limite_raridade=x", "LIMITE_INVALIDO"),
            ("limite_raridade=101", "LIMITE_INVALIDO"),
            ("numero_ap_ate=0", "CONCURSO_INVALIDO"),
            ("numero_ap_ate=1.5", "CONCURSO_INVALIDO"),
            ("data_ate=28-10-2026", "DATA_INVALIDA"),
            ("desconhecido=1", "PARAMETRO_DESCONHECIDO"),
        )
        for consulta, codigo in casos:
            with self.subTest(consulta=consulta):
                resposta = self._cliente().get(
                    f"/api/grupos-padroes/PG_001/perfil?{consulta}"
                )
                self.assertEqual(400, resposta.status_code)
                self.assertEqual(codigo, resposta.get_json()["erro"]["codigo"])

    def test_rejeita_grupo_invalido_ou_nao_implementado(self):
        invalido = self._cliente().get("/api/grupos-padroes/pg-1/perfil")
        futuro = self._cliente().get("/api/grupos-padroes/PG_002/perfil")
        self.assertEqual(400, invalido.status_code)
        self.assertEqual("GRUPO_INVALIDO", invalido.get_json()["erro"]["codigo"])
        self.assertEqual(404, futuro.status_code)
        self.assertEqual("GRUPO_NAO_IMPLEMENTADO", futuro.get_json()["erro"]["codigo"])

    def test_classificacao_incompleta_retorna_conflito_sem_detalhe(self):
        segredo = "detalhe-interno"

        def falhar(*_args):
            raise ErroRecalculoClassificacao("CLASSIFICACAO_INCOMPLETA", segredo)

        resposta = self._cliente(falhar).get("/api/grupos-padroes/PG_001/perfil")
        self.assertEqual(409, resposta.status_code)
        self.assertEqual("CLASSIFICACAO_INCOMPLETA", resposta.get_json()["erro"]["codigo"])
        self.assertNotIn(segredo, resposta.get_data(as_text=True))


if __name__ == "__main__":
    unittest.main()
