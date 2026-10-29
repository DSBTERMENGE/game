from datetime import date
from decimal import Decimal
from unittest.mock import Mock
import unittest

from msen.padroes import criar_registro_detectores_aprovados
from msen.padroes.registro import RegistroDetectores
from msen.screener import (
    FrequenciaPadraoFotografada,
    criar_familia_detectores_raros,
    criar_grupo_padroes_fotografado,
    executar_funil_extensivel,
)


GRUPO_POR_PADRAO = {
    "PD_001": "PG_001", "PD_002": "PG_001", "PD_003": "PG_001",
    "PD_004": "PG_002", "PD_005": "PG_002", "PD_006": "PG_002",
    "PD_007": "PG_003", "PD_008": "PG_003", "PD_009": "PG_003",
}

CASOS_POSITIVOS = {
    "PD_001": (1, 2, 10, 20, 30, 40),
    "PD_002": (1, 2, 3, 10, 20, 40),
    "PD_003": (1, 2, 3, 4, 20, 40),
    "PD_004": (1, 11, 23, 36, 48, 60),
    "PD_005": (1, 11, 21, 34, 48, 60),
    "PD_006": (1, 11, 21, 31, 48, 60),
    "PD_007": (1, 5, 18, 27, 44, 59),
    "PD_008": (1, 5, 9, 18, 27, 44),
    "PD_009": (1, 3, 5, 7, 20, 40),
}


def fotografar(grupo_cod, codigos, limite=10):
    return criar_grupo_padroes_fotografado(
        grupo_cod=grupo_cod,
        limite_raridade=limite,
        operador="<",
        numero_ap_inicial=1,
        numero_ap_final=100,
        data_inicial=date(2020, 1, 1),
        data_final=date(2026, 10, 29),
        denominador=100,
        frequencias=tuple(
            FrequenciaPadraoFotografada(codigo, 1, Decimal(1))
            for codigo in codigos
        ),
    )


class FamiliaDetectoresRarosTests(unittest.TestCase):
    def test_limite_zero_cria_familia_sem_detectores_e_aprova_saldo(self):
        familia = criar_familia_detectores_raros(
            grupos_fotografados=(), registro=RegistroDetectores()
        )
        relatorio = executar_funil_extensivel(
            ((1, 10, 20, 30, 40, 50),), (familia,)
        )
        self.assertEqual((), familia.filtros)
        self.assertEqual(0, relatorio.total_excluido)
        self.assertEqual(1, relatorio.total_aprovado)

    def test_cada_detector_aprovado_exclui_seu_caso_manual(self):
        registro = criar_registro_detectores_aprovados()
        for codigo, combinacao in CASOS_POSITIVOS.items():
            with self.subTest(codigo=codigo):
                familia = criar_familia_detectores_raros(
                    grupos_fotografados=(
                        fotografar(GRUPO_POR_PADRAO[codigo], (codigo,)),
                    ),
                    registro=registro,
                )
                decisao = familia.filtros[0].avaliador(combinacao)
                self.assertFalse(decisao.aprovada)
                self.assertEqual("PADRAO_RARO_DETECTADO", decisao.motivo)
                self.assertEqual(codigo, decisao.evidencias["padrao_cod"])

    def test_detector_nao_selecionado_nao_e_executado(self):
        selecionado = Mock(return_value=False)
        nao_selecionado = Mock(side_effect=AssertionError("não deveria executar"))
        registro = RegistroDetectores()
        registro.registrar("PD_001", nao_selecionado)
        registro.registrar("PD_002", selecionado)

        familia = criar_familia_detectores_raros(
            grupos_fotografados=(fotografar("PG_001", ("PD_002",)),),
            registro=registro,
        )
        familia.filtros[0].avaliador((1, 10, 20, 30, 40, 50))

        selecionado.assert_called_once()
        nao_selecionado.assert_not_called()

    def test_funil_para_na_primeira_exclusao_e_contabiliza_o_padrao(self):
        oficial = criar_registro_detectores_aprovados()
        pd003 = Mock(wraps=oficial.obter("PD_003"))
        pd009 = Mock(wraps=oficial.obter("PD_009"))
        registro = RegistroDetectores()
        registro.registrar("PD_003", pd003)
        registro.registrar("PD_009", pd009)
        familia = criar_familia_detectores_raros(
            grupos_fotografados=(
                fotografar("PG_001", ("PD_003",)),
                fotografar("PG_003", ("PD_009",)),
            ),
            registro=registro,
        )

        relatorio = executar_funil_extensivel(
            ((1, 2, 3, 4, 20, 40), (1, 3, 5, 7, 20, 40)),
            (familia,),
        )

        self.assertEqual(2, relatorio.total_excluido)
        self.assertEqual((2, 1), tuple(item.avaliacoes for item in relatorio.familias[0].filtros))
        self.assertEqual((1, 1), tuple(item.exclusoes for item in relatorio.familias[0].filtros))
        self.assertEqual(2, pd003.call_count)
        self.assertEqual(1, pd009.call_count)


if __name__ == "__main__":
    unittest.main()
