# Evidência da etapa 31.3 — Primeira fase experimental do Polígono 2

Data: 12/11/2026

## Método experimental

Para cada uma das seis dezenas, as cinco ligações possíveis são ordenadas por
ângulo. Conservam-se as duas ligações que delimitam o maior setor angular vazio,
representando as extremidades vistas a partir daquela dezena. A união das
escolhas individuais forma o conjunto de arestas candidatas após a primeira
eliminação das ligações internas.

O diagnóstico informa, sem corrigir automaticamente:

- arestas restantes;
- grau de cada dezena;
- duas escolhas feitas a partir de cada dezena;
- quantidade total de arestas;
- conectividade das seis dezenas;
- existência de cruzamentos;
- atendimento ou não ao circuito final de seis arestas.

## Leitura dos resultados atuais

Foram consultados, sem gravação, os 3.069 resultados existentes:

| Situação | Arestas | Concursos | Exemplo |
| --- | ---: | ---: | --- |
| circuito pronto | 6 | 379 | concurso 6 |
| excedente | 7 | 1.540 | concurso 1 |
| excedente | 8 | 1.041 | concurso 2 |
| excedente | 9 | 109 | concurso 12 |

Exemplos para a observação posterior no Painel:

- concurso 1: graus 3, 2, 2, 2, 3 e 2; sete arestas, conectado e sem
  cruzamento;
- concurso 2: graus 2, 2, 2, 3, 3 e 4; oito arestas, conectado e com
  cruzamento;
- concurso 12: graus 4, 2, 3, 4, 2 e 3; nove arestas, conectado e sem
  cruzamento;
- concurso 6: seis arestas, grau dois em todas as dezenas, conectado e sem
  cruzamento.

## Validação

- quatro testes novos e 33 testes geométricos existentes aprovados;
- resultado independente da ordem de entrada das dezenas;
- validação das seis dezenas reutilizada do motor geométrico existente;
- nenhuma regra de eliminação dos excedentes implementada;
- nenhuma API, interface, tabela ou linha do banco foi alterada.
