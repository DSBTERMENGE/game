# Teste do Item 6.5

Data: 2026-10-26

## Ferramenta

- Playwright 1.64.1;
- Google Chrome instalado no computador;
- execução invisível (`headless`);
- servidor HTTP interno ao teste, encerrado automaticamente;
- API simulada no navegador, sem acesso ou alteração do PostgreSQL.

## Fluxos aprovados

1. carregar resultados, desenhar marcas, selecionar e navegar circularmente;
2. iniciar o voo em 0,1 segundo, avançar e pausar;
3. selecionar uma planilha real de teste, simular a importação HTTP, recarregar
   resultados, desenhar a mancha e limpar todas as marcas.

## Resultado final

```text
3 testes Playwright aprovados em 3,1 segundos
19 testes unitários de frontend aprovados
137 testes Python aprovados
```

O primeiro servidor auxiliar testado não encerrava corretamente seu processo
filho no Windows. Ele foi substituído por um servidor Node.js interno ao teste,
que inicia e fecha no mesmo processo sem deixar porta ou tarefa ativa.

Nenhum navegador adicional foi baixado, nenhum banco foi alterado e o
PythonAnywhere não foi acessado.
