# Dependências para planilhas Excel

## Decisão do Item 3.1

O projeto utilizará `openpyxl` para arquivos no formato `.xlsx`. A dependência
foi limitada à série 3, começando na versão 3.1.5. A biblioteca permite abrir a
planilha em modo somente leitura, opção que será adotada pelo leitor no Item 3.2.

Também foi registrada `defusedxml`, recomendada pela própria documentação do
`openpyxl` para reduzir riscos relacionados a XML malicioso. Ela será instalada
normalmente junto com as dependências do projeto no ambiente de execução.

O Item 3.1 não implementa a importação. Ele apenas registra as dependências e
fornece entradas pequenas, reproduzíveis e separadas da fonte original.

Referências oficiais:

- https://openpyxl.readthedocs.io/en/stable/
- https://pypi.org/project/openpyxl/
