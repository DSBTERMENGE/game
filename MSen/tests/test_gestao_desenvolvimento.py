"""Testes das regras da Gestão do desenvolvimento."""

import unittest

from msen.services.gestao_desenvolvimento import (
    DadosManutencao, ErroGestaoDesenvolvimento,
)


class GestaoDesenvolvimentoTest(unittest.TestCase):
    def test_normaliza_dados_e_aplica_padroes(self):
        dados = DadosManutencao.validar({
            "titulo": "  Melhorar pesquisa  ",
            "data_registro": "2026-11-11",
            "descricao": "  Permitir busca parcial. ",
        })
        self.assertEqual("Melhorar pesquisa", dados.titulo)
        self.assertEqual("NAO_CLASSIFICADO", dados.tipo)
        self.assertEqual("2026-11-11", dados.data_registro.isoformat())
        self.assertEqual("NAO_INICIADO", dados.status_trabalho)

    def test_aceita_conclusao_sem_campos_auxiliares(self):
        dados = DadosManutencao.validar({
            "titulo": "Item", "descricao": "Descrição",
            "data_registro": "2026-11-11",
            "status_trabalho": "CONCLUIDO",
        })
        self.assertEqual("CONCLUIDO", dados.status_trabalho)

    def test_rejeita_falha_publicacao_sem_observacao(self):
        with self.assertRaisesRegex(ErroGestaoDesenvolvimento, "falha"):
            DadosManutencao.validar({
                "titulo": "Item", "descricao": "Descrição",
                "data_registro": "2026-11-11",
                "status_publicacao": "FALHA_PUBLICACAO",
            })

    def test_rejeita_campos_desconhecidos(self):
        with self.assertRaises(ErroGestaoDesenvolvimento) as contexto:
            DadosManutencao.validar({
                "titulo": "Item", "descricao": "Descrição", "id_manutencao": 8,
                "data_registro": "2026-11-11",
            })
        self.assertEqual("CAMPOS_DESCONHECIDOS", contexto.exception.codigo)


if __name__ == "__main__":
    unittest.main()
