# Evidência de teste — Item 9.7

Data: 2026-10-26

## Interface criada

- botão **Cadastro de Padrões** na área de comandos;
- janela em formato de grade com cabeçalho fixo;
- rolagem vertical e horizontal;
- formulário de inclusão acima da tabela;
- edição direta de nome e descrição em cada linha;
- código e estatísticas sem campos editáveis;
- indicação `Implementada` ou `Pendente` para a função Python;
- exclusão somente depois de confirmação;
- mensagens de sucesso e erro acessíveis.

## Organização

- estrutura em `frontend/index.html`;
- aparência exclusiva em `frontend/css/padroes.css`;
- comportamento exclusivo em `frontend/js/padroes.js`;
- código da grade não foi misturado ao módulo de gráficos.

## Testes

- 20 testes unitários de frontend aprovados;
- 4 fluxos no Google Chrome com API simulada aprovados em 3,6 segundos;
- o fluxo da grade criou `PD_004`, editou seus textos, exibiu estatísticas como
  somente leitura e excluiu após confirmação;
- 174 testes Python aprovados;
- 2 fluxos integrados Chrome/PostgreSQL aprovados em 8,6 segundos;
- o Chrome carregou os três padrões e as estatísticas reais do `games` sem
  executar mutações no banco persistente;
- nenhum database ou servidor temporário permaneceu;
- PythonAnywhere não foi acessado.

## Conclusão

A grade CRUD está funcional no Google Chrome e preserva a separação entre HTML,
CSS e JavaScript. O Item 9.7 está concluído.
