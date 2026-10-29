export const CODIGOS_FAMILIAS = Object.freeze(["ESTATISTICA", "GEOMETRIA", "PADROES"]);

export function validarDetalhesPadroes(detalhes, familia) {
  if (!detalhes || detalhes.operador !== "<" || !Array.isArray(detalhes.grupos)) return false;
  if (detalhes.grupos.length > 3 || !detalhes.fechamento?.valido) return false;
  let saldo = familia.entrada;
  let exclusoes = 0;
  const codigos = new Set();
  for (const grupo of detalhes.grupos) {
    if (grupo.entrada !== saldo || grupo.entrada !== grupo.exclusoes + grupo.saldo) return false;
    if (!grupo.reconciliado || !Array.isArray(grupo.padroes)) return false;
    for (const padrao of grupo.padroes) {
      if (codigos.has(padrao.padrao_cod)) return false;
      codigos.add(padrao.padrao_cod);
      if (padrao.estado !== "APLICADO_RARO") return false;
      if (padrao.correspondencias !== padrao.exclusoes) return false;
    }
    exclusoes += grupo.exclusoes;
    saldo = grupo.saldo;
  }
  return exclusoes === familia.exclusoes
    && saldo === familia.saldo
    && detalhes.fechamento.entrada === familia.entrada
    && detalhes.fechamento.exclusoes === familia.exclusoes
    && detalhes.fechamento.saldo === familia.saldo;
}

export function validarQuadroExtensivel(dados) {
  if (!dados || !dados.escopo || !dados.resumo || !dados.fechamento) return false;
  if (!Array.isArray(dados.familias) || dados.familias.length !== 3) return false;
  if (dados.familias.some((familia, indice) => familia.codigo !== CODIGOS_FAMILIAS[indice])) return false;
  let saldo = dados.resumo.total_analisado;
  for (const familia of dados.familias) {
    if (familia.entrada !== saldo || familia.entrada - familia.exclusoes !== familia.saldo) return false;
    let saldoFiltro = familia.entrada;
    let somaExclusoes = 0;
    for (const filtro of familia.filtros) {
      if (filtro.entrada !== saldoFiltro || filtro.avaliacoes !== saldoFiltro) return false;
      if (filtro.entrada - filtro.exclusoes !== filtro.saldo) return false;
      somaExclusoes += filtro.exclusoes;
      saldoFiltro = filtro.saldo;
    }
    if (saldoFiltro !== familia.saldo || somaExclusoes !== familia.exclusoes) return false;
    saldo = familia.saldo;
  }
  const familiaPadroes = dados.familias[2];
  const configuracao = dados.configuracao_raridade;
  const selecionadosDetalhes = dados.detalhes_padroes?.grupos
    ?.flatMap((grupo) => grupo.padroes.map((padrao) => padrao.padrao_cod)) || [];
  return configuracao?.operador === "<"
    && configuracao.limite_percentual === dados.detalhes_padroes?.limite_percentual
    && JSON.stringify(configuracao.padroes_selecionados) === JSON.stringify(selecionadosDetalhes)
    && validarDetalhesPadroes(dados.detalhes_padroes, familiaPadroes)
    && dados.fechamento.valido === true
    && dados.fechamento.lado_esquerdo === dados.fechamento.lado_direito
    && saldo === dados.resumo.total_aprovado
    && dados.resumo.total_analisado === dados.resumo.total_excluido + dados.resumo.total_aprovado;
}
