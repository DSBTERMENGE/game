# Evidência da Etapa 25.3 — motor temporário em memória

Data: 09/11/2026.

## Escopo

- implementar fonte de dados em fluxo;
- executar o backtest em transação PostgreSQL `READ ONLY`;
- manter somente um corte estatístico por vez;
- produzir um trio temporário por concurso;
- consolidar as classes 0 a 6 e as médias;
- permitir progresso e cancelamento;
- não criar API, tela ou persistência.

## Componentes

- `msen.database.fonte_backtest_temporario_repository`;
- `msen.services.backtest_temporario_selecao_dezenas`;
- `tests/test_backtest_temporario_selecao_dezenas.py`;
- `tests/validar_backtest_temporario_selecao_dezenas.py`.

O motor antigo não foi modificado e continua sendo o caminho utilizado pela API
e pela página atuais.

## Validação integrada

Comando executado no banco local `games`:

```powershell
$env:PYTHONPATH='src'
python -B tests/validar_backtest_temporario_selecao_dezenas.py
```

Resultado observado para a configuração salva de ID 2:

| Informação | Resultado |
|---|---:|
| Período | 500 a 3069 |
| Pontos temporários | 2.570 |
| Menor seleção | 40 |
| Maior seleção | 59 |
| Média de dezenas | 52,157977 |
| Média de acertos | 5,235019 |
| Classe 0 | 0 |
| Classe 1 | 0 |
| Classe 2 | 2 |
| Classe 3 | 67 |
| Classe 4 | 353 |
| Classe 5 | 1.051 |
| Classe 6 | 1.097 |
| Classes somadas | 2.570 |
| Concursos nas classes 4, 5 ou 6 | 2.501 |
| Duração do motor | aproximadamente 5,21 s |

Esses números descrevem somente a configuração usada na validação e não
representam promessa de desempenho futuro.

## Ausência de persistência

Antes e depois da execução foram comparadas as cardinalidades de:

- configurações;
- resultados;
- execuções de pesquisa;
- alvos de pesquisa;
- avaliações individuais.

Todas permaneceram inalteradas. O PostgreSQL também protege toda a execução com
`SET TRANSACTION READ ONLY`.

## Cancelamento

Uma segunda execução de 500 a 510 recebeu cancelamento antes do primeiro alvo.
O motor retornou `BACKTEST_CANCELADO`, descartou o relatório incompleto e as
cardinalidades permaneceram inalteradas.

## Memória e isolamento temporal

- fotografias são lidas por cursor de servidor;
- cada grupo contém somente as 60 estatísticas do corte corrente;
- o resultado-alvo é entregue por fluxo ordenado;
- a seleção é calculada antes de o serviço consumir o resultado correspondente;
- avaliações individuais são liberadas depois de formar o ponto;
- permanecem no relatório somente concurso, quantidade de dezenas e acertos;
- o corte 499 é reconstruído pela fonte histórica já existente;
- os demais cortes usam as fotografias persistidas do módulo de frequências.

## Testes automatizados adicionados

O arquivo `test_backtest_temporario_selecao_dezenas.py` verifica:

- exclusividade e soma das classes;
- mínimo, máximo e médias;
- classes premiadas;
- rejeição de relatório vazio;
- rejeição de quantidade de acertos fora de 0 a 6.

A instalação Python disponível nesta sessão não contém `pytest`; por isso, a
suíte completa não foi executada. Os módulos foram importados e exercitados
pelo validador integrado completo com sucesso.

## Conclusão

O motor paralelo está implementado, reproduzível em memória, cancelável e
tecnicamente impedido de escrever. API e interface continuam fora desta etapa.
