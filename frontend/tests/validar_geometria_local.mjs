// Valida no Google Chrome a geometria real sem modificar banco ou preferências.

import { chromium, expect } from "@playwright/test";


const browser = await chromium.launch({ channel: "chrome", headless: true });
try {
  const page = await browser.newPage({ viewport: { width: 1366, height: 900 } });
  await page.goto("http://127.0.0.1:5050/");
  const aguardarGeometria = async () => {
    await expect.poll(
      async () => page.locator("#resumo-geometrico").textContent(),
      { timeout: 60_000 },
    ).toContain("Extensão:");
  };
  await aguardarGeometria();

  const mensagem = await page.locator("#mensagem-sistema").textContent();
  if (mensagem !== "3069 resultados carregados.") {
    throw new Error(`Quantidade inesperada no painel: ${mensagem}`);
  }
  const conferirDesenho = async () => {
    const obtido = {
      linha: await page.locator("polyline.linha-geometrica").count(),
      fechamento: await page.locator("line.fechamento-geometrico").count(),
      vertices: await page.locator("circle.vertice-geometrico").count(),
      regioes: await page.locator("polygon.regiao-geometrica").count(),
      centro: await page.locator("circle.centro-gravidade").count(),
      media: await page.locator("circle.marca-media").count(),
      resumo: await page.locator("#resumo-geometrico").textContent(),
    };
    if (obtido.linha !== 1 || obtido.fechamento !== 1 || obtido.vertices !== 6) {
      throw new Error(`Percurso incompleto: ${JSON.stringify(obtido)}`);
    }
    if (obtido.regioes < 1 || obtido.centro !== 1 || obtido.media !== 1) {
      throw new Error(`Medidas visuais incompletas: ${JSON.stringify(obtido)}`);
    }
    if (!obtido.resumo.includes("Extensão:") || !obtido.resumo.includes("Área:")) {
      throw new Error(`Resumo geométrico ausente: ${obtido.resumo}`);
    }
    return obtido;
  };

  const primeiro = await conferirDesenho();
  await page.locator("#botao-proximo").click();
  await aguardarGeometria();
  const segundo = await conferirDesenho();
  await page.locator("#botao-aparencia").click();
  if (!(await page.locator("#dialogo-aparencia").isVisible())) {
    throw new Error("O diálogo de aparência não abriu.");
  }
  console.log(JSON.stringify({ mensagem, primeiro, segundo, aparencia: "visível" }));
} finally {
  await browser.close();
}
