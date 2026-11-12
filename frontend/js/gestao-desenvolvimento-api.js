const BASE = "/api/gestao-desenvolvimento";

export async function requisitarGestao(url, opcoes = {}, fetchImpl = fetch) {
  const resposta = await fetchImpl(url, {
    headers: { Accept: "application/json", ...(opcoes.body ? { "Content-Type": "application/json" } : {}), ...(opcoes.headers ?? {}) },
    ...opcoes,
  });
  const corpo = await resposta.json().catch(() => ({}));
  if (!resposta.ok) {
    const erro = new Error(corpo.erro?.mensagem ?? "Não foi possível concluir a operação.");
    erro.codigo = corpo.erro?.codigo ?? "FALHA_HTTP";
    erro.status = resposta.status;
    throw erro;
  }
  return corpo;
}

export function criarApiGestao(fetchImpl = fetch) {
  return {
    listar(consulta) {
      const parametros = new URLSearchParams();
      for (const [nome, valor] of Object.entries(consulta)) {
        if (valor !== null && valor !== undefined && valor !== "") parametros.set(nome, String(valor));
      }
      return requisitarGestao(`${BASE}?${parametros}`, {}, fetchImpl);
    },
    consultar(id) {
      return requisitarGestao(`${BASE}/${encodeURIComponent(id)}`, {}, fetchImpl);
    },
    historico(id) {
      return requisitarGestao(`${BASE}/${encodeURIComponent(id)}/historico`, {}, fetchImpl);
    },
    criar(dados, chaveIdempotencia) {
      return requisitarGestao(BASE, {
        method: "POST", body: JSON.stringify({ dados, chave_idempotencia: chaveIdempotencia }),
      }, fetchImpl);
    },
    atualizar(id, dados, versao) {
      return requisitarGestao(`${BASE}/${encodeURIComponent(id)}`, {
        method: "PUT", body: JSON.stringify({ dados, versao_registro: versao }),
      }, fetchImpl);
    },
    arquivar(id, versao) {
      return requisitarGestao(`${BASE}/${encodeURIComponent(id)}/arquivamento`, {
        method: "POST", body: JSON.stringify({ versao_registro: versao }),
      }, fetchImpl);
    },
    desarquivar(id, versao) {
      return requisitarGestao(`${BASE}/${encodeURIComponent(id)}/arquivamento`, {
        method: "DELETE", body: JSON.stringify({ versao_registro: versao }),
      }, fetchImpl);
    },
  };
}
