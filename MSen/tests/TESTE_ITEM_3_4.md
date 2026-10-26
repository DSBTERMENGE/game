# Teste do Item 3.4 — comparação incremental

Data: 2026-10-26.

## Resultado

- oito testes específicos aprovados;
- 78 testes acumulados aprovados;
- reimportar a mesma planilha classificou as duas linhas como `IGUAL` e não
  produziu novidades;
- a planilha atualizada classificou o concurso 100 como `IGUAL`, o 101 como
  `ALTERADA` e o 102 como `NOVA`;
- a divergência do concurso 101 preservou separadamente os dados existentes e
  os importados, sem sobrescrever nenhum deles;
- uma linha inválida foi relatada sem impedir a classificação da linha válida;
- as duas ocorrências de um concurso repetido na planilha foram classificadas
  como `INVALIDA`;
- diferença apenas na versão do cálculo não foi tratada como alteração dos
  dados originais;
- a comparação não modificou a planilha nem a coleção de existentes.

## Limite desta subetapa

A comparação ocorre somente em memória. A integração que buscará existentes no
PostgreSQL e gravará apenas registros autorizados pertence à etapa de
persistência. Nenhuma operação de banco foi executada no Item 3.4.
