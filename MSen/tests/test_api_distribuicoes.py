"""Testes do contrato HTTP das distribuições da Etapa 17.5."""

from datetime import date
from decimal import Decimal
import unittest

from msen.api import criar_app
from msen.api.distribuicoes import ErroDistribuicoes, _perfil_json
from msen.services import calcular_perfil_estatistico


def resposta_teste() -> dict[str, object]:
    return {
        "janela": {"quantidade_resultados": 2, "corte_exclusivo": True},
        "parametros": [],
        "ativa_no_screener": False,
    }


class ApiDistribuicoesTestCase(unittest.TestCase):
    def _cliente(self, servico=None):
        return criar_app({
            "TESTING": True,
            "CALCULAR_DISTRIBUICOES": servico or (lambda *_args: resposta_teste()),
        }).test_client()

    def test_retorna_contrato_e_mantem_screener_inativo(self) -> None:
        resposta = self._cliente().get("/api/perfis/distribuicoes")
        corpo = resposta.get_json()["distribuicoes"]

        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(corpo["janela"]["quantidade_resultados"], 2)
        self.assertTrue(corpo["janela"]["corte_exclusivo"])
        self.assertFalse(corpo["ativa_no_screener"])

    def test_encaminha_corte_classes_metodo_e_margens(self) -> None:
        recebidos = []

        def servico(*argumentos):
            recebidos.append(argumentos)
            return resposta_teste()

        resposta = self._cliente(servico).get(
            "/api/perfis/distribuicoes?numero_ap_antes_de=100&classes=8"
            "&metodo_faixa=percentual_media&margem_inferior=10&margem_superior=20"
        )

        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(
            recebidos,
            [(100, None, 8, "percentual_media", Decimal("10"), Decimal("20"))],
        )

    def test_encaminha_corte_exclusivo_por_data(self) -> None:
        recebidos = []

        def servico(*argumentos):
            recebidos.append(argumentos)
            return resposta_teste()

        resposta = self._cliente(servico).get(
            "/api/perfis/distribuicoes?data_antes_de=2026-10-28"
        )

        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(
            recebidos,
            [(None, date(2026, 10, 28), 10, "desvio_padrao", Decimal(1), Decimal(1))],
        )

    def test_rejeita_parametros_invalidos(self) -> None:
        casos = (
            ("numero_ap_antes_de=0", "CONCURSO_INVALIDO"),
            ("data_antes_de=28-10-2026", "DATA_INVALIDA"),
            ("numero_ap_antes_de=2&data_antes_de=2026-01-01", "CORTES_CONFLITANTES"),
            ("classes=0", "CLASSES_INVALIDAS"),
            ("classes=51", "CLASSES_INVALIDAS"),
            ("metodo_faixa=x", "METODO_INVALIDO"),
            ("margem_inferior=-1", "MARGEM_INVALIDA"),
            ("desconhecido=1", "PARAMETRO_DESCONHECIDO"),
        )
        for consulta, codigo in casos:
            with self.subTest(consulta=consulta):
                resposta = self._cliente().get(f"/api/perfis/distribuicoes?{consulta}")
                self.assertEqual(resposta.status_code, 400)
                self.assertEqual(resposta.get_json()["erro"]["codigo"], codigo)

    def test_protege_janela_vazia_e_geometria_incompleta(self) -> None:
        for codigo, status in (("JANELA_VAZIA", 400), ("GEOMETRIA_INCOMPLETA", 409)):
            with self.subTest(codigo=codigo):
                def falhar(*_args, codigo=codigo):
                    raise ErroDistribuicoes(codigo, "detalhe controlado")

                resposta = self._cliente(falhar).get("/api/perfis/distribuicoes")
                self.assertEqual(resposta.status_code, status)
                self.assertEqual(resposta.get_json()["erro"]["codigo"], codigo)

    def test_serializacao_e_reproduzivel_e_expoe_normal_como_referencia(self) -> None:
        perfil = calcular_perfil_estatistico((2, 4, 4, 4, 5, 5, 7, 9))
        argumentos = dict(
            classes=4,
            metodo_faixa="desvio_padrao",
            margem_inferior=Decimal(1),
            margem_superior=Decimal(2),
        )

        primeiro = _perfil_json("EST_MEDIA", perfil, **argumentos)
        segundo = _perfil_json("EST_MEDIA", perfil, **argumentos)

        self.assertEqual(primeiro, segundo)
        self.assertEqual(primeiro["faixa"]["limite_inferior"], "3")
        self.assertEqual(primeiro["faixa"]["limite_superior"], "9")
        self.assertFalse(primeiro["faixa"]["ativa_no_screener"])
        self.assertEqual(
            primeiro["curva_normal_referencia"]["uso"], "REFERENCIA_VISUAL"
        )


if __name__ == "__main__":
    unittest.main()
