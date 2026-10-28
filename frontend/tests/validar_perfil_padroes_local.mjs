// Valida no Chrome o perfil real servido pelo Flask e PostgreSQL local.

import { chromium } from "@playwright/test";


const browser = await chromium.launch({ channel: "chrome", headless: true });
try {
  const page = await browser.newPage({ viewport: { width: 1280, height: 800 } });
  await page.goto("http://127.0.0.1:5050/padroes.html");
  await page.locator("#corpo-tabela-padroes tr").nth(8).waitFor();
  await page.locator("#perfil-padroes summary").click();
  await page.locator("#corpo-tabela-perfil tr").nth(3).waitFor();

  const linhas = await page.locator("#corpo-tabela-perfil tr").count();
  if (linhas !== 4) throw new Error(`Esperadas quatro classes; recebidas ${linhas}.`);
  const resumo = await page.locator("#resumo-perfil").textContent();
  if (resumo !== "3.069 resultados") throw new Error(`Resumo inesperado: ${resumo}`);
  const indicados = await page.locator("#perfil-indicadores").textContent();
  if (!indicados.includes("PD_002, PD_003")) {
    throw new Error(`Padrões indicados inesperados: ${indicados}`);
  }
  const raros = await page.locator('#corpo-tabela-perfil tr[data-raro="true"]').count();
  if (raros !== 2) throw new Error(`Esperados dois padrões indicados; recebidos ${raros}.`);
  const mensagem = await page.locator("#mensagem-perfil").textContent();
  if (!mensagem.includes("screener inativo")) throw new Error(`Mensagem inesperada: ${mensagem}`);

  const disposicao = await page.evaluate(() => ({
    posicao: getComputedStyle(document.querySelector(".perfil-padroes__painel")).position,
    gradeAltura: document.querySelector(".padroes-grade").clientHeight,
    painelTemRolagem: document.querySelector(".perfil-padroes__grade").scrollWidth
      >= document.querySelector(".perfil-padroes__grade").clientWidth,
  }));
  if (disposicao.posicao !== "absolute" || disposicao.gradeAltura < 200) {
    throw new Error(`Disposição compacta inválida: ${JSON.stringify(disposicao)}`);
  }

  await page.locator("#perfil-tipo-corte").selectOption("numero");
  await page.locator("#perfil-numero").fill("100");
  await page.locator("#form-perfil button").click();
  await page.locator("#resumo-perfil").filter({ hasText: "100 resultados" }).waitFor();

  console.log(JSON.stringify({
    linhas, resumo, raros, corte: "100 resultados", disposicao,
  }));
} finally {
  await browser.close();
}
