# Evidência de teste — subetapa 18.8

Data: 28/10/2026

## Proteções

- execução aceita somente modo `amostra`;
- limite obrigatório de **5.000** combinações;
- confirmação de processamento integral obrigatoriamente falsa;
- API disponível somente por `POST`, sem parâmetro de quantidade;
- nenhuma combinação ou resultado do ensaio é persistido;
- configuração, perfil histórico e versões recebem fotografia SHA-256.

Checksum observado:

`10f549c1b1c6cd4e05b38d8f8b981a5db33bedb6fb101805e322530bb0274db3`

## Resultado real da amostra

- analisadas: **5.000**;
- excluídas: **4.580**;
- aprovadas: **420**.

### Estatística

- entrada: 5.000; exclusões: 2.999; saldo: 2.001;
- soma/média: 1.701 exclusões;
- mediana: 441 exclusões líquidas;
- desvio-padrão: 857 exclusões líquidas.

### Geometria

- entrada: 2.001; exclusões: 1.578; saldo: 423;
- extensão: 640;
- perímetro: 96;
- área: 289;
- regiões: 229;
- centro de gravidade: 324.

### Padrões

- entrada: 423; exclusões PG_001: 3; saldo: 420.

## Comparação

O screener anterior aprovou **4.409** na mesma amostra e o novo aprovou **420**,
diferença de -3.989. Isso não mede superioridade. Os funis não são equivalentes:

- a ordem mudou para estatística, geometria e padrões;
- o novo usa média histórica ±1 desvio-padrão nas dez medidas;
- o novo possui cinco filtros geométricos, contra somente extensão no anterior;
- padrões agora usam classificação exclusiva de PG_001 e raridade `< 10%`.

## Testes

- Python: **487 aprovados**;
- JavaScript: **35 aprovados**;
- Chrome com respostas controladas: **18 aprovados**;
- Chrome com API e PostgreSQL reais: **1 aprovado**;
- API real: 5.000 analisadas, três famílias e proteção integral confirmada;
- servidor local atualizado: PID **34596**, único listener na porta 5050.

Os `ResourceWarning` preexistentes na leitura de três arquivos do frontend não
causaram falha e não pertencem ao novo ensaio.
