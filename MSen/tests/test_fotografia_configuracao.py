"""Testes da fotografia reproduzível da configuração do screener."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
import json
import unittest

from msen.screener import (
    DefinicaoFamilia,
    DefinicaoFiltro,
    EnvelopeFotografia,
    ErroFotografia,
    FrequenciaPadraoFotografada,
    criar_fotografia_configuracao,
    criar_grupo_padroes_fotografado,
    envelopar_fotografia,
    verificar_envelope_fotografia,
)


def _avaliador_nao_executado(_combinacao):
    raise AssertionError("A fotografia não deve executar filtros.")


class FotografiaConfiguracaoTests(unittest.TestCase):
    def setUp(self) -> None:
        self.familias = (
            DefinicaoFamilia(
                "GRAF", "Geometria", 2,
                (DefinicaoFiltro("AREA", "Área", 1, _avaliador_nao_executado),),
            ),
            DefinicaoFamilia(
                "EST", "Estatística", 1,
                (
                    DefinicaoFiltro("MEDIA", "Média", 2, _avaliador_nao_executado),
                    DefinicaoFiltro("SOMA", "Soma", 1, _avaliador_nao_executado),
                ),
            ),
        )
        self.parametros = {
            "AREA": {"faixa": [Decimal("4.5"), Decimal("30.0")]},
            "MEDIA": {"desvios": Decimal("1.0")},
            "SOMA": {"referencia": date(2026, 10, 28), "desvios": Decimal("1.0")},
        }
        self.grupo = criar_grupo_padroes_fotografado(
            grupo_cod="G001", limite_raridade="10", operador="<",
            numero_ap_inicial=1, numero_ap_final=100,
            data_inicial=date(1996, 3, 11), data_final=date(2026, 10, 28),
            denominador=100,
            frequencias=(
                FrequenciaPadraoFotografada("PD_003", 10, Decimal("10")),
                FrequenciaPadraoFotografada(None, 17, Decimal("17")),
                FrequenciaPadraoFotografada("PD_001", 70, Decimal("70")),
                FrequenciaPadraoFotografada("PD_002", 3, Decimal("3")),
            ),
        )

    def _fotografia(self, **alteracoes):
        dados = {
            "familias": self.familias,
            "parametros_filtros": self.parametros,
            "grupos_padroes": (self.grupo,),
            "versoes_calculo": {"geometria": 2, "estatistica": 1},
            "modo": "experimental",
            "semente": 20261028,
            "limite_combinacoes": 5000,
        }
        dados.update(alteracoes)
        return criar_fotografia_configuracao(**dados)

    def test_fotografa_ordem_parametros_versoes_e_intervalo(self) -> None:
        fotografia = self._fotografia()
        envelope = envelopar_fotografia(fotografia)
        dados = json.loads(envelope.conteudo_json)

        self.assertEqual(["EST", "GRAF"], [item["codigo"] for item in dados["familias"]])
        self.assertEqual(["SOMA", "MEDIA"], [item["codigo"] for item in dados["familias"][0]["filtros"]])
        self.assertEqual("2026-10-28", dados["familias"][0]["filtros"][0]["parametros"]["referencia"])
        self.assertEqual(["PD_002"], dados["grupos_padroes"][0]["padroes_excludentes"])
        self.assertEqual(5000, dados["limite_combinacoes"])
        self.assertTrue(verificar_envelope_fotografia(envelope))

    def test_mesmo_conteudo_logico_produz_json_e_checksum_identicos(self) -> None:
        primeiro = envelopar_fotografia(self._fotografia())
        parametros_reordenados = {
            "SOMA": {"desvios": Decimal("1.0"), "referencia": date(2026, 10, 28)},
            "AREA": {"faixa": (Decimal("4.5"), Decimal("30.0"))},
            "MEDIA": {"desvios": Decimal("1.0")},
        }
        segundo = envelopar_fotografia(self._fotografia(
            parametros_filtros=parametros_reordenados,
            versoes_calculo={"estatistica": 1, "geometria": 2},
        ))
        self.assertEqual(primeiro, segundo)

    def test_alteracao_de_configuracao_muda_checksum(self) -> None:
        primeiro = envelopar_fotografia(self._fotografia())
        segundo = envelopar_fotografia(self._fotografia(semente=20261029))
        self.assertNotEqual(primeiro.checksum_sha256, segundo.checksum_sha256)

    def test_fotografia_nao_muda_quando_origem_e_alterada(self) -> None:
        fotografia = self._fotografia()
        envelope = envelopar_fotografia(fotografia)
        self.parametros["SOMA"]["desvios"] = Decimal("99")
        self.assertEqual(envelope, envelopar_fotografia(fotografia))

    def test_operador_define_limite_e_classe_sem_correspondencia_nao_exclui(self) -> None:
        inclusivo = criar_grupo_padroes_fotografado(
            grupo_cod="G001", limite_raridade=10, operador="<=",
            numero_ap_inicial=1, numero_ap_final=100,
            data_inicial=date(2020, 1, 1), data_final=date(2020, 12, 31),
            denominador=100, frequencias=self.grupo.frequencias,
        )
        self.assertEqual(("PD_002", "PD_003"), inclusivo.padroes_excludentes)
        self.assertNotIn(None, inclusivo.padroes_excludentes)

    def test_detecta_envelope_adulterado(self) -> None:
        envelope = envelopar_fotografia(self._fotografia())
        adulterado = EnvelopeFotografia(envelope.conteudo_json + " ", envelope.checksum_sha256)
        self.assertFalse(verificar_envelope_fotografia(adulterado))

    def test_rejeita_tipos_ambiguos_e_parametros_incompletos(self) -> None:
        with self.assertRaisesRegex(ErroFotografia, "tipo não permitido"):
            self._fotografia(parametros_filtros={**self.parametros, "SOMA": {"valor": 1.5}})
        with self.assertRaisesRegex(ErroFotografia, "corresponder exatamente"):
            self._fotografia(parametros_filtros={"SOMA": {}})

    def test_rejeita_frequencia_que_nao_reconcilia(self) -> None:
        with self.assertRaisesRegex(ErroFotografia, "não reconciliam"):
            criar_grupo_padroes_fotografado(
                grupo_cod="G001", limite_raridade=10, operador="<",
                numero_ap_inicial=1, numero_ap_final=1,
                data_inicial=date(2020, 1, 1), data_final=date(2020, 1, 1),
                denominador=1,
                frequencias=(FrequenciaPadraoFotografada("PD_001", 1, Decimal("99")),),
            )


if __name__ == "__main__":
    unittest.main()
