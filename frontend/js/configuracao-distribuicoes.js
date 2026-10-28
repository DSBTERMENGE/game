export const CHAVE_CONFIGURACAO_DISTRIBUICOES = "msen.configuracao-distribuicoes.v1";

export const CONFIGURACAO_DISTRIBUICOES_PADRAO = Object.freeze({
  metodo_faixa: "desvio_padrao",
  margem_inferior: "1",
  margem_superior: "1",
});

const METODOS = new Set(["desvio_padrao", "percentual_media"]);

function margemValida(valor) {
  const numero = Number(valor);
  return Number.isFinite(numero) && numero >= 0;
}

export function normalizarConfiguracaoDistribuicoes(valor) {
  if (!valor || typeof valor !== "object") return { ...CONFIGURACAO_DISTRIBUICOES_PADRAO };
  const metodo = METODOS.has(valor.metodo_faixa)
    ? valor.metodo_faixa
    : CONFIGURACAO_DISTRIBUICOES_PADRAO.metodo_faixa;
  const inferior = margemValida(valor.margem_inferior)
    ? String(valor.margem_inferior)
    : CONFIGURACAO_DISTRIBUICOES_PADRAO.margem_inferior;
  const superior = margemValida(valor.margem_superior)
    ? String(valor.margem_superior)
    : CONFIGURACAO_DISTRIBUICOES_PADRAO.margem_superior;
  return { metodo_faixa: metodo, margem_inferior: inferior, margem_superior: superior };
}

export function carregarConfiguracaoDistribuicoes(armazenamento = localStorage) {
  try {
    const bruto = armazenamento.getItem(CHAVE_CONFIGURACAO_DISTRIBUICOES);
    return normalizarConfiguracaoDistribuicoes(bruto ? JSON.parse(bruto) : null);
  } catch (_erro) {
    return { ...CONFIGURACAO_DISTRIBUICOES_PADRAO };
  }
}

export function salvarConfiguracaoDistribuicoes(configuracao, armazenamento = localStorage) {
  const normalizada = normalizarConfiguracaoDistribuicoes(configuracao);
  armazenamento.setItem(CHAVE_CONFIGURACAO_DISTRIBUICOES, JSON.stringify(normalizada));
  return normalizada;
}

export function criarConsultaDistribuicoes(configuracao) {
  const normalizada = normalizarConfiguracaoDistribuicoes(configuracao);
  return new URLSearchParams(normalizada).toString();
}
