# Evidências do Item 10.12 — compactação visual

Data: 2026-10-27.

## Cenários no Google Chrome

Foram usados catálogos simulados com 30 grupos e 45 padrões para forçar as
rolagens, sem acessar PostgreSQL.

### Janela de 1280 × 720

- barra principal com altura máxima de 46 px;
- submenu aberto sem alterar a altura da barra ou deslocar o conteúdo;
- página sem rolagem horizontal própria;
- grade contida dentro da largura e da altura visíveis;
- mais de 300 px de altura útil para a grade;
- rolagens horizontal e vertical internas confirmadas;
- cabeçalho permaneceu fixo após deslocamento vertical de 500 px.

### Janela de 700 × 600

Nas páginas de grupos e padrões:

- documento não ultrapassou a largura da janela;
- barra de inclusão conservou uma linha com rolagem horizontal própria;
- tabela conservou rolagem horizontal dentro da grade;
- grade permaneceu contida nos limites direito e inferior da janela.

## Regressão direcionada

- 22 testes de frontend: aprovados;
- 8 fluxos no Google Chrome: aprovados;
- `git diff --check`: sem erros.

Nenhum ajuste adicional foi necessário e nenhum banco foi acessado.
