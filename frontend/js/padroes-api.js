const API_PADROES = "/api/padroes";
const API_GRUPOS = "/api/grupos-padroes";

async function requisitar(url, opcoes = {}, fetchImpl = fetch) {
  const resposta = await fetchImpl(url, {
    headers: { Accept: "application/json", ...(opcoes.body ? { "Content-Type": "application/json" } : {}), ...(opcoes.headers ?? {}) },
    ...opcoes,
  });
  const corpo = await resposta.json().catch(() => ({}));
  if (!resposta.ok) throw new Error(corpo.erro?.mensagem ?? "Não foi possível concluir a operação com o Padrão.");
  return corpo;
}

function normalizar(padrao) {
  return { ...padrao, id: padrao.padrao_cod, titulo: padrao.padrao_nome, descricao: padrao.padrao_descr };
}

export async function listarGruposParaFiltro(fetchImpl = fetch) {
  const corpo = await requisitar(API_GRUPOS, {}, fetchImpl);
  return corpo.grupos ?? [];
}

export function criarApiPadroes(fetchImpl = fetch) {
  let grupoAtual = null;
  return {
    async listar(consulta) {
      grupoAtual = consulta.grupo_cod || null;
      if (!grupoAtual) return { registros: [], total: 0 };
      const corpo = await requisitar(`${API_PADROES}?grupo_cod=${encodeURIComponent(grupoAtual)}`, {}, fetchImpl);
      const trecho = String(consulta.busca ?? "").trim().toLocaleLowerCase("pt-BR");
      const registros = (corpo.padroes ?? []).map(normalizar).filter((padrao) =>
        !trecho || padrao.titulo.toLocaleLowerCase("pt-BR").includes(trecho)
      );
      return { registros, total: registros.length };
    },
    async criar(dados) {
      const corpo = await requisitar(API_PADROES, {
        method: "POST",
        body: JSON.stringify({ grupo_cod: grupoAtual, padrao_nome: dados.titulo, padrao_descr: dados.descricao }),
      }, fetchImpl);
      return { registro: normalizar(corpo.padrao) };
    },
    async atualizar(codigo, dados) {
      const corpo = await requisitar(`${API_PADROES}/${encodeURIComponent(codigo)}`, {
        method: "PUT",
        body: JSON.stringify({ grupo_cod: grupoAtual, padrao_nome: dados.titulo, padrao_descr: dados.descricao }),
      }, fetchImpl);
      return { registro: normalizar(corpo.padrao) };
    },
    excluir(codigo) {
      return requisitar(`${API_PADROES}/${encodeURIComponent(codigo)}`, { method: "DELETE" }, fetchImpl);
    },
  };
}
