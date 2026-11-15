const CHAVE_CONFIGURACAO = "msen.configuracaoVisual.v3";
const CHAVE_CONFIGURACAO_V2 = "msen.configuracaoVisual.v2";
const CHAVE_CONFIGURACAO_V1 = "msen.configuracaoVisual.v1";

export const CONFIGURACAO_VISUAL_PADRAO = Object.freeze({
  corLinha: "#25834f",
  corPoligono1: "#17663b",
  corVertices: "#e8fff0",
  corResultado: "#80d8a0",
  corMedia: "#ff9f43",
  corCentroGravidade: "#7566d9",
  corRegioes: "#6fcf97",
  corMediaEspacial: "#8b4513",
  corCg1: "#7566d9",
  corCg2: "#2471a3",
  corReferenciasMancha: "#f1c40f",
  espessuraLinhas: 1,
  diametroVertices: 2,
  opacidadeRegioes: 0.12,
  diametroPontosMancha: 3,
  fatorIntensidadeMancha: 0.12,
  mostrarLinha: true,
  mostrarPoligono1: true,
  mostrarVertices: true,
  mostrarResultado: true,
  mostrarMedia: true,
  mostrarCentroGravidade: true,
  mostrarRegioes: true,
});

const campos = {
  corLinha: "cor-linha",
  corPoligono1: "cor-poligono-1",
  corVertices: "cor-vertices",
  corResultado: "cor-resultado",
  corMedia: "cor-media",
  corCentroGravidade: "cor-centro-gravidade",
  corRegioes: "cor-regioes",
  corMediaEspacial: "cor-media-espacial",
  corCg1: "cor-cg1",
  corCg2: "cor-cg2",
  corReferenciasMancha: "cor-referencias-mancha",
  espessuraLinhas: "espessura-linhas",
  diametroVertices: "diametro-vertices",
  opacidadeRegioes: "opacidade-regioes",
  diametroPontosMancha: "diametro-pontos-mancha",
  fatorIntensidadeMancha: "fator-intensidade-mancha",
  mostrarLinha: "mostrar-linha",
  mostrarPoligono1: "mostrar-poligono-1",
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
  diametroPontosMancha: [0.1, 10],
  fatorIntensidadeMancha: [0, 0.5],
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
    const armazenamento = armazenamentoDisponivel();
    const texto = armazenamento?.getItem(CHAVE_CONFIGURACAO);
    if (texto) return validar(JSON.parse(texto));
    const versao2 = armazenamento?.getItem(CHAVE_CONFIGURACAO_V2);
    if (versao2) return validar(JSON.parse(versao2));
    const versao1 = armazenamento?.getItem(CHAVE_CONFIGURACAO_V1);
    if (!versao1) return validar({});
    const antiga = JSON.parse(versao1);
    return validar({
      ...antiga,
      corPoligono1: antiga.corFechamento,
      mostrarPoligono1: antiga.mostrarFechamento,
    });
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
  elemento.style.setProperty("--cor-poligono-1", validada.corPoligono1);
  elemento.style.setProperty("--cor-vertices-geometricos", validada.corVertices);
  elemento.style.setProperty("--cor-resultado", validada.corResultado);
  elemento.style.setProperty("--cor-media", validada.corMedia);
  elemento.style.setProperty("--cor-centro-gravidade", validada.corCentroGravidade);
  elemento.style.setProperty("--cor-regioes", validada.corRegioes);
  elemento.style.setProperty("--cor-media-espacial", validada.corMediaEspacial);
  elemento.style.setProperty("--cor-cg1", validada.corCg1);
  elemento.style.setProperty("--cor-cg2", validada.corCg2);
  elemento.style.setProperty("--cor-referencias-mancha", validada.corReferenciasMancha);
  elemento.style.setProperty("--espessura-linhas", `${validada.espessuraLinhas}mm`);
  elemento.style.setProperty("--opacidade-regioes", String(validada.opacidadeRegioes));
  elemento.style.setProperty("--diametro-pontos-mancha", `${validada.diametroPontosMancha}mm`);
  elemento.style.setProperty("--fator-intensidade-mancha", String(validada.fatorIntensidadeMancha));
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
