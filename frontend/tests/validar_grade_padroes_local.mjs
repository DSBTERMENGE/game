// Valida em Chrome a grade local de padrões sem modificar dados.

import { chromium } from "@playwright/test";


const browser = await chromium.launch({ channel: "chrome", headless: true });
try {
  const page = await browser.newPage({ viewport: { width: 1280, height: 900 } });
  await page.goto("http://127.0.0.1:5050/padroes.html");
  await page.locator("#corpo-tabela-padroes tr").nth(5).waitFor();

  const linhas = await page.locator("#corpo-tabela-padroes tr").count();
  if (linhas !== 6) throw new Error(`Esperadas 6 linhas; recebidas ${linhas}.`);

  const esperado = new Map([
    ["PD_004", ["1037", "2,960425", "2,387099"]],
    ["PD_005", ["66", "45,969231", "42,006948"]],
    ["PD_006", ["4", "696,666667", "373,443734"]],
  ]);
  const conferidos = {};
  for (const [codigo, estatisticas] of esperado) {
    const linha = page.locator(`tr[data-codigo="${codigo}"]`);
    const celulas = await linha.locator("td").allTextContents();
    const nome = await linha.locator("input").inputValue();
    if (!nome.includes("linhas subjacentes")) {
      throw new Error(`${codigo} não exibe o nome corrigido.`);
    }
    if (celulas[7] !== "Implementada") {
      throw new Error(`${codigo} não aparece como implementada.`);
    }
    if (JSON.stringify(celulas.slice(4, 7)) !== JSON.stringify(estatisticas)) {
      throw new Error(`${codigo} exibe estatísticas inesperadas: ${celulas.slice(4, 7)}`);
    }
    conferidos[codigo] = { nome, estatisticas, estado: celulas[7] };
  }
  console.log(JSON.stringify({ linhas, conferidos }));
} finally {
  await browser.close();
}
