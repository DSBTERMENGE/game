import { criarCrudNavegavel } from "./crud-navegavel.js";
import { criarApiPadroes, listarGruposParaFiltro } from "./padroes-api.js";

const raiz = document.querySelector("#cadastro-padroes");
const campos = [
  {
    nome: "titulo", rotulo: "Nome do padrão", tipo: "texto", obrigatorio: true,
    largura: "larga",
    validar: (valor) => String(valor).length > 200 ? "Nome do padrão aceita no máximo 200 caracteres." : "",
  },
  {
    nome: "descricao", rotulo: "Descrição", tipo: "texto-longo", linhas: 7,
    obrigatorio: true, largura: "total",
    validar: (valor) => String(valor).length > 4000 ? "Descrição aceita no máximo 4.000 caracteres." : "",
  },
  {
    nome: "funcaoDetectora", rotulo: "Função detectora", tipo: "texto",
    obrigatorio: false, largura: "total", apenasEdicao: true,
    validar: (valor) => String(valor ?? "").trim().length > 500
      ? "Função detectora aceita no máximo 500 caracteres." : "",
  },
];

async function iniciar() {
  try {
    const grupos = await listarGruposParaFiltro();
    criarCrudNavegavel({
      raiz,
      titulo: "Padrões",
      descricao: "Cadastre os padrões, vincule-os ao Grupo e informe a função detectora quando ela estiver implementada.",
      campos,
      colunas: [{ campo: "titulo", rotulo: "Nome do padrão" }],
      filtros: [{
        nome: "grupo_cod", rotulo: "Grupo", obrigatorio: true,
        rotuloVazio: "Selecione um Grupo",
        opcoes: grupos.map((grupo) => ({ valor: grupo.grupo_cod, rotulo: grupo.grupo_nome })),
      }],
      api: criarApiPadroes(),
      usarOrdenacao: false,
      usarExclusao: true,
      layout: "selecao",
      obterIdentificador: (registro) => registro.padrao_cod,
    });
  } catch (_erro) {
    raiz.innerHTML = '<p class="padroes-erro" role="alert">Não foi possível carregar os Grupos. Atualize a página e tente novamente.</p>';
  }
}

iniciar();
