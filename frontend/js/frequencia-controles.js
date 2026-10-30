export const MENSAGEM_CONFIRMACAO_FREQUENCIA =
  "O tick para salvar está ativo. Você realmente deseja salvar os dados?";

export function criarEstadoInicialFrequencia() {
  return { salvarDados: true, executando: false };
}

export function descreverPreviaFrequencia(previa) {
  if (previa.modo === "INCREMENTAL") {
    return `Serão acrescentados os concursos: ${previa.concursos_novos.join(", ")}.`;
  }
  if (previa.modo === "RECONSTRUCAO_CONFIGURACAO") {
    const campos = previa.divergencias_configuracao
      .map((item) => `${item.campo}: ${item.valor_gravado} → ${item.valor_calculado}`)
      .join("; ");
    return `A geração será reconstruída e substituída. ${campos}`;
  }
  if (previa.modo === "RECONSTRUCAO_ORIGEM") {
    return "Os resultados de origem mudaram. A geração será reconstruída e substituída.";
  }
  if (previa.modo === "PRIMEIRA_CARGA") return "Será criada a primeira geração histórica.";
  return "Não existem concursos novos para processar.";
}

export function criarControleFrequencia({ confirmar, salvar, simular }) {
  if (![confirmar, salvar, simular].every((item) => typeof item === "function")) {
    throw new TypeError("O controle exige confirmar, salvar e simular.");
  }
  let executando = false;
  return {
    estaExecutando: () => executando,
    async executar({ previa, salvarDados = true }) {
      if (executando) return null;
      executando = true;
      try {
        if (!salvarDados) return await simular();
        const aceito = await confirmar(
          MENSAGEM_CONFIRMACAO_FREQUENCIA,
          descreverPreviaFrequencia(previa),
        );
        if (!aceito) return null;
        return await salvar({ confirmacao_gravacao: true });
      } finally {
        executando = false;
      }
    },
  };
}
