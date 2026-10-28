# Contrato da fotografia de configuração

A fotografia identifica exatamente a configuração usada por uma execução do
screener. Ela é criada **antes** do processamento das combinações e não consulta
novamente configurações mutáveis durante aquela execução.

## Conteúdo congelado

- versão do formato, modo, semente e limite de combinações;
- famílias e filtros, na ordem efetiva de execução;
- parâmetros canônicos de cada filtro e versões das funções de cálculo;
- intervalo histórico e denominador usados em cada grupo de padrões;
- frequências históricas de todos os subgrupos e da classe sem correspondência;
- limite e operador de raridade (`<` ou `<=`);
- lista de padrões excludentes resultante dessa política.

O avaliador Python não integra a fotografia: código executável é identificado por
sua versão de cálculo. Alterar qualquer dado fotografado produz outro SHA-256.

## Reprodutibilidade

Mapas são ordenados, datas usam ISO, decimais são textos exatos e listas são
congeladas. `float`, conjuntos, horários e números não finitos são recusados para
evitar representações ambíguas. O JSON usa uma serialização canônica e seu SHA-256
permite detectar alteração posterior.

Para os grupos de padrões, quantidade, percentual e denominador precisam fechar.
A classe sem correspondência participa do fechamento estatístico, mas nunca vira
um código de padrão excludente.
