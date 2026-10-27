import inspect
import unittest

import msen.padroes as padroes
from msen.padroes import (
    CodigoPadraoInvalido,
    DetectorJaRegistrado,
    DetectorNaoRegistrado,
    RegistroDetectores,
)


def detector_falso(dezenas: tuple[int, ...]) -> bool:
    """Detector controlado usado somente pelos testes da infraestrutura."""

    return False


class EstruturaPadroesTestCase(unittest.TestCase):
    def test_pacote_inicia_sem_detector_antecipado(self):
        registro = RegistroDetectores()
        self.assertEqual((), registro.codigos_registrados())

    def test_registra_e_recupera_detector_pelo_codigo_estavel(self):
        registro = RegistroDetectores()
        registro.registrar("PD_001", detector_falso)
        self.assertTrue(registro.contem("PD_001"))
        self.assertIs(detector_falso, registro.obter("PD_001"))
        self.assertEqual(("PD_001",), registro.codigos_registrados())

    def test_rejeita_codigo_fora_do_contrato(self):
        registro = RegistroDetectores()
        for codigo in ("P1", "pd_001", "PD_01", "PD_ABC", ""):
            with self.subTest(codigo=codigo):
                with self.assertRaises(CodigoPadraoInvalido):
                    registro.registrar(codigo, detector_falso)

    def test_rejeita_objeto_que_nao_seja_funcao_chamavel(self):
        registro = RegistroDetectores()
        with self.assertRaises(TypeError):
            registro.registrar("PD_001", None)  # type: ignore[arg-type]

    def test_nao_substitui_detector_ja_registrado(self):
        registro = RegistroDetectores()
        registro.registrar("PD_001", detector_falso)
        with self.assertRaises(DetectorJaRegistrado):
            registro.registrar("PD_001", lambda dezenas: True)

    def test_diferencia_detector_pendente_de_resultado_falso(self):
        registro = RegistroDetectores()
        with self.assertRaises(DetectorNaoRegistrado):
            registro.obter("PD_001")

        registro.registrar("PD_001", detector_falso)
        self.assertFalse(registro.obter("PD_001")((1, 2, 3, 4, 5, 6)))

    def test_todos_os_elementos_publicos_exportados_possuem_descricao(self):
        for nome in padroes.__all__:
            with self.subTest(nome=nome):
                elemento = getattr(padroes, nome)
                if inspect.isclass(elemento) or inspect.isfunction(elemento):
                    self.assertTrue(inspect.getdoc(elemento))

        for nome in ("registrar", "obter", "contem", "codigos_registrados"):
            with self.subTest(nome=f"RegistroDetectores.{nome}"):
                self.assertTrue(inspect.getdoc(getattr(RegistroDetectores, nome)))


if __name__ == "__main__":
    unittest.main()
