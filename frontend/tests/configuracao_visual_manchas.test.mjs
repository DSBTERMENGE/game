import assert from "node:assert/strict";
import test, { beforeEach } from "node:test";

import {
  CONFIGURACAO_VISUAL_PADRAO,
  aplicarConfiguracaoVisual,
  carregarConfiguracaoVisual,
  salvarConfiguracaoVisual,
} from "../js/configuracao-visual.js";

let dados;

beforeEach(() => {
  dados = new Map();
  globalThis.localStorage = {
    getItem: (chave) => dados.get(chave) ?? null,
    setItem: (chave, valor) => dados.set(chave, String(valor)),
  };
});

test("define os padrões separados das três médias e das referências", () => {
  assert.equal(CONFIGURACAO_VISUAL_PADRAO.corMediaEspacial, "#8b4513");
  assert.equal(CONFIGURACAO_VISUAL_PADRAO.corCg1, "#7566d9");
  assert.equal(CONFIGURACAO_VISUAL_PADRAO.corCg2, "#2471a3");
  assert.equal(CONFIGURACAO_VISUAL_PADRAO.corReferenciasMancha, "#f1c40f");
  assert.equal(CONFIGURACAO_VISUAL_PADRAO.diametroPontosMancha, 3);
  assert.equal(CONFIGURACAO_VISUAL_PADRAO.fatorIntensidadeMancha, 0.12);
});

test("preserva a configuração v2 e completa os novos campos com os padrões", () => {
  dados.set("msen.configuracaoVisual.v2", JSON.stringify({
    corLinha: "#123456",
    diametroVertices: 4,
  }));

  const configuracao = carregarConfiguracaoVisual();

  assert.equal(configuracao.corLinha, "#123456");
  assert.equal(configuracao.diametroVertices, 4);
  assert.equal(configuracao.corMediaEspacial, "#8b4513");
  assert.equal(configuracao.fatorIntensidadeMancha, 0.12);
});

test("salva na versão 3 e expõe as novas propriedades visuais", () => {
  const configuracao = salvarConfiguracaoVisual({
    corMediaEspacial: "#654321",
    corCg1: "#112233",
    corCg2: "#445566",
    corReferenciasMancha: "#abcdef",
    diametroPontosMancha: 2.5,
    fatorIntensidadeMancha: 0.2,
  });
  const propriedades = {};
  aplicarConfiguracaoVisual({
    style: { setProperty: (nome, valor) => { propriedades[nome] = valor; } },
  }, configuracao);

  assert.ok(dados.has("msen.configuracaoVisual.v3"));
  assert.equal(propriedades["--cor-media-espacial"], "#654321");
  assert.equal(propriedades["--cor-cg1"], "#112233");
  assert.equal(propriedades["--cor-cg2"], "#445566");
  assert.equal(propriedades["--cor-referencias-mancha"], "#abcdef");
  assert.equal(propriedades["--diametro-pontos-mancha"], "2.5mm");
  assert.equal(propriedades["--fator-intensidade-mancha"], "0.2");
});
