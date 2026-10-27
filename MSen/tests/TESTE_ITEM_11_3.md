# Evidência do Item 11.3 — registro e estatísticas de mesma coluna

Data: 2026-10-27.

## Implementação

- `PD_004` associado ao detector de sequência vertical com exatamente duas
  linhas subjacentes;
- `PD_005` associado ao detector de sequência vertical com exatamente três;
- `PD_006` associado ao detector de sequência vertical com quatro, cinco ou
  seis linhas subjacentes;
- registro novo e independente criado a cada chamada;
- cálculo conjunto reutilizando ocorrências, intervalos, média e desvio-padrão
  populacional já aprovados;
- série histórica materializada uma única vez para aceitar iteradores.

## Testes

Foram aprovados 29 testes direcionados, abrangendo:

- registro dos três códigos;
- ocorrências conhecidas dos três padrões;
- intervalos de 15, 10 e 20 concursos;
- média e desvio-padrão populacional;
- histórico vazio ou com uma ocorrência;
- histórico fora de ordem fornecido por iterador;
- regressão dos padrões sequenciais e da infraestrutura de registro.

A primeira tentativa incluiu no comando o módulo inexistente
`tests.test_registro_padroes`; os 22 testes encontrados naquela execução
passaram, e o comando foi corrigido para `tests.test_estrutura_padroes`, quando
os 29 testes passaram integralmente.

Nenhum banco de dados foi acessado ou alterado. A persistência das estatísticas
fica reservada à próxima subetapa.
