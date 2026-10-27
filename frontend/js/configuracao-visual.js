const CHAVE_CONFIGURACAO = "msen.configuracaoVisual.v1";

export const CONFIGURACAO_VISUAL_PADRAO = Object.freeze({
  corLinha: "#25834f",
  corFechamento: "#17663b",
  corVertices: "#e8fff0",
  corResultado: "#80d8a0",
  corMedia: "#ff9f43",
  corCentroGravidade: "#7566d9",
  corRegioes: "#6fcf97",
  espessuraLinhas: 1,
  diametroVertices: 2,
  opacidadeRegioes: 0.12,
  mostrarLinha: true,
  mostrarFechamento: true,
  mostrarVertices: true,
  mostrarResultado: true,
  mostrarMedia: true,
  mostrarCentroGravidade: true,
  mostrarRegioes: true,
});

const campos = {
  corLinha: "cor-linha",
  corFechamento: "cor-fechamento",
  corVertices: "cor-vertices",
  corResultado: "cor-resultado",
  corMedia: "cor-media",
  corCentroGravidade: "cor-centro-gravidade",
  corRegioes: "cor-regioes",
  espessuraLinhas: "espessura-linhas",
  diametroVertices: "diametro-vertices",
  opacidadeRegioes: "opacidade-regioes",
  mostrarLinha: "mostrar-linha",
  mostrarFechamento: "mostrar-fechamento",
  mostrarVertices: "mostrar-vertices",
  mostrarResultado: "mostrar-resultado",
  mostrarMedia: "mostrar-media",
  mostrarCentroGravidade: "mostrar-centro-gravidade",
  mostrarRegioes: "mostrar-regioes",
};

const limites = {
  espessuraLinhas: [0.1, 3],
  diametroVertices: [1, 10],
  opacidadeRegioes: [0, 1],
};

function armazenamentoDisponivel() {
  return globalThis.localStorage ?? null;
}

function validar(configuracao = {}) {
  const resultado = { ...CONFIGURACAO_VISUAL_PADRAO };
  Object.keys(resultado).forEach((chave) => {
    const valor = configuracao[chave];
    if (typeof resultado[chave] === "boolean" && typeof valor === "boolean") resultado[chave] = valor;
    else if (typeof resultado[chave] === "string" && /^#[0-9a-f]{6}$/i.test(valor)) resultado[chave] = valor;
    else if (chave in limites && Number.isFinite(Number(valor))) {
      const [minimo, maximo] = limites[chave];
      resultado[chave] = Math.min(maximo, Math.max(minimo, Number(valor)));
    }
  });
  return resultado;
}

export function carregarConfiguracaoVisual() {
  // Usa o padrão quando o navegador não possui preferências válidas.
  try {
    const texto = armazenamentoDisponivel()?.getItem(CHAVE_CONFIGURACAO);
    return validar(texto ? JSON.parse(texto) : {});
  } catch {
    return { ...CONFIGURACAO_VISUAL_PADRAO };
  }
}

export function salvarConfiguracaoVisual(configuracao) {
  // Persiste somente uma cópia validada das preferências visuais.
  const validada = validar(configuracao);
  armazenamentoDisponivel()?.setItem(CHAVE_CONFIGURACAO, JSON.stringify(validada));
  return validada;
}

export function aplicarConfiguracaoVisual(elemento, configuracao) {
  // Aplica cores e medidas como variáveis CSS no elemento do mapa.
  const validada = validar(configuracao);
  elemento.style.setProperty("--cor-linha-geometrica", validada.corLinha);
  elemento.style.setProperty("--cor-fechamento-geometrico", validada.corFechamento);
  elemento.style.setProperty("--cor-vertices-geometricos", validada.corVertices);
  elemento.style.setProperty("--cor-resultado", validada.corResultado);
  elemento.style.setProperty("--cor-media", validada.corMedia);
  elemento.style.setProperty("--cor-centro-gravidade", validada.corCentroGravidade);
  elemento.style.setProperty("--cor-regioes", validada.corRegioes);
  elemento.style.setProperty("--espessura-linhas", `${validada.espessuraLinhas}mm`);
  elemento.style.setProperty("--opacidade-regioes", String(validada.opacidadeRegioes));
  return validada;
}

function preencherFormulario(configuracao) {
  Object.entries(campos).forEach(([chave, id]) => {
    const campo = document.querySelector(`#${id}`);
    if (typeof configuracao[chave] === "boolean") campo.checked = configuracao[chave];
    else campo.value = String(configuracao[chave]);
  });
}

function lerFormulario() {
  return Object.fromEntries(Object.entries(campos).map(([chave, id]) => {
    const campo = document.querySelector(`#${id}`);
    const valor = typeof CONFIGURACAO_VISUAL_PADRAO[chave] === "boolean"
      ? campo.checked
      : campo.value;
    return [chave, valor];
  }));
}

export function vincularPainelConfiguracao(configuracaoInicial, aoSalvar) {
  // Liga o diálogo compacto à persistência e informa cada alteração salva.
  const dialogo = document.querySelector("#dialogo-aparencia");
  const formulario = document.querySelector("#form-aparencia");
  let atual = validar(configuracaoInicial);
  preencherFormulario(atual);

  document.querySelector("#botao-aparencia").addEventListener("click", () => {
    preencherFormulario(atual);
    dialogo.showModal();
  });
  document.querySelector("#botao-fechar-aparencia").addEventListener("click", () => dialogo.close());
  document.querySelector("#botao-restaurar-aparencia").addEventListener("click", () => {
    preencherFormulario(CONFIGURACAO_VISUAL_PADRAO);
  });
  formulario.addEventListener("submit", (evento) => {
    evento.preventDefault();
    atual = salvarConfiguracaoVisual(lerFormulario());
    aoSalvar(atual);
    dialogo.close();
  });
}
