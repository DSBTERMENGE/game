# Evidência de teste — Item 9.6

Data: 2026-10-26

## API implementada

- `GET /api/padroes`;
- `POST /api/padroes`;
- `PUT /api/padroes/<padrao_cod>`;
- `DELETE /api/padroes/<padrao_cod>`.

Somente nome e descrição são aceitos do usuário. Código, identificador e os
três campos estatísticos são protegidos no servidor. A resposta informa se o
detector Python está implementado.

## Códigos e exclusão

A migração `003_inicializar_catalogo_padroes.sql` registra os três padrões
iniciais e cria `padroes_codigo_seq`. O teste PostgreSQL confirmou:

- primeiro cadastro novo com código `PD_004`;
- edição de nome e descrição;
- exclusão de `PD_004`;
- cadastro seguinte com `PD_005`, sem reutilização;
- exclusão de padrão implementado respeitada pelo recálculo;
- padrão sem detector mantido com estatísticas nulas.

## Testes da API

Foram cobertos listagem, criação, edição, exclusão, serialização decimal,
detector pendente, campos protegidos, JSON e textos inválidos, código inválido,
duplicidade, ausência e erro seguro do banco.

## Validação local

- migração `003` aplicada ao `games` local;
- `GET /api/padroes` real retornou `200`;
- `PD_001`, `PD_002` e `PD_003` retornaram suas contagens e detector disponível;
- nenhuma operação mutável da API foi executada no banco persistente;
- 10 testes específicos da API aprovados;
- 174 testes Python acumulados aprovados;
- 2 fluxos Chrome/PostgreSQL aprovados em 8,5 segundos;
- nenhum database ou servidor temporário permaneceu;
- PythonAnywhere não foi acessado.

## Conclusão

O CRUD HTTP está funcional, validado e documentado. O Item 9.6 está concluído.
