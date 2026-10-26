# Teste do Item 4.2 — controle de migrações

Data: 2026-10-26.

## Testes automatizados

- oito testes específicos aprovados;
- 100 testes acumulados aprovados;
- ordenação numérica de versões;
- SHA-256 calculado sobre os bytes armazenados;
- arquivos fora do padrão ignorados;
- versão duplicada rejeitada;
- pasta ausente e migração vazia rejeitadas;
- controle transacional explícito completo retirado em memória;
- `BEGIN` sem `COMMIT`, ou o inverso, rejeitado.

Durante o primeiro teste, a expectativa de checksum não considerava a conversão
de LF para CRLF feita pelo Windows. O teste foi corrigido para conferir os bytes
realmente gravados; o executor não precisou ser alterado.

## Testes reais isolados

Ambiente: cluster PostgreSQL 16.11 temporário, porta 55442.

### Banco vazio

- migração `001` aplicada;
- uma versão registrada;
- três tabelas esperadas encontradas;
- 60 sementes de frequência encontradas.

### Banco atualizado

- nenhuma migração reaplicada;
- versão `001` reconhecida como já aplicada;
- checksum alterado em cópia temporária rejeitado como `CHECKSUM_DIVERGENTE`.

### Erro e rollback

A migração temporária `002` criou uma tabela e depois provocou divisão por zero.
O executor devolveu `MIGRACAO_FALHOU`; a tabela e o registro `002` não
permaneceram no banco.

### Concorrência

Duas conexões executaram simultaneamente uma migração com espera intencional.
Uma aplicou `001`; a segunda aguardou a trava e reconheceu `001` como existente.
Ao final havia uma linha de controle e uma única linha na tabela de teste.

## Isolamento

O cluster temporário foi parado e removido. A porta 55442 ficou sem resposta.
Os PostgreSQL persistentes 16 e 18 e o PythonAnywhere não foram alterados.
