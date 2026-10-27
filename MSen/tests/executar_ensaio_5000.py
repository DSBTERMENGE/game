"""Executa manualmente o ensaio seguro de 5.000 e imprime seu quadro JSON."""

from __future__ import annotations

import json
from pathlib import Path

from msen.screener import (
    carregar_configuracao_screener,
    executar_ensaio_amostral,
    serializar_quadro_avaliacao,
)


def main() -> None:
    """Carrega configuração local opcional e imprime o ensaio sem persistir."""

    raiz = Path(__file__).resolve().parents[1]
    configuracao = carregar_configuracao_screener(
        raiz / "config" / "screener.toml",
        raiz / "config" / "screener.local.toml",
    )
    quadro = executar_ensaio_amostral(configuracao)
    print(json.dumps(serializar_quadro_avaliacao(quadro), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
