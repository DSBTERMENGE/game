"""Aplica migrações pendentes exclusivamente ao database local games."""

import json
from pathlib import Path
import sys

from dotenv import load_dotenv

from msen.config import carregar_configuracao_banco
from msen.database import executar_migracoes


MIGRACOES = Path(__file__).resolve().parents[2] / "database" / "migrations"


def main() -> None:
    """Exige confirmação, valida o destino e aplica somente versões pendentes."""

    load_dotenv()
    if sys.argv[1:] != ["CONFIRMAR_GAMES"]:
        raise SystemExit("Uso: aplicar_migracoes_games.py CONFIRMAR_GAMES")
    configuracao = carregar_configuracao_banco()
    if configuracao.nome != "games":
        raise RuntimeError("A operação exige GAME_DB_NAME=games.")
    relatorio = executar_migracoes(configuracao, MIGRACOES)
    print(
        json.dumps(
            {
                "aplicadas": list(relatorio.aplicadas),
                "ja_aplicadas": list(relatorio.ja_aplicadas),
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
