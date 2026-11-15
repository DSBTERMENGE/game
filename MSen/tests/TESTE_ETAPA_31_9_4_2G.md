# Evidência — subetapa 31.9.4.2G

Data: 14/11/2026

## Auditoria do código

- Média espacial, CG1 e CG2 chamam `prepararManchaDeMedia`;
- as três camadas chamam `plotarCirculo`;
- não resta arredondamento das coordenadas em passos de 0,25;
- a antiga função `desenharConcentracao` foi removida;
- Quadrantes e Dezenas continuam fora do mecanismo das médias.

## Testes direcionados

```text
node --test frontend/tests/configuracao_visual_manchas.test.mjs frontend/tests/manchas_medias.test.mjs frontend/tests/plotagem_manchas.test.mjs frontend/tests/painel_navegacao.test.mjs
```

Resultado: 44 testes aprovados, 0 falhas.

## Suíte completa do frontend

```text
npm run test:frontend
```

Resultado: 145 testes aprovados, 0 falhas.

## API real

A consulta somente de leitura a `http://127.0.0.1:5050` confirmou:

- 3.069 resultados;
- 3.069 registros de manchas;
- zero coordenadas inválidas de CG1;
- zero coordenadas inválidas de CG2.

O interpretador Python global disponível não possui o pacote `pytest` e o
workspace não contém ambiente virtual. Nenhuma dependência foi instalada. A API
foi validada diretamente no servidor real já em execução.

## Resultado

O conjunto Média espacial, CG1 e CG2 está tecnicamente validado. A continuidade
do Painel pode seguir para o mecanismo independente dos Quadrantes e, depois,
para a representação das ocorrências das Dezenas.
