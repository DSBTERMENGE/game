# Interface oficial do Screener

A página `screener.html` consome diretamente o formato serializado do
quadro consolidado. Ela não contém números fictícios. Desde a subetapa 18.8, o
botão chama `POST /api/screener/quadro` para executar exatamente 5.000
combinações.

## Organização

- resumo compacto com universo, amostra, exclusões e aprovações;
- três famílias inicialmente recolhidas;
- expansão individual ou conjunta;
- filtros em tabela com entrada, avaliações, exclusões, dois percentuais e saldo;
- rolagem interna para preservar espaço vertical e horizontal;
- fechamento contábil visível.

Cada filtro exibido é marcado como “Função Python validada”. Isso não significa
geração automática: somente filtros efetivamente presentes no relatório podem
aparecer. Grupos apenas cadastrados, mas sem classificador Python integrado, não
podem entrar na execução.

O botão não recebe quantidade do usuário. A API fixa 5.000 combinações, exige
modo amostral, mantém o processamento integral bloqueado e apresenta a comparação
com o screener anterior sobre a mesma amostra.
