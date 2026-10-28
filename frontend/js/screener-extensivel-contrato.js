export const CODIGOS_FAMILIAS = Object.freeze(["ESTATISTICA", "GEOMETRIA", "PADROES"]);

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
  return dados.fechamento.valido === true
    && dados.fechamento.lado_esquerdo === dados.fechamento.lado_direito
    && saldo === dados.resumo.total_aprovado
    && dados.resumo.total_analisado === dados.resumo.total_excluido + dados.resumo.total_aprovado;
}
