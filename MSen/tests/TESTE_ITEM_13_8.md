# Evidência do Item 13.8 — configuração visual persistente

Data: 2026-10-27.

Foi criado um botão compacto `Aparência` no painel. Ele abre um diálogo modal,
sem ocupar altura permanente, com configuração de:

- cores da linha, fechamento, vértices, resultado, média, CG e regiões;
- espessura das linhas em milímetros;
- diâmetro dos vértices em milímetros;
- transparência das regiões;
- visibilidade independente dos sete elementos;
- restauração dos valores padrão.

As preferências validadas são armazenadas em `localStorage` sob uma chave
versionada e reaplicadas automaticamente ao carregar a página. Valores ausentes,
corrompidos ou fora dos limites voltam para padrões seguros. A configuração é
local ao navegador e não depende do PostgreSQL.

O teste real do Chrome detectou que a transparência padrão `0,12` não era
compatível com o passo inicial `0,05`, impedindo o envio nativo do formulário.
O passo foi corrigido para `0,01` e a persistência após recarregar passou.

Validações finais:

- 250 testes Python;
- 24 testes de frontend;
- 9 fluxos reais no Google Chrome, incluindo persistência e restauração;
- configurações aplicadas às variáveis CSS e ao desenho condicional;
- nenhum banco de dados acessado ou alterado.

O servidor local não foi reiniciado e PythonAnywhere não foi alterado.
