# Evidência da Etapa 25.5 — relatório gráfico temporário

Data: 09/11/2026.

## Implementação

Foi acrescentado à página de Seleção de dezenas um relatório experimental e
paralelo ao backtest persistente. Ele usa somente uma configuração salva,
solicita a prévia e a confirmação do usuário e consome a API temporária criada
na Etapa 25.4.

O relatório permanece apenas na memória do servidor e na página aberta. O
usuário pode descartá-lo explicitamente, e a página também solicita o descarte
ao ser encerrada.

## Gráfico de quantidade de dezenas

- eixo horizontal compartilhado com o gráfico de acertos;
- linhas verticais e rótulos somente nos concursos múltiplos de 100;
- todos os concursos participam do traçado, embora não recebam linha de grade;
- eixo vertical determinado pela menor e pela maior quantidade retornada;
- somente os limites horizontais mínimo e máximo ficam destacados;
- altura compacta de 190 unidades.

## Gráfico de acertos

- mesmo alinhamento horizontal e mesmos pontos por concurso;
- escala vertical exclusiva de 0 a 6;
- sete linhas horizontais finas;
- classes 0, 1, 2 e 3 em vermelho;
- classes 4, 5 e 6 em verde;
- altura de 300 unidades, maior que a do gráfico superior.

## Quadro-resumo

O quadro apresenta período, testes efetuados, menor e maior quantidade de
dezenas, média de dezenas, média de acertos, quantidade nas classes 4 a 6 e a
distribuição exclusiva de 0 a 6 com quantidade e percentual.

## Validação automatizada

Comando:

```powershell
npm run test:frontend
```

Resultado: 89 testes aprovados. Os testes específicos confirmam o alinhamento,
as marcações somente de 100 em 100, os limites mínimo e máximo, os sete níveis
de acerto e a rejeição de séries inválidas.

Comando:

```powershell
npx playwright test frontend/tests/browser/selecao_dezenas.spec.mjs
```

Resultado: 5 testes aprovados. O novo teste abre a prévia, confirma o cálculo,
recebe o relatório temporário, verifica os dois gráficos e o quadro-resumo e
descarta o resultado sem usar o fluxo persistente.

## Conclusão

Os dois gráficos e o quadro-resumo estão disponíveis como experiência paralela.
O backtest persistente atual foi preservado e ainda não foi substituído.
