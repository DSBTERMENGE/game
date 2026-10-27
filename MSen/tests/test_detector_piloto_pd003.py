from pathlib import Path
import sys
import unittest

from msen.padroes import (
    detectar_duas_dezenas_sequenciais,
    detectar_tres_dezenas_sequenciais,
)

sys.path.insert(0, str(Path(__file__).resolve().parent))
from validar_detector_pd003 import CASOS_BOOLEANOS, avaliar_casos_pd003


class DetectorPilotoPD003TestCase(unittest.TestCase):
    def test_todos_os_casos_aprovados_estao_conformes(self):
        casos = avaliar_casos_pd003()
        self.assertEqual(20, len(casos))
        divergentes = [item for item in casos if not item["conforme"]]
        self.assertEqual([], divergentes)

    def test_casos_positivos_sao_exclusivos_do_pd003(self):
        positivos = (item for item in CASOS_BOOLEANOS if item[2] is True)
        for codigo, dezenas, _esperado, _motivo in positivos:
            with self.subTest(caso=codigo):
                self.assertFalse(detectar_duas_dezenas_sequenciais(dezenas))
                self.assertFalse(detectar_tres_dezenas_sequenciais(dezenas))


if __name__ == "__main__":
    unittest.main()
