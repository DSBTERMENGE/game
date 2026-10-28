# Evidência de teste — subetapa 18.5

Data: 28/10/2026

## Escopo

Conexão dos grupos de padrões ao funil extensível usando a fotografia histórica,
sem interface, banco ou ensaio sobre as 5.000 combinações.

## Verificações

- classificador oficial do grupo sequencial PG_001;
- uma classificação por combinação e por grupo;
- exclusão somente de padrão presente na lista fotografada;
- classe sem correspondência aprovada e incluída no perfil histórico;
- evidência com frequência, denominador, limite e operador;
- múltiplos grupos ordenados com exclusões líquidas;
- interrupção após a primeira exclusão;
- erro para classificador ausente ou classe não fotografada.

## Resultado

- Testes específicos: **6 aprovados**.
- Regressão Python: **479 testes aprovados**.
- Os `ResourceWarning` preexistentes na leitura de três arquivos do frontend não
  causaram falha e não pertencem à família de padrões.
