const BASE = "/api/grupos-padroes";

async function requisitar(url, opcoes = {}, fetchImpl = fetch) {
  const resposta = await fetchImpl(url, {
    headers: { Accept: "application/json", ...(opcoes.body ? { "Content-Type": "application/json" } : {}), ...(opcoes.headers ?? {}) },
    ...opcoes,
  });
  const corpo = await resposta.json().catch(() => ({}));
  if (!resposta.ok) throw new Error(corpo.erro?.mensagem ?? "Não foi possível concluir a operação com o Grupo.");
  return corpo;
}

function normalizar(grupo) {
  return { ...grupo, id: grupo.grupo_cod, titulo: grupo.grupo_nome, descricao: grupo.grupo_descr };
}

export function criarApiGrupos(fetchImpl = fetch) {
  return {
    async listar(consulta) {
      const corpo = await requisitar(BASE, {}, fetchImpl);
      const trecho = String(consulta.busca ?? "").trim().toLocaleLowerCase("pt-BR");
      const todos = (corpo.grupos ?? []).map(normalizar).filter((grupo) =>
        !trecho || grupo.titulo.toLocaleLowerCase("pt-BR").includes(trecho)
      );
      return { registros: todos, total: todos.length };
    },
    async criar(dados) {
      const corpo = await requisitar(BASE, {
        method: "POST", body: JSON.stringify({ grupo_nome: dados.titulo, grupo_descr: dados.descricao }),
      }, fetchImpl);
      return { registro: normalizar(corpo.grupo) };
    },
    async atualizar(codigo, dados) {
      const corpo = await requisitar(`${BASE}/${encodeURIComponent(codigo)}`, {
        method: "PUT", body: JSON.stringify({ grupo_nome: dados.titulo, grupo_descr: dados.descricao }),
      }, fetchImpl);
      return { registro: normalizar(corpo.grupo) };
    },
    excluir(codigo) {
      return requisitar(`${BASE}/${encodeURIComponent(codigo)}`, { method: "DELETE" }, fetchImpl);
    },
  };
}
