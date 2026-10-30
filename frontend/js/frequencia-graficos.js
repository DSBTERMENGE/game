export const MEDICOES_FREQUENCIA = Object.freeze([
  { campo: "quantidade_ocorrencias", titulo: "Número de ocorrências", unidade: "ocorrências", casas: 0 },
  { campo: "intervalo_minimo", titulo: "Intervalo mínimo", unidade: "concursos", casas: 0 },
  { campo: "intervalo_maximo", titulo: "Intervalo máximo", unidade: "concursos", casas: 0 },
  { campo: "media_intervalos", titulo: "Média dos intervalos", unidade: "concursos", casas: 2 },
  { campo: "mediana_intervalos", titulo: "Mediana dos intervalos", unidade: "concursos", casas: 2 },
  { campo: "desvio_padrao_intervalos", titulo: "Desvio-padrão dos intervalos", unidade: "concursos", casas: 2 },
]);

export function prepararBarrasFrequencia(dezenas, campo) {
  const valores = dezenas.map((item) => {
    const bruto = item[campo];
    if (bruto === null || bruto === undefined || bruto === "") return null;
    const numero = Number(bruto);
    return Number.isFinite(numero) ? numero : null;
  });
  const maximo = Math.max(0, ...valores.filter((valor) => valor !== null));
  return dezenas.map((item, indice) => ({
    dezena: item.dezena,
    quantidadeIntervalos: item.quantidade_intervalos,
    valor: valores[indice],
    proporcao: valores[indice] === null || maximo === 0 ? 0 : valores[indice] / maximo,
  }));
}

export function formatarMedicaoFrequencia(valor, casas) {
  if (valor === null) return "Sem intervalo suficiente";
  return valor.toLocaleString("pt-BR", {
    minimumFractionDigits: casas, maximumFractionDigits: casas,
  });
}
