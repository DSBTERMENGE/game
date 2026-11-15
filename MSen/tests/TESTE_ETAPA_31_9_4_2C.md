# Evidência — subetapa 31.9.4.2C

Data: 14/11/2026

## Escopo autorizado

Preparar a configuração visual das manchas de médias, sem integrar ou alterar
o algoritmo que desenha a Média espacial, o CG1 ou o CG2.

## Implementação

- a configuração visual foi versionada como `msen.configuracaoVisual.v3`;
- configurações anteriores v2 e v1 permanecem legíveis;
- Média espacial: marrom `#8b4513`;
- CG1: roxo `#7566d9`;
- CG2: azul `#2471a3`;
- círculos de referência: amarelo `#f1c40f`;
- diâmetro padrão dos pontos: 3 mm;
- fator padrão de intensidade: 0,12;
- os seis valores podem ser alterados no quadro Configuração visual;
- nenhum desses campos foi ligado ao desenho das manchas nesta subetapa.

## Validação

Testes direcionados:

```text
node --test frontend/tests/configuracao_visual_manchas.test.mjs frontend/tests/painel_navegacao.test.mjs
```

Resultado: 31 testes aprovados, 0 falhas.

Suíte completa:

```text
npm run test:frontend
```

Resultado: 141 testes aprovados, 0 falhas.
