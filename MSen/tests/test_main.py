"""Testes do ponto de entrada da aplicação."""

from msen.main import main


def test_main_exibe_mensagem_inicial(capsys) -> None:
    assert main() == 0
    assert capsys.readouterr().out == "MSen iniciado com sucesso.\n"
