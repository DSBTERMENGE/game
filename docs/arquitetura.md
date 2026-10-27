# Arquitetura

O projeto começa como um pacote Python instalado a partir do diretório `src`.
Essa organização evita que os testes importem acidentalmente arquivos locais
que não fariam parte de uma instalação real.

## Componentes atuais

- `msen.main`: ponto de entrada da aplicação;
- `dados`: arquivos de entrada e recursos visuais;
- `tests`: testes automatizados com pytest;
- `frontend/index.html`: ponto de entrada da interface;
- `frontend/css`: folhas de estilo;
- `frontend/js`: comportamento JavaScript da interface.

A fábrica Flask serve a API e o diretório `frontend` na mesma origem. A rota
`/` entrega o HTML, `/css` e `/js` entregam os recursos estáticos e `/api`
concentra as operações de dados. Isso evita configuração CORS e reproduz no
teste local o fluxo que será usado por uma aplicação WSGI.

O Cadastro de Padrões mantém responsabilidades separadas:

- `frontend/index.html`: estrutura da grade e do formulário;
- `frontend/css/padroes.css`: janela, tabela, cabeçalho fixo e rolagem;
- `frontend/js/padroes.js`: consumo da API e operações CRUD;
- `msen/api/padroes.py`: validação HTTP e proteção dos campos calculados;
- `msen/database/padroes_repository.py`: SQL do cadastro.

Novos módulos devem ser criados por responsabilidade, por exemplo `leitura`,
`modelos`, `analises` e `relatorios`, quando essas necessidades surgirem.
