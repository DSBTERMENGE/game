export const PROTOTIPO_SCREENER = Object.freeze({
  total_inicial: 50063860,
  niveis: [
    {
      codigo: "estatistica",
      titulo: "1 — Valores estatísticos",
      entrada: 50063860,
      exclusoes: 12515965,
      saldo: 37547895,
      filtros: [
        { nome: "Soma / média", exclusoes: 6007663, regra: "Uma única informação; média = soma ÷ 6" },
        { nome: "Desvio-padrão", exclusoes: 4505747, regra: "Fora da faixa histórica configurada" },
        { nome: "Mediana", exclusoes: 2002555, regra: "Fora da faixa histórica configurada" },
      ],
    },
    {
      codigo: "geometria",
      titulo: "2 — Análise geométrica",
      entrada: 37547895,
      exclusoes: 9386974,
      saldo: 28160921,
      filtros: [
        { nome: "Extensão aberta", exclusoes: 3754790, regra: "Fora da faixa aceita" },
        { nome: "Perímetro fechado", exclusoes: 2628353, regra: "Fora da faixa aceita" },
        { nome: "Área total", exclusoes: 1877395, regra: "Fora da faixa aceita" },
        { nome: "Quantidade de regiões", exclusoes: 750958, regra: "Fora da faixa aceita" },
        { nome: "Centro de gravidade", exclusoes: 375478, regra: "X ou Y fora da faixa aceita" },
      ],
    },
    {
      codigo: "padroes",
      titulo: "3 — Padrões históricos",
      entrada: 28160921,
      exclusoes: 2816092,
      saldo: 25344829,
      limite_raridade: "10%",
      filtros: [
        { nome: "PG_001 · PD_003", exclusoes: 1126437, regra: "Frequência histórica 0,16% · excluir" },
        { nome: "PG_002 · PD_006", exclusoes: 844828, regra: "Frequência histórica 2,40% · excluir" },
        { nome: "PG_003 · PD_009", exclusoes: 563218, regra: "Frequência histórica 6,75% · excluir" },
        { nome: "PG_004 · PD_012", exclusoes: 281609, regra: "Frequência histórica 8,90% · excluir" },
      ],
      selecionados: ["PD_003", "PD_006", "PD_009", "PD_012"],
    },
  ],
  total_aprovado: 25344829,
});

export function validarFechamentoPrototipo(dados = PROTOTIPO_SCREENER) {
  let saldo = dados.total_inicial;
  for (const nivel of dados.niveis) {
    const somaFiltros = nivel.filtros.reduce((total, filtro) => total + filtro.exclusoes, 0);
    if (nivel.entrada !== saldo || somaFiltros !== nivel.exclusoes) return false;
    if (nivel.entrada - nivel.exclusoes !== nivel.saldo) return false;
    saldo = nivel.saldo;
  }
  return saldo === dados.total_aprovado;
}
