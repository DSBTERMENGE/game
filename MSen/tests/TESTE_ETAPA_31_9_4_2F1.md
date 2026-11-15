# Evidência — subetapa 31.9.4.2F1

Data: 14/11/2026

## Escopo autorizado

Aplicar o mecanismo comum somente ao CG1. O CG2 deveria permanecer no mecanismo
anterior até autorização específica.

## Implementação

- Média espacial e CG1 chamam a mesma função de preparação e plotagem;
- cada coordenada decimal válida de CG1 gera um círculo independente;
- a cor padrão do CG1 é roxa e vem da configuração visual salva;
- diâmetro e fator de intensidade também vêm da configuração salva;
- pontos coincidentes não são reunidos nem redimensionados;
- o CG1 possui centro e referências amarelas de 20%, 40% e 60%;
- o resumo do CG1 informa o centro, as quatro parcelas e suas frequências;
- o CG2 continua usando a rotina anterior de concentração.

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
