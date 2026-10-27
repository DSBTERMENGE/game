"""Importação incremental e atômica do Excel para PostgreSQL."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

import psycopg

from msen.calculos import ResultadoCalculado, calcular_frequencias
from msen.database import RepositorioFrequencias, RepositorioResultados
from msen.importacao import StatusImportacao, comparar_importacao_excel
from msen.modelos import ResultadoEntrada

from .padroes import recalcular_padroes_iniciais
from .analise_geometrica import recalcular_analises_geometricas


@dataclass(frozen=True, slots=True)
class RelatorioImportacaoBanco:
    arquivo: str
    sha256: str
    iniciada_em: str
    concluida_em: str
    registros_antes: int
    registros_depois: int
    linhas_analisadas: int
    novas: int
    inseridas: int
    iguais: int
    alteradas: int
    invalidas: int
    concursos_inseridos: tuple[int, ...]
    concursos_alterados: tuple[int, ...]
    linhas_invalidas: tuple[int, ...]


def _como_entrada(resultado: ResultadoCalculado) -> ResultadoEntrada:
    return ResultadoEntrada(
        data_resultado=resultado.data_resultado,
        numero_ap=resultado.numero_ap,
        res_01=resultado.res_01, res_02=resultado.res_02, res_03=resultado.res_03,
        res_04=resultado.res_04, res_05=resultado.res_05, res_06=resultado.res_06,
    )


def importar_planilha_no_banco(
    conexao: psycopg.Connection, caminho: str | Path
) -> RelatorioImportacaoBanco:
    """Insere apenas novidades e recalcula frequências na mesma transação."""

    origem = Path(caminho)
    inicio = datetime.now(timezone.utc)
    checksum = hashlib.sha256(origem.read_bytes()).hexdigest()
    repositorio = RepositorioResultados(conexao)
    existentes = repositorio.listar(limite=10_000)
    antes = repositorio.contar()
    comparacao = comparar_importacao_excel(
        origem, (item.resultado for item in existentes)
    )
    novas = comparacao.com_status(StatusImportacao.NOVA)
    iguais = comparacao.com_status(StatusImportacao.IGUAL)
    alteradas = comparacao.com_status(StatusImportacao.ALTERADA)
    invalidas = comparacao.com_status(StatusImportacao.INVALIDA)

    with conexao.transaction():
        for linha in novas:
            assert linha.importado is not None
            repositorio.inserir(linha.importado)

        todos = repositorio.listar(limite=10_000)
        frequencias = calcular_frequencias(_como_entrada(item.resultado) for item in todos)
        RepositorioFrequencias(conexao).atualizar_todas(frequencias)
        recalcular_padroes_iniciais(conexao)
        recalcular_analises_geometricas(conexao)

    depois = repositorio.contar()
    fim = datetime.now(timezone.utc)
    return RelatorioImportacaoBanco(
        arquivo=origem.name,
        sha256=checksum,
        iniciada_em=inicio.isoformat(),
        concluida_em=fim.isoformat(),
        registros_antes=antes,
        registros_depois=depois,
        linhas_analisadas=len(comparacao.linhas),
        novas=len(novas), inseridas=len(novas), iguais=len(iguais),
        alteradas=len(alteradas), invalidas=len(invalidas),
        concursos_inseridos=tuple(int(linha.numero_ap) for linha in novas),
        concursos_alterados=tuple(int(linha.numero_ap) for linha in alteradas),
        linhas_invalidas=tuple(linha.numero_linha for linha in invalidas),
    )


def salvar_relatorio_importacao(
    relatorio: RelatorioImportacaoBanco, caminho: str | Path
) -> Path:
    """Preserva relatório sem parâmetros de conexão ou credenciais."""

    if not isinstance(relatorio, RelatorioImportacaoBanco):
        raise TypeError("É necessário fornecer um RelatorioImportacaoBanco.")
    destino = Path(caminho)
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(
        json.dumps(asdict(relatorio), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return destino
