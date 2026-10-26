# Teste do Item 3.2 — localização do cabeçalho e leitura

Data: 2026-10-26.

## Resultado

- sete testes específicos aprovados;
- 64 testes acumulados aprovados;
- cabeçalho localizado na linha 7 da fonte real;
- cabeçalho controlado localizado quando deslocado para a linha 4;
- mudanças de ordem, maiúsculas e espaços nos nomes das colunas aceitas;
- coluna ausente ou renomeada rejeitada com código identificável;
- célula obrigatória vazia e data inválida rejeitadas com linha e campo;
- linhas totalmente vazias ignoradas;
- datas nativas do Excel normalizadas de `datetime` para `date`.

## Verificação da fonte real

O leitor devolveu 3.069 objetos `ResultadoEntrada`. O primeiro corresponde ao
concurso 3069, data 11/10/2026 e resultados 47, 5, 22, 44, 57 e 19.

SHA-256 antes e depois da leitura:

`027726F33A89738AD9DC95FAC9A7ECCD390609F5C63CACBB2F00B3873724CE67`

O arquivo foi aberto com `read_only=True` e `data_only=True`, fechado em bloco
`finally` e não foi modificado.

O Item 3.2 não calcula campos derivados nem grava no banco de dados.
