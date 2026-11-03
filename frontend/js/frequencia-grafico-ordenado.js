const SVG_NS = "http://www.w3.org/2000/svg";

function svgElemento(nome, atributos = {}) {
  const elemento = document.createElementNS(SVG_NS, nome);
  for (const [chave, valor] of Object.entries(atributos)) {
    elemento.setAttribute(chave, String(valor));
  }
  return elemento;
}

function caminho(pontos) {
  return pontos.map((ponto, indice) => (
    `${indice === 0 ? "M" : "L"}${ponto.x.toFixed(2)},${ponto.y.toFixed(2)}`
  )).join(" ");
}

export function geometriaOcorrenciasOrdenadas(dados, largura = 1440, altura = 650) {
  if (!dados || dados.total <= 0 || dados.ordenados.length === 0) return null;
  const esquerda = 88, direita = largura - 28, topo = 36, inferior = altura - 72;
  const escalaX = (valor) => esquerda + valor * (direita - esquerda) / 100;
  const escalaY = (valor) => inferior - valor * (inferior - topo) / 100;
  const grade = Array.from({ length: 21 }, (_, indice) => indice * 5);
  const pontos = dados.ordenados.map((item) => ({
    ...item,
    x: escalaX(item.percentualOcorrencias),
    y: escalaY(item.percentualMaiorIntervalo),
  }));
  return {
    largura, altura, esquerda, direita, topo, inferior, grade, pontos,
    caminho: caminho(pontos),
  };
}

function percentual(valor) {
  return `${Number(valor).toLocaleString("pt-BR", { maximumFractionDigits: 2 })}%`;
}

export function renderizarOcorrenciasOrdenadas(svg, detalhe, dados) {
  svg.replaceChildren();
  const geometria = geometriaOcorrenciasOrdenadas(dados);
  if (!geometria) {
    detalhe.textContent = "Não existem intervalos concluídos para ordenar.";
    return { pontos: 0 };
  }
  svg.setAttribute("viewBox", `0 0 ${geometria.largura} ${geometria.altura}`);
  svg.setAttribute("role", "img");
  svg.setAttribute("aria-label", "Ocorrências ordenadas pelo tamanho dos intervalos");

  for (const valor of geometria.grade) {
    const x = geometria.esquerda + valor * (geometria.direita - geometria.esquerda) / 100;
    const y = geometria.inferior - valor * (geometria.inferior - geometria.topo) / 100;
    svg.append(
      svgElemento("line", {
        x1: x, x2: x, y1: geometria.topo, y2: geometria.inferior,
        class: "ordenado-grade",
      }),
      svgElemento("line", {
        x1: geometria.esquerda, x2: geometria.direita, y1: y, y2: y,
        class: "ordenado-grade",
      }),
    );
    const rotuloX = svgElemento("text", {
      x, y: geometria.inferior + 25,
      class: "ordenado-rotulo", "text-anchor": "middle",
    });
    rotuloX.textContent = `${valor}%`; svg.append(rotuloX);
    const rotuloY = svgElemento("text", {
      x: geometria.esquerda - 12, y: y + 4,
      class: "ordenado-rotulo", "text-anchor": "end",
    });
    rotuloY.textContent = `${valor}%`; svg.append(rotuloY);
  }
  svg.append(
    svgElemento("line", { x1: geometria.esquerda, x2: geometria.esquerda, y1: geometria.topo, y2: geometria.inferior, class: "ordenado-eixo" }),
    svgElemento("line", { x1: geometria.esquerda, x2: geometria.direita, y1: geometria.inferior, y2: geometria.inferior, class: "ordenado-eixo" }),
  );
  const tituloX = svgElemento("text", {
    x: (geometria.esquerda + geometria.direita) / 2,
    y: geometria.altura - 18, class: "ordenado-titulo-eixo", "text-anchor": "middle",
  });
  tituloX.textContent = "Ocorrências ordenadas do menor para o maior (%)"; svg.append(tituloX);
  const tituloY = svgElemento("text", {
    x: 20, y: (geometria.topo + geometria.inferior) / 2,
    class: "ordenado-titulo-eixo", "text-anchor": "middle",
    transform: `rotate(-90 20 ${(geometria.topo + geometria.inferior) / 2})`,
  });
  tituloY.textContent = "Duração do intervalo (% do maior)"; svg.append(tituloY);
  svg.append(svgElemento("path", {
    d: geometria.caminho, class: "ordenado-curva",
  }));
  for (const item of geometria.pontos) {
    const descricao = `Ocorrência ${item.ordem} de ${dados.total} · ${percentual(item.percentualOcorrencias)} acumulado · intervalo ${item.intervalo} · ${percentual(item.percentualMaiorIntervalo)} do maior`;
    const ponto = svgElemento("circle", {
      cx: item.x, cy: item.y, r: 3.5, class: "ordenado-ponto",
      tabindex: 0, role: "button", "aria-label": descricao,
    });
    const title = svgElemento("title"); title.textContent = descricao; ponto.append(title);
    const mostrar = () => { detalhe.textContent = descricao; };
    ponto.addEventListener("mouseenter", mostrar);
    ponto.addEventListener("focus", mostrar);
    ponto.addEventListener("click", mostrar);
    svg.append(ponto);
  }
  detalhe.textContent = `Foram ordenadas ${dados.total.toLocaleString("pt-BR")} ocorrências. Selecione um ponto para consultar os valores exatos.`;
  return { pontos: geometria.pontos.length };
}
