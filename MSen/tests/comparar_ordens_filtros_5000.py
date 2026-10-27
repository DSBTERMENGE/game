"""Imprime a comparação reproduzível das ordens do funil experimental."""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from msen.screener import carregar_configuracao_screener, comparar_ordens_filtros


def main() -> None:
    """Executa as três ordens autorizadas sobre a amostra de 5.000."""

    raiz = Path(__file__).resolve().parents[1]
    configuracao = carregar_configuracao_screener(raiz / "config" / "screener.toml")
    for resultado in comparar_ordens_filtros(configuracao):
        print(
            resultado.nome,
            f"avaliacoes={resultado.total_avaliacoes}",
            f"evitadas={resultado.avaliacoes_evitadas}",
            f"tempo={resultado.duracao_segundos:.6f}s",
            f"aprovadas={resultado.total_aprovado}",
        )


if __name__ == "__main__":
    main()
