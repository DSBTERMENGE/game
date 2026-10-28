# Teste do Item 16.9 — visualização compacta do perfil

Data: 28/10/2026

## Interface implementada

A página `padroes.html` recebeu o acionador compacto `Perfil PG_001` na mesma
linha do filtro existente. Ao abrir, um painel flutuante é sobreposto à grade:
ele não desloca a tabela, não cria outra linha de navegação e desaparece ao ser
fechado.

O painel contém:

- limite percentual configurável apenas para consulta;
- histórico completo ou corte por concurso/data;
- total da amostra, classificados e sem correspondência;
- padrões indicados abaixo do limite;
- tabela rolável com quatro classes, dois percentuais, intervalo médio,
  desvio-padrão e diagnóstico;
- mensagem explícita de que o screener permanece inativo.

HTML, CSS e JavaScript continuam em arquivos separados. A tabela possui
rolagem horizontal e vertical internas, cabeçalho fixo e destaque visual das
classes abaixo do limite.

## Testes

- 24 testes estáticos/JavaScript: aprovados;
- fluxo específico no Google Chrome: aprovado;
- 12 fluxos completos no Google Chrome: aprovados;
- 410 testes da regressão Python: aprovados.

O teste no Chrome confirmou quatro linhas, resumo de 3.069 resultados,
`PD_002/PD_003` indicados, dois destaques, mensagem de screener inativo,
posicionamento absoluto sem deslocar a grade e envio do corte
`numero_ap_ate=100`.

## Limite operacional

A interface foi validada com a API simulada e a API real já foi validada em
PostgreSQL temporário na subetapa 16.8. Como a migração `008` ainda não foi
aplicada ao database principal `games`, abrir o perfil contra esse database
antes da autorização de aplicação exibirá a mensagem segura de perfil ainda
indisponível. Nenhum banco foi alterado nesta subetapa.
