# Evidência — subetapa 22.17.0

Data: 2026-11-02

## Escopo

Subetapa exclusivamente documental. Nenhum HTML, CSS, JavaScript, API ou banco
de dados foi alterado.

## Inventário dos modais

- `modal-andamento.js` é compartilhado por auditoria e frequências, mas sua
  responsabilidade é progresso, cancelamento e resultado de tarefa assíncrona.
- Ajuda, prévia, configuração de faixas e aparência usam `<dialog>` com
  estruturas próprias de suas finalidades.
- Os dois gráficos novos usarão um único modal gráfico e um controlador comum;
  não serão criados dois diálogos nem duas estruturas permanentes.
- Serão reaproveitados os padrões existentes de fundo, cabeçalho, rodapé,
  acessibilidade, foco, `Esc` e encerramento, sem acoplar o gráfico ao modal de
  andamento.

## Contrato matemático

- Distribuição real: `n(d) / N × 100` para cada duração inteira `d`.
- Curva normal: área teórica entre `d − 0,5` e `d + 0,5`, usando média e
  desvio-padrão populacional calculados sobre os mesmos intervalos.
- Ordenação percentual: `X = i / N × 100` e
  `Y = intervalo_i / maior_intervalo × 100`.
- Repetições permanecem como ocorrências independentes.
- A grade de 5% não arredonda nem desloca pontos.
- Desvio zero e conjunto vazio terão tratamento explícito.
