export function montarConfiguracao(valores) {
  const modo = String(valores.modo_quantidade || "").toUpperCase();
  const quantidade = modo === "FIXA" ? Number(valores.quantidade_dezenas) : null;
  const configuracao = {
    nome: String(valores.nome || "").trim(),
    fator_k: Number(valores.fator_k),
    fator_j: Number(valores.fator_j),
    modo_quantidade: modo,
    quantidade_dezenas: quantidade,
    versao_calculo: Number(valores.versao_calculo),
  };
  if (!configuracao.nome) throw new Error("Informe o nome da configuração.");
  if (!(configuracao.fator_k > 0 && configuracao.fator_k <= 1)) throw new Error("O fator k deve estar entre zero e um.");
  if (configuracao.fator_j < -configuracao.fator_k || configuracao.fator_j > configuracao.fator_k) throw new Error("O fator j deve permanecer entre -k e +k.");
  if (!["MAX", "FIXA"].includes(modo)) throw new Error("Escolha o modo de quantidade.");
  if (modo === "FIXA" && (!Number.isInteger(quantidade) || quantidade < 6 || quantidade > 60)) throw new Error("A quantidade fixa deve ficar entre 6 e 60.");
  if (!Number.isInteger(configuracao.versao_calculo) || configuracao.versao_calculo < 1) throw new Error("A versão deve ser positiva.");
  return configuracao;
}

export function idsComparacao(texto) {
  const ids = String(texto).split(",").map((item) => Number(item.trim())).filter((item) => Number.isInteger(item) && item > 0);
  if (ids.length < 2 || new Set(ids).size !== ids.length) throw new Error("Informe ao menos dois IDs distintos.");
  return ids;
}

export function formatarDezenas(dezenas = []) {
  return dezenas.map((dezena) => String(dezena).padStart(2, "0")).join(" · ");
}
