import { criarCrudNavegavel } from "./crud-navegavel.js";
import { criarApiGrupos } from "./grupos-padroes-api.js";

const campos = [
  {
    nome: "titulo", rotulo: "Nome do grupo", tipo: "texto", obrigatorio: true,
    largura: "larga",
    validar: (valor) => String(valor).length > 200 ? "Nome do grupo aceita no máximo 200 caracteres." : "",
  },
  {
    nome: "descricao", rotulo: "Descrição", tipo: "texto-longo", linhas: 7,
    obrigatorio: true, largura: "total",
    validar: (valor) => String(valor).length > 4000 ? "Descrição aceita no máximo 4.000 caracteres." : "",
  },
];

criarCrudNavegavel({
  raiz: document.querySelector("#cadastro-grupos"),
  titulo: "Grupo",
  descricao: "Cadastre os grupos usados para organizar os critérios e padrões do Screener.",
  campos,
  colunas: [
    { campo: "titulo", rotulo: "Nome do grupo" },
    { campo: "grupo_cod", rotulo: "Código" },
  ],
  api: criarApiGrupos(),
  usarOrdenacao: false,
  usarExclusao: true,
  layout: "selecao",
  obterIdentificador: (registro) => registro.grupo_cod,
});
