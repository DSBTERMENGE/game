# Teste do Item 16.8 — API do perfil por grupo

Data: 28/10/2026

## Endpoint

Foi criado:

```text
GET /api/grupos-padroes/PG_001/perfil
```

Parâmetros opcionais:

- `limite_raridade`, com padrão 10%;
- `numero_ap_ate`, inclusivo;
- `data_ate`, inclusivo e no formato `AAAA-MM-DD`.

Concurso e data de corte são mutuamente exclusivos. A resposta informa
amostra efetiva, versões, quatro classes, contagens, percentuais, estatísticas
de intervalo e os padrões apenas indicados como raros. O campo
`ativa_no_screener` permanece `false`.

## Testes direcionados

Doze testes da API e do serviço confirmaram:

- contrato JSON e decimais sem conversão imprecisa para `float`;
- limite padrão e limite informado;
- encaminhamento dos dois tipos de corte;
- rejeição de cortes conflitantes e parâmetros desconhecidos;
- validação de limite, concurso, data e código do grupo;
- retorno 404 para grupo ainda sem classificador;
- retorno 409 seguro para classificação incompleta;
- ausência de detalhes internos nas mensagens de erro.

## Integração PostgreSQL temporária

Um clone dos resultados reais foi usado por uma instância Flask isolada:

```text
perfil completo: 3.069 resultados
padrões indicados com 10%: PD_002 e PD_003
numero_ap_ate=100: 100 resultados
data_ate=1998-02-01: 100 resultados
```

O catálogo de `PD_001`–`PD_003` foi fotografado antes e depois das três
requisições. Não houve alteração, comprovando que a API GET e os perfis com
corte são somente leitura.

## Regressão e limpeza

- 410 testes Python: aprovados;
- database temporário removido; auditoria final `[]`;
- database principal `games` e PythonAnywhere não alterados.

Contrato detalhado em `docs/API_PERFIS_PADROES.md`.
