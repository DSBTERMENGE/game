# Evidência de teste — subetapa 18.3

Data: 28/10/2026

## Escopo

Conexão da família estatística ao contrato extensível, ainda sem interface, API,
persistência ou execução sobre a amostra de 5.000 combinações.

## Verificações

- soma e média usam uma decisão e uma contabilização;
- a evidência mostra soma, média e limites equivalentes;
- mediana e desvio-padrão são filtros independentes;
- funções matemáticas oficiais calculam todos os valores;
- valores internos e exatamente nos limites são aceitos;
- valores externos são excluídos;
- cada filtro avalia somente o saldo recebido;
- subtotal e fechamento global reconciliam.

## Resultado

- Testes específicos: **5 aprovados**.
- Regressão Python: **466 testes aprovados**.
- Os `ResourceWarning` preexistentes na leitura de três arquivos do frontend não
  causaram falha e não pertencem à família estatística.
