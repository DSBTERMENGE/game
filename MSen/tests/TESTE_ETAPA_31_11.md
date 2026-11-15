# Teste da etapa 31.11 — Validação final do Painel

Data: 14/11/2026

## Validação integrada no servidor real

O fluxo foi executado em `http://127.0.0.1:5050/` sem importação e sem gravação
no banco. Foram conferidos:

- carregamento de mais de 3.000 resultados;
- seis dezenas e geometria do concurso individual;
- Linha Poligonal, Polígono 1 e Polígono 2;
- centros de gravidade CG1 e CG2;
- avanço e pausa do Voo dos pássaros;
- manchas de Dezenas, Média espacial, CG1, CG2 e Quadrantes;
- 60 frequências no resumo lateral;
- quatro quadrados e dois eixos dos Quadrantes;
- resumos analíticos combinados;
- altura lateral limitada à altura do mapa e largura fixa de 208 px;
- salvamento e recuperação da configuração visual no navegador isolado do
  teste.

## Conferência direta da API

- resultados retornados: 3.069;
- primeiro concurso: 1;
- geometria individual disponível;
- Polígono 2 disponível;
- pontos históricos das manchas: 3.069;
- CG1 e CG2 presentes nos pontos históricos.

## Testes automatizados

- integração real do Painel: aprovada;
- frontend: 163 testes aprovados e nenhuma falha;
- `git diff --check`: aprovado.

A suíte Python foi solicitada, mas o Python disponível na máquina informou
`No module named pytest`. Nenhum pacote foi instalado e nenhum ambiente foi
alterado sem autorização. A API em execução foi validada diretamente e não
apresentou erro.

## Resultado

Aprovado. Nenhuma regressão funcional foi encontrada e a página Painel está
concluída.
