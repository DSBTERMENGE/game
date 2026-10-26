import unittest

import psycopg

from msen.config import (
    ConfiguracaoBanco,
    ErroConfiguracaoBanco,
    carregar_configuracao_banco,
)
from msen.database import ErroConexaoBanco, abrir_conexao


AMBIENTE_VALIDO = {
    "GAME_DB_HOST": "127.0.0.1",
    "GAME_DB_PORT": "5432",
    "GAME_DB_NAME": "games",
    "GAME_DB_USER": "game_app",
    "GAME_DB_PASSWORD": "segredo-de-teste",
    "GAME_DB_SSLMODE": "prefer",
    "GAME_DB_CONNECT_TIMEOUT": "5",
}


class ConfiguracaoBancoTestCase(unittest.TestCase):
    def test_carrega_configuracao_valida(self):
        configuracao = carregar_configuracao_banco(AMBIENTE_VALIDO)
        self.assertEqual("127.0.0.1", configuracao.host)
        self.assertEqual(5432, configuracao.porta)
        self.assertEqual("games", configuracao.nome)

    def test_senha_ausente_e_rejeitada(self):
        ambiente = dict(AMBIENTE_VALIDO)
        ambiente.pop("GAME_DB_PASSWORD")
        with self.assertRaises(ErroConfiguracaoBanco) as contexto:
            carregar_configuracao_banco(ambiente)
        self.assertEqual("VARIAVEL_OBRIGATORIA_AUSENTE", contexto.exception.codigo)
        self.assertEqual("GAME_DB_PASSWORD", contexto.exception.variavel)

    def test_senha_vazia_e_rejeitada(self):
        ambiente = dict(AMBIENTE_VALIDO, GAME_DB_PASSWORD="  ")
        with self.assertRaises(ErroConfiguracaoBanco):
            carregar_configuracao_banco(ambiente)

    def test_porta_e_tempo_limite_invalidos_sao_rejeitados(self):
        for variavel, valor in (("GAME_DB_PORT", "abc"), ("GAME_DB_PORT", "70000"),
                                ("GAME_DB_CONNECT_TIMEOUT", "0")):
            with self.subTest(variavel=variavel, valor=valor):
                ambiente = dict(AMBIENTE_VALIDO, **{variavel: valor})
                with self.assertRaises(ErroConfiguracaoBanco):
                    carregar_configuracao_banco(ambiente)

    def test_sslmode_invalido_e_rejeitado(self):
        ambiente = dict(AMBIENTE_VALIDO, GAME_DB_SSLMODE="inventado")
        with self.assertRaises(ErroConfiguracaoBanco) as contexto:
            carregar_configuracao_banco(ambiente)
        self.assertEqual("SSLMODE_INVALIDO", contexto.exception.codigo)

    def test_representacao_da_configuracao_oculta_senha(self):
        configuracao = carregar_configuracao_banco(AMBIENTE_VALIDO)
        representacao = repr(configuracao)
        self.assertNotIn("segredo-de-teste", representacao)
        self.assertIn("senha='***'", representacao)

    def test_abertura_envia_parametros_separados_ao_driver(self):
        recebidos = {}
        sentinela = object()

        def conector(**parametros):
            recebidos.update(parametros)
            return sentinela

        configuracao = carregar_configuracao_banco(AMBIENTE_VALIDO)
        self.assertIs(sentinela, abrir_conexao(configuracao, conector=conector))
        self.assertEqual("segredo-de-teste", recebidos["password"])
        self.assertNotIn("dsn", recebidos)

    def test_falha_do_driver_nao_expoe_credenciais(self):
        def conector(**_):
            raise psycopg.OperationalError("erro que contém segredo-de-teste")

        configuracao = carregar_configuracao_banco(AMBIENTE_VALIDO)
        with self.assertRaises(ErroConexaoBanco) as contexto:
            abrir_conexao(configuracao, conector=conector)
        mensagem = str(contexto.exception)
        self.assertNotIn("segredo-de-teste", mensagem)
        self.assertEqual("FALHA_CONEXAO", contexto.exception.codigo)

    def test_exige_objeto_de_configuracao_validado(self):
        with self.assertRaises(TypeError):
            abrir_conexao(object())


if __name__ == "__main__":
    unittest.main()
