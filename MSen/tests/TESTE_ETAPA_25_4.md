# Evidência da Etapa 25.4 — API temporária

Data: 09/11/2026.

## Implementação

Foram adicionadas rotas paralelas para:

- preparar a prévia;
- iniciar cálculo assíncrono;
- consultar progresso e resultado;
- cancelar com segurança;
- descartar o relatório da memória.

As rotas persistentes antigas continuam intactas e a página ainda não utiliza
o novo contrato.

## Ciclo de vida

- o identificador é UUID temporário, não chave de banco;
- somente a execução mais recente permanece no processo;
- uma nova execução elimina o relatório terminal anterior;
- `DELETE` elimina explicitamente relatório concluído, cancelado ou falho;
- relatório em andamento precisa ser cancelado ou concluído antes do descarte;
- cancelamento descarta qualquer resultado parcial;
- reiniciar o servidor elimina naturalmente todos os relatórios temporários.

## Contrato de entrada

A prévia e o início recebem exatamente:

```json
{
  "id_configuracao_selecao": 2,
  "concurso_inicial": 500,
  "concurso_final": 3069
}
```

Configurações não salvas, IDs inválidos, campos desconhecidos e períodos
invertidos são rejeitados.

## Testes unitários

Comando:

```powershell
$env:PYTHONPATH='src'
python -B -m unittest discover -s tests -p test_api_selecao_dezenas.py -v
```

Resultado: 18 testes aprovados. Foram cobertos prévia, início, consulta,
validação de entrada, substituição do relatório anterior e descarte explícito,
além da regressão das rotas antigas.

## Validação HTTP integrada

Comando:

```powershell
$env:PYTHONPATH='src'
python -B tests/validar_api_backtest_temporario.py
```

Resultado:

- prévia sem gravação;
- 2.570 pontos retornados para o período 500 a 3.069;
- estado final `CONCLUIDA`;
- duração total HTTP observada de aproximadamente 6,34 segundos;
- cancelamento concluído como `CANCELADA`;
- resultado cancelado igual a `null`;
- descarte confirmado por HTTP 204 e consulta posterior HTTP 404;
- cardinalidades do banco idênticas antes e depois.

## Conclusão

A API temporária disponibiliza o motor da Etapa 25.3 sem persistir resultados e
sem alterar o caminho atualmente usado pela interface.
