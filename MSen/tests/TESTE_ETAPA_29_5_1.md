# Auditoria da subetapa 29.5.1 — processamento integral

Data: 11/11/2026

## Gargalos confirmados

1. `executar_funil_extensivel` executa `tuple(combinacoes)` antes do laço. No
   universo integral, a tupla externa e cerca de 50 milhões de tuplas internas
   podem ultrapassar 4 GiB antes de considerar o restante da aplicação.
2. `executar_funil_extensivel` e `executar_funil` mantêm uma lista com todas as
   combinações aprovadas. Isso é útil nos testes de 5.000, mas desnecessário no
   relatório integral, que precisa das quantidades acumuladas.
3. O progresso é informado a cada 25 combinações. Uma passagem integral pode
   produzir cerca de dois milhões de atualizações; o relatório comparativo faz
   uma segunda passagem.
4. O gerador já usa `itertools.combinations`, que é preguiçoso, mas a validação
   da configuração e o próprio gerador exigem limite exatamente igual a 5.000.
5. Um iterador integral é consumido na primeira passagem. A comparação, se
   continuar necessária, deverá criar um segundo iterador, nunca reutilizar o
   iterador já esgotado.

## Estimativa inicial

O teste real de 5.000 combinações levou aproximadamente 4,3 segundos incluindo
preparação e duas passagens. Uma extrapolação linear simples ultrapassa 12 horas.
Esse número não é previsão definitiva; a subetapa 29.5.5 deverá medir volumes
maiores porque preparação fixa, contenção e frequência de progresso alteram a
proporção.

## Alterações indispensáveis para 29.5.2

- receber o total esperado separadamente do iterador;
- contabilizar aprovadas sem armazená-las no modo integral;
- manter as combinações aprovadas no modo amostral para preservar os testes;
- comunicar progresso por lotes configuráveis;
- criar um iterador novo para cada passagem;
- manter cancelamento por combinação ou em intervalo suficientemente curto.

Nenhum código, banco ou componente da interface foi alterado nesta auditoria.
