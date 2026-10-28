# Teste da subetapa 17.3 — perfil estatístico genérico

## Série de referência

Foi usada a série `2, 4, 4, 4, 5, 5, 7, 9`, cujo cálculo manual conhecido é:

- quantidade: 8;
- média: 5;
- variância populacional: 4;
- desvio-padrão populacional: 2;
- mínimo: 2;
- máximo: 9.

## Casos automatizados

1. reconciliação das medidas com os valores manuais;
2. distribuição empírica fechando 8 registros e 100%;
3. faixa percentual assimétrica de -10% a +20%;
4. faixa assimétrica de -1 a +2 desvios;
5. série constante com desvio zero;
6. média negativa sem inversão dos limites percentuais;
7. rejeição de série vazia, tipos inválidos e número não finito;
8. rejeição de margem negativa e perfil inválido.

## Resultado

- 8 testes específicos aprovados.
- 430 testes Python de regressão aprovados.
- Foram emitidos somente avisos preexistentes sobre três arquivos do screener
  não fechados por um teste; nenhum teste falhou.
- Banco, API, interface e regras do screener permaneceram inalterados.
