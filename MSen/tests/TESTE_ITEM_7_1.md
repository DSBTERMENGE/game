# Teste do Item 7.1

Data: 2026-10-26

## Fluxo integrado local

```text
Excel -> Google Chrome -> POST /api/resultados/importar -> cálculos
      -> PostgreSQL temporário -> relatório -> GET /api/resultados -> interface
```

## Isolamento e segurança

- database efêmero no padrão `games_test_7_1_<processo>`;
- nomes fora desse padrão são rejeitados antes de qualquer comando SQL;
- migração 001 aplicada antes da importação;
- servidor Flask e database removidos ao final;
- auditoria final encontrou zero databases temporários e zero portas abertas;
- databases persistentes `games`, `postgres` e `financas` não podem ser alvos
  do removedor controlado.

## Primeira importação

- planilha: `resultados_validos.xlsx`;
- linhas analisadas e inseridas: 2;
- resultados armazenados: 2;
- frequências armazenadas: 60;
- soma de ocorrências: 12;
- concurso 100: dezenas `[1, 10, 20, 30, 40, 60]`;
- soma calculada: 161;
- média aritmética: 26,833333;
- mediana: 25,0;
- relatório preservado na interface depois do recarregamento.

## Reimportação

- inseridos: 0;
- iguais: 2;
- alterados: 0;
- inválidos: 0;
- resultados, frequências e ocorrências permaneceram inalterados.

## Regressão

- 2 testes integrados PostgreSQL/Chrome aprovados em 8,1 segundos;
- 3 testes Chrome com API simulada aprovados;
- 19 testes unitários de frontend aprovados;
- 140 testes Python aprovados.

O PostgreSQL persistente e o PythonAnywhere não foram alterados.
