# Evidência — subetapa 31.9.4.2B

Data: 14/11/2026

## Escopo autorizado

Criar e validar uma função genérica e isolada para plotar os círculos das
manchas de médias. A integração com Média espacial, CG1 e CG2 não pertence a
esta subetapa.

## Implementação

- módulo: `frontend/js/plotagem-manchas.js`;
- entrada: destino SVG, coordenada lógica, conversor de coordenadas, diâmetro em
  milímetros, cor, intensidade e classe opcional;
- saída: exatamente um elemento SVG `circle` anexado ao destino;
- coordenadas decimais são entregues ao conversor sem arredondamento;
- coordenadas coincidentes geram círculos independentes;
- diâmetro, cor e intensidade são aplicados diretamente ao círculo;
- entradas inválidas são recusadas antes do desenho.

O módulo permanece sem importação no Painel. Assim, esta subetapa não modifica
o desenho atual das manchas.

## Validação

Comando específico:

```text
node --test frontend/tests/plotagem_manchas.test.mjs
```

Resultado: 4 testes aprovados, 0 falhas.

Comando completo:

```text
npm run test:frontend
```

Resultado: 138 testes aprovados, 0 falhas.
