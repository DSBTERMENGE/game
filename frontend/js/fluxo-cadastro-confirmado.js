const copiar = (valor) => valor == null ? valor : structuredClone(valor);

export function criarFluxoCadastroConfirmado({ validar, gravar }) {
  if (typeof validar !== "function" || typeof gravar !== "function") {
    throw new TypeError("O fluxo confirmado exige validação e gravação explícitas.");
  }

  let estado = "INATIVO";
  let dadosConferidos = null;
  let operacaoAtual = null;

  function preparar(dados) {
    if (estado === "SALVANDO") throw new Error("A gravação já está em andamento.");
    dadosConferidos = copiar(validar(copiar(dados)));
    estado = "CONFERENCIA";
    return copiar(dadosConferidos);
  }

  function cancelar() {
    if (estado === "SALVANDO") return false;
    dadosConferidos = null;
    estado = "INATIVO";
    return true;
  }

  async function confirmar() {
    if (operacaoAtual) return operacaoAtual;
    if (estado !== "CONFERENCIA" || dadosConferidos == null) return null;
    const dados = copiar(dadosConferidos);
    estado = "SALVANDO";
    operacaoAtual = Promise.resolve()
      .then(() => gravar(dados))
      .then((resultado) => {
        estado = "CONCLUIDO";
        dadosConferidos = null;
        return resultado;
      })
      .catch((erro) => {
        estado = "CONFERENCIA";
        throw erro;
      })
      .finally(() => { operacaoAtual = null; });
    return operacaoAtual;
  }

  return {
    preparar,
    cancelar,
    confirmar,
    obterEstado: () => ({ estado, possuiDadosConferidos: dadosConferidos != null }),
  };
}
