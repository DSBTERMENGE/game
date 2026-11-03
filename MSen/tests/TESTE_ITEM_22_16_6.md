# Teste do item 22.16.6 — Intervalos individuais observados

Data: 2026-10-31

## Objetivo

Confirmar que o gráfico de evolução apresenta os valores individuais que
originam as curvas acumuladas de intervalo mínimo, médio e máximo.

## Regra verificada

- Cada ponto usa no eixo X o concurso em que o evento voltou a ocorrer.
- O eixo Y usa `concurso atual - concurso anterior`.
- Um evento dentro do período conserva seu intervalo mesmo quando o evento
  anterior está antes do concurso inicial consultado.
- A regra vale para `SIMPLES`, `2VS` e `3VS`.
- Os pontos são apenas derivados na consulta; não alteram o histórico gravado.

## Cobertura

- Integração PostgreSQL verifica os três tipos de evento e o vínculo entre
  concurso anterior, atual e intervalo.
- Testes estáticos verificam API, legenda e camada visual dos pontos.
- Fluxo Chrome confirma dois pontos individuais, tooltip e ausência de
  coordenadas inválidas no gráfico auxiliar.

## Resultado

- 56 testes JavaScript aprovados.
- 10 fluxos Chrome do módulo aprovados, incluindo pontos, tooltip,
  responsividade e ausência de coordenadas inválidas.
- Validação PostgreSQL aprovada para fotografia, séries `SIMPLES`, `2VS` e
  `3VS`, incluindo os intervalos individuais.
- Após autorização específica, as duas instâncias encontradas na porta 5050
  foram encerradas e substituídas por uma única instância, PID 30540.
- A página real respondeu HTTP 200. Para a dezena 17, evento `SIMPLES`, cortes
  500–3.069, a API retornou 2.570 fotografias, 271 ocorrências e 271 intervalos
  visíveis. O ponto do concurso 641 confirmou o intervalo 60 desde o concurso
  581.
