# Evidência de teste — subetapa 18.4

Data: 28/10/2026

## Escopo

Conexão da família geométrica ao contrato extensível, sem interface, banco ou
execução sobre a amostra protegida.

## Verificações

- funções geométricas oficiais calculam todas as medidas;
- uma análise por combinação é compartilhada pelos cinco filtros;
- extensão, perímetro, área, regiões e centro possuem decisões ordenadas;
- X e Y do centro formam uma única decisão;
- valores exatamente nos limites são aceitos;
- primeira exclusão interrompe a combinação;
- centro ausente obedece à política explícita;
- subtotal registra exclusões líquidas e fecha com o saldo aprovado.

## Resultado

- Testes específicos: **7 aprovados**.
- Regressão Python: **473 testes aprovados**.
- Os `ResourceWarning` preexistentes na leitura de três arquivos do frontend não
  causaram falha e não pertencem à família geométrica.
