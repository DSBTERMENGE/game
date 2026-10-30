import { criarModalAndamento } from "./modal-andamento.js";

async function respostaJson(resposta) {
  const dados = await resposta.json();
  if (!resposta.ok) throw new Error(dados.erro?.mensagem || `Falha HTTP ${resposta.status}.`);
  return dados;
}

export function formatarDezenas(dezenas) { return dezenas.map((numero) => String(numero).padStart(2, "0")).join(" · "); }
export function formatarResultado(item) {
  if (!item?.estado) return "Pendente";
  if (item.estado === "SEM_VALOR" || item.estado === "SEM_CORRESPONDENCIA") return "Sem correspondência";
  if (item.subgrupo_codigo) return `${item.subgrupo_codigo} — ${item.subgrupo_nome}`;
  return item.valor ?? "Pendente";
}

export function diagnosticoFinalValidacao(resultado) {
  const total = Number(resultado?.avaliacoes || 0);
  const aprovadas = Number(resultado?.aprovadas || 0);
  const reprovadas = Number(resultado?.reprovadas || 0);
  const pendentes = Number(resultado?.pendentes || 0);
  const contagem = `Total: ${total.toLocaleString("pt-BR")}; ${aprovadas.toLocaleString("pt-BR")} aprovadas; ${reprovadas.toLocaleString("pt-BR")} reprovadas; ${pendentes.toLocaleString("pt-BR")} pendentes.`;
  const aprovado = Boolean(resultado?.homologacao_concluida) && reprovadas === 0 && pendentes === 0;
  return aprovado
    ? { aprovado, mensagem: `Validação e auditoria concluída e aprovada. ${contagem}` }
    : { aprovado, mensagem: `Processamento concluído, mas a Validação e auditoria não foi aprovada. ${contagem} Use o filtro Situação para localizar as ocorrências.` };
}

const e = {
  estado: document.querySelector("#estado-algoritmo"), motivo: document.querySelector("#estado-motivo"),
  atualizar: document.querySelector("#botao-atualizar-validacao"), total: document.querySelector("#resumo-total"),
  aprovadas: document.querySelector("#resumo-aprovadas"), reprovadas: document.querySelector("#resumo-reprovadas"),
  pendentes: document.querySelector("#resumo-pendentes"), formulario: document.querySelector("#filtros-auditoria"),
  categoria: document.querySelector("#filtro-categoria"), criterio: document.querySelector("#filtro-criterio"),
  grupo: document.querySelector("#filtro-grupo"), subgrupo: document.querySelector("#filtro-subgrupo"),
  situacao: document.querySelector("#filtro-situacao"), limpar: document.querySelector("#botao-limpar-filtros"),
  corpo: document.querySelector("#corpo-avaliacoes"), vazia: document.querySelector("#auditoria-vazia"),
  consulta: document.querySelector("#estado-consulta"), pagina: document.querySelector("#pagina-atual"),
  anterior: document.querySelector("#pagina-anterior"), seguinte: document.querySelector("#pagina-seguinte"),
  relatorioFechamento: document.querySelector("#relatorio-fechamento"),
  relatorioSincronizacao: document.querySelector("#relatorio-sincronizacao"),
  corpoRelatorio: document.querySelector("#corpo-relatorio-criterios"),
  semDivergencias: document.querySelector("#relatorio-sem-divergencias"),
  listaDivergencias: document.querySelector("#lista-divergencias"),
};
let pagina = 1, totalPaginas = 1, filtrosCarregados = false;

function opcao(valor, texto) { const item = document.createElement("option"); item.value = valor; item.textContent = texto; return item; }
function preencherFiltros(filtros) {
  if (filtrosCarregados) return;
  filtros.criterios.forEach((item) => e.criterio.append(opcao(item.codigo, `${item.codigo} — ${item.nome}`)));
  filtros.grupos.forEach((item) => e.grupo.append(opcao(item.codigo, `${item.codigo} — ${item.nome}`)));
  filtros.subgrupos.forEach((item) => e.subgrupo.append(opcao(item.codigo, `${item.codigo} — ${item.nome}`)));
  filtrosCarregados = true;
}
function parametros() {
  const dados = new URLSearchParams({ pagina: String(pagina), limite: "50" });
  for (const campo of ["categoria", "criterio", "grupo", "subgrupo", "situacao"]) { const valor = e[campo].value; if (valor) dados.set(campo, valor); }
  return dados;
}
function celula(texto, classe = "") { const td = document.createElement("td"); td.textContent = texto ?? "—"; if (classe) td.className = classe; return td; }

function renderizar(dados) {
  const resumo = dados.resumo;
  const validacaoAprovada = resumo.total > 0 && resumo.reprovadas === 0 && resumo.pendentes === 0;
  e.estado.textContent = validacaoAprovada
    ? "Validação e auditoria aprovada"
    : "Validação e auditoria requer atualização";
  e.estado.className = `auditoria-estado auditoria-estado--${validacaoAprovada ? "atualizado" : "desatualizado"}`;
  e.motivo.textContent = validacaoAprovada
    ? `${resumo.aprovadas.toLocaleString("pt-BR")} avaliações aprovadas; nenhuma reprovação ou pendência.`
    : `${resumo.reprovadas.toLocaleString("pt-BR")} reprovadas e ${resumo.pendentes.toLocaleString("pt-BR")} pendentes. Use o filtro Situação para localizar as ocorrências.`;
  e.atualizar.hidden = false;
  e.total.textContent = dados.resumo.total.toLocaleString("pt-BR"); e.aprovadas.textContent = dados.resumo.aprovadas.toLocaleString("pt-BR");
  e.reprovadas.textContent = dados.resumo.reprovadas.toLocaleString("pt-BR"); e.pendentes.textContent = dados.resumo.pendentes.toLocaleString("pt-BR");
  preencherFiltros(dados.filtros); e.corpo.replaceChildren();
  for (const item of dados.avaliacoes) {
    const tr = document.createElement("tr");
    tr.append(celula(item.numero_ap), celula(formatarDezenas(item.dezenas), "auditoria-dezenas"), celula(item.criterio.categoria),
      celula(`${item.criterio.codigo} — ${item.criterio.nome}`), celula(item.grupo ? `${item.grupo.codigo} — ${item.grupo.nome}` : "—"),
      celula(formatarResultado(item.esperado), "auditoria-valor"), celula(formatarResultado(item.calculado), "auditoria-valor"),
      celula(item.aprovado ?? "Pendente", `auditoria-situacao auditoria-situacao--${item.aprovado?.toLowerCase() || "pendente"}`));
    e.corpo.append(tr);
  }
  e.vazia.hidden = dados.avaliacoes.length !== 0; pagina = dados.paginacao.pagina; totalPaginas = dados.paginacao.total_paginas;
  e.pagina.textContent = `Página ${pagina} de ${totalPaginas}`; e.anterior.disabled = pagina <= 1; e.seguinte.disabled = pagina >= totalPaginas;
  e.consulta.textContent = `${dados.paginacao.total_itens.toLocaleString("pt-BR")} avaliações encontradas`;
}

function linhaTexto(rotulo, valor) {
  const linha = document.createElement("p"), titulo = document.createElement("strong"); titulo.textContent = `${rotulo}: `;
  linha.append(titulo, document.createTextNode(valor)); return linha;
}
function renderizarRelatorio(dados) {
  const f = dados.fechamento;
  e.relatorioFechamento.textContent = `${f.aprovadas.toLocaleString("pt-BR")} S · ${f.divergentes.toLocaleString("pt-BR")} N · ${f.pendentes.toLocaleString("pt-BR")} pendentes`;
  e.corpoRelatorio.replaceChildren();
  for (const item of dados.criterios) {
    const tr = document.createElement("tr");
    tr.append(celula(`${item.codigo} — ${item.nome}`), celula(item.estado), celula(item.exigidas), celula(item.executadas),
      celula(item.aprovadas), celula(item.divergentes), celula(item.pendentes), celula(item.estado_catalogo)); e.corpoRelatorio.append(tr);
  }
  e.listaDivergencias.replaceChildren(); e.semDivergencias.hidden = dados.divergencias.length !== 0;
  for (const item of dados.divergencias) {
    const artigo = document.createElement("article"), titulo = document.createElement("h3");
    artigo.className = "auditoria-divergencia";
    titulo.textContent = `${item.criterio.codigo} — ${item.criterio.nome} · concurso ${item.numero_ap}`;
    artigo.append(titulo, linhaTexto("Combinação", formatarDezenas(item.dezenas)),
      linhaTexto("Categoria e grupo", `${item.criterio.categoria} · ${item.grupo ? `${item.grupo.codigo} — ${item.grupo.nome}` : "sem grupo"}`),
      linhaTexto("Esperado", formatarResultado(item.esperado)), linhaTexto("Calculado", formatarResultado(item.calculado)),
      linhaTexto("Diferença", item.diferenca ?? "não aplicável"), linhaTexto("Assinatura executada", item.assinatura_executada ?? "não executada"),
      linhaTexto("Assinatura atual", item.assinatura_atual), linhaTexto("Hipótese diagnóstica da IA", item.hipotese_diagnostica));
    e.listaDivergencias.append(artigo);
  }
}
function renderizarSincronizacao(sincronizacao) {
  if (!sincronizacao) return;
  const quantidade = (campo) => (sincronizacao[campo] || []).length;
  e.relatorioSincronizacao.textContent = `Última atualização: ${quantidade("incluidos")} novos, ${quantidade("implementacoes_alteradas")} implementações alteradas, ${quantidade("regras_alteradas")} regras alteradas, ${quantidade("excluidos")} excluídos e ${sincronizacao.avaliacoes_criadas || 0} avaliações criadas.`;
}
async function carregar() {
  e.consulta.textContent = "Carregando avaliações…";
  try { renderizar(await respostaJson(await fetch(`/api/validacao/quadro?${parametros()}`))); } catch (erro) { e.consulta.textContent = erro.message; }
}
async function carregarRelatorio() {
  try { renderizarRelatorio(await respostaJson(await fetch("/api/validacao/relatorio"))); } catch (erro) { e.relatorioFechamento.textContent = erro.message; }
}
const modal = criarModalAndamento({ titulo: "Atualizando Validação e auditoria",
  iniciar: async () => respostaJson(await fetch("/api/validacao/execucoes", { method: "POST" })),
  consultar: async (id) => respostaJson(await fetch(`/api/validacao/execucoes/${encodeURIComponent(id)}`)),
  apresentarResultado: diagnosticoFinalValidacao });
e.atualizar.addEventListener("click", async () => {
  if (modal.estaExecutando()) return; e.atualizar.disabled = true;
  try { const execucao = await modal.abrir(); renderizarSincronizacao(execucao?.resultado?.sincronizacao); await Promise.all([carregar(), carregarRelatorio()]); }
  finally { e.atualizar.disabled = false; }
});
e.formulario.addEventListener("submit", (evento) => { evento.preventDefault(); pagina = 1; carregar(); });
e.limpar.addEventListener("click", () => { e.formulario.reset(); pagina = 1; carregar(); });
e.anterior.addEventListener("click", () => { if (pagina > 1) { pagina -= 1; carregar(); } });
e.seguinte.addEventListener("click", () => { if (pagina < totalPaginas) { pagina += 1; carregar(); } });
Promise.all([carregar(), carregarRelatorio()]);
