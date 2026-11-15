const SVG_NS = "http://www.w3.org/2000/svg";
const PIXELS_POR_MILIMETRO = 96 / 25.4;

function numeroFinito(valor, nome) {
  const numero = Number(valor);
  if (!Number.isFinite(numero)) throw new TypeError(`${nome} deve ser um número finito.`);
  return numero;
}

export function plotarCirculo({
  destino,
  coordenada,
  converterCoordenada,
  diametroMm,
  cor,
  intensidade,
  classe = "",
}) {
  if (!destino?.append) throw new TypeError("O destino da plotagem deve aceitar círculos SVG.");
  if (typeof converterCoordenada !== "function") {
    throw new TypeError("A conversão da coordenada lógica para pixels é obrigatória.");
  }
  const logica = {
    x: numeroFinito(coordenada?.x, "coordenada.x"),
    y: numeroFinito(coordenada?.y, "coordenada.y"),
  };
  const diametro = numeroFinito(diametroMm, "diametroMm");
  if (diametro <= 0) throw new RangeError("O diâmetro deve ser maior que zero.");
  const opacidade = numeroFinito(intensidade, "intensidade");
  if (opacidade < 0 || opacidade > 1) {
    throw new RangeError("A intensidade deve estar entre 0 e 1.");
  }
  if (typeof cor !== "string" || !cor.trim()) throw new TypeError("A cor do círculo é obrigatória.");

  const convertida = converterCoordenada(logica);
  const pixel = {
    x: numeroFinito(convertida?.x, "pixel.x"),
    y: numeroFinito(convertida?.y, "pixel.y"),
  };
  const circulo = document.createElementNS(SVG_NS, "circle");
  circulo.setAttribute("cx", String(pixel.x));
  circulo.setAttribute("cy", String(pixel.y));
  circulo.setAttribute("r", String(diametro * PIXELS_POR_MILIMETRO / 2));
  circulo.setAttribute("fill", cor);
  circulo.setAttribute("fill-opacity", String(opacidade));
  if (classe) circulo.setAttribute("class", classe);
  destino.append(circulo);
  return circulo;
}

