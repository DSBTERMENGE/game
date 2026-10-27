# Evidência do Item 12.3 — registro e estatísticas de mesma linha

Data: 2026-10-27.

## Implementação

- `PD_007` associado ao detector de exatamente duas dezenas na linha mais
  ocupada;
- `PD_008` associado ao detector de exatamente três dezenas;
- `PD_009` associado ao detector de quatro, cinco ou seis dezenas;
- registro novo e independente criado a cada chamada;
- catálogo unificado ampliado para `PD_001`–`PD_009`;
- cálculo conjunto reutilizando ocorrências, intervalos, média e desvio-padrão
  populacional;
- série histórica materializada uma única vez para aceitar iteradores.

## Testes

Foram aprovados 55 testes direcionados, incluindo:

- registro dos três novos códigos e catálogo com nove detectores;
- ocorrências conhecidas dos três padrões;
- intervalos de 15, 10 e 20 concursos;
- média e desvio-padrão populacional;
- histórico vazio ou com uma ocorrência;
- histórico fora de ordem fornecido por iterador;
- regressão dos detectores anteriores, estrutura pública e API.

Nenhum banco de dados foi acessado ou alterado. A integração ao serviço e a
persistência ficam reservadas à próxima subetapa.
