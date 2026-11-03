# Teste da subetapa 23.7 — previsão dos concursos futuros

Data: 03/11/2026.

## Escopo concluído

- uso do último concurso armazenado como corte real conhecido;
- horizonte configurável com valor padrão 1;
- mesmo corte para todos os alvos do horizonte;
- persistência idempotente da previsão, configuração e assinatura da origem;
- conferência posterior das previsões que receberam resultado;
- preservação das dezenas, faixas e ranking originalmente emitidos;
- geração de nova previsão após a entrada de resultados;
- preservação de previsões sobrepostas para o mesmo alvo, quando seus cortes
  e origens forem diferentes.

## Teste unitário

Executado:

```text
python -m unittest tests.test_previsao_selecao_dezenas -v
```

Resultado: horizonte confirmado como parte da assinatura reproduzível.

## PostgreSQL efêmero

Executado:

```text
python -m tests.validar_previsao_selecao_dezenas
```

O ensaio copiou os resultados 1 a 505 para um database temporário e emitiu,
com corte 505, previsões para 506 e 507. A repetição não criou outra execução
nem outros alvos. Depois foi inserido o resultado 506:

- a previsão antiga do 506 passou de `PENDENTE` para `AVALIADO`;
- suas dezenas retornadas permaneceram idênticas;
- surgiu uma nova execução com corte 506 para os alvos 507 e 508;
- o alvo 507 passou a possuir duas previsões preservadas, uma para cada corte.

O database temporário foi removido ao final. Nenhuma previsão foi gravada no
banco local persistente.

## Regressão

Executado:

```text
python -m unittest discover -s tests -p "test_*.py"
```

Resultado: **654 testes aprovados**. Permaneceram apenas três avisos
preexistentes de arquivos do Screener abertos durante testes.
