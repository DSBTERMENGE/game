# Evidência — subetapa 31.9.4.2F3

Data: 14/11/2026

## Escopo autorizado

Aplicar ao CG2 o mecanismo comum já validado para Média espacial e CG1, sem
alterar Quadrantes ou Dezenas.

## Implementação

- CG2 utiliza a função comum de preparação e plotagem;
- cada coordenada decimal válida produz um ponto independente;
- a cor azul vem do campo próprio da configuração visual salva;
- diâmetro e fator de intensidade também vêm da configuração salva;
- o CG2 possui centro, referências amarelas e resumo próprios;
- pontos coincidentes não são agrupados ou redimensionados;
- foi removida a rotina antiga que arredondava para 0,25, agrupava pontos e
  alterava o raio conforme a frequência;
- Média espacial e CG1 continuam usando o mesmo código comum;
- Quadrantes e Dezenas não foram modificados.

## Validação

Testes direcionados:

```text
node --test frontend/tests/manchas_medias.test.mjs frontend/tests/plotagem_manchas.test.mjs frontend/tests/painel_navegacao.test.mjs
```

Resultado: 41 testes aprovados, 0 falhas.

Suíte completa:

```text
npm run test:frontend
```

Resultado: 145 testes aprovados, 0 falhas.
