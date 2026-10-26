# Decisão do framework da API

Data: 2026-10-26.

## Escolha

O MSen usará Flask 3.1, com dependência `Flask>=3.1.3,<4`.

## Motivos

- API pequena, com poucas rotas já definidas no plano;
- código e acesso ao PostgreSQL atualmente síncronos;
- cliente de testes HTTP fornecido pelo próprio framework;
- fábrica de aplicação permite configurações independentes;
- integração direta com servidores WSGI e com o PythonAnywhere;
- não exige ORM: o SQL permanece nos repositórios já implementados.

FastAPI não foi escolhido porque seu benefício principal exigiria adotar ASGI e
fluxo assíncrono sem necessidade atual. Django não foi escolhido porque inclui
ORM, administração e outras estruturas além do escopo desta aplicação.

## Organização

- `msen.api.criar_app`: fábrica da aplicação;
- `GET /api/saude`: verificação técnica sem banco;
- `MSen/wsgi.py`: entrada de produção;
- rotas de negócio: adicionadas gradualmente nos Itens 5.2 a 5.4.

Referências oficiais:

- https://flask.palletsprojects.com/en/stable/patterns/appfactories/
- https://flask.palletsprojects.com/en/stable/testing/
- https://help.pythonanywhere.com/pages/Flask
