import { criarCrudNavegavel } from "./crud-navegavel.js";
import { criarApiGestao } from "./gestao-desenvolvimento-api.js";

const opcoes = (itens) => itens.map(([valor, rotulo]) => ({ valor, rotulo }));
const tipos = opcoes([
  ["ERRO", "Erro"], ["MAU_FUNCIONAMENTO", "Mau funcionamento"],
  ["MODIFICACAO", "Modificação"], ["NOVA_FUNCIONALIDADE", "Nova funcionalidade"],
  ["NAO_CLASSIFICADO", "Não classificado"],
]);
const estadosTrabalho = opcoes([
  ["NAO_INICIADO", "Não iniciado"], ["EM_ANALISE", "Em análise"],
  ["EM_ANDAMENTO", "Em andamento"], ["AGUARDANDO_VALIDACAO", "Aguardando validação"],
  ["CONCLUIDO", "Concluído"], ["CANCELADO", "Cancelado"],
]);
const estadosPublicacao = opcoes([
  ["NAO_APLICAVEL", "Não aplicável"], ["AGUARDANDO_PUBLICACAO", "Aguardando publicação"],
  ["PUBLICADO", "Publicado no PythonAnywhere"], ["FALHA_PUBLICACAO", "Falha na publicação"],
]);
const hojeLocal = () => {
  const agora = new Date();
  const local = new Date(agora.getTime() - agora.getTimezoneOffset() * 60_000);
  return local.toISOString().slice(0, 10);
};

const campos = [
  { nome: "tipo", rotulo: "Tipo", tipo: "select", opcoes: tipos, obrigatorio: true, valorInicial: "NAO_CLASSIFICADO", largura: "media" },
  { nome: "titulo", rotulo: "Título", tipo: "texto", obrigatorio: true, largura: "larga" },
  { nome: "data_registro", rotulo: "Data", tipo: "data", obrigatorio: true, valorInicial: hojeLocal(), largura: "curta" },
  { nome: "status_trabalho", rotulo: "Situação do trabalho", tipo: "select", opcoes: estadosTrabalho, obrigatorio: true, valorInicial: "NAO_INICIADO", largura: "media" },
  { nome: "status_publicacao", rotulo: "Situação da publicação", tipo: "select", opcoes: estadosPublicacao, obrigatorio: true, valorInicial: "NAO_APLICAVEL", largura: "media" },
  { nome: "pagina_origem", rotulo: "Página relacionada", tipo: "texto", largura: "larga" },
  { nome: "descricao", rotulo: "Descrição", tipo: "texto-longo", linhas: 9, obrigatorio: true, largura: "total" },
  { nome: "observacao_publicacao", rotulo: "Observação da publicação", tipo: "texto-longo", linhas: 3, largura: "total" },
];

const api = criarApiGestao();
const controlador = criarCrudNavegavel({
  raiz: document.querySelector("#gestao-desenvolvimento"),
  titulo: "Gestão do desenvolvimento",
  descricao: "Registre problemas, modificações e novas funcionalidades do Game.",
  campos,
  colunas: [
    { campo: "titulo", rotulo: "Título" }, { campo: "data_registro", rotulo: "Data" },
    { campo: "tipo", rotulo: "Tipo" }, { campo: "status_trabalho", rotulo: "Situação" },
  ],
  filtros: [
    { nome: "tipo", rotulo: "Tipo", opcoes: tipos },
    { nome: "status_trabalho", rotulo: "Trabalho", opcoes: estadosTrabalho },
    { nome: "status_publicacao", rotulo: "Publicação", opcoes: estadosPublicacao },
  ],
  usarOrdenacao: false,
  api,
});

const botaoAjuda = document.querySelector("#abrir-ajuda-gestao");
const cabecalho = document.querySelector("#gestao-desenvolvimento .crud-navegavel__cabecalho");
const botaoNovo = cabecalho.querySelector('[data-acao="novo"]');
const acoesCabecalho = document.createElement("div");
acoesCabecalho.className = "gestao-cabecalho-acoes";
botaoNovo.replaceWith(acoesCabecalho);
acoesCabecalho.append(botaoNovo, botaoAjuda);
document.querySelector(".gestao-acoes").remove();
