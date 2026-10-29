# Teste da subetapa 18-C.9 — API e interface do limite de raridade

Data: 2026-10-29

## Objetivo

Permitir configurar o limite percentual do screener sem editar código-fonte,
expor o valor efetivamente usado e informar somente os padrões selecionados.

## API

`POST /api/screener/quadro-extensivel` aceita o corpo:

```json
{"limite_raridade": "7.5"}
```

Regras:

- o campo é opcional; sem ele, usa-se o padrão validado do arquivo de
  configuração;
- aceita valores de 0% a 100%, normalizados para seis casas decimais;
- o operador permanece estritamente `<`;
- campos desconhecidos, JSON malformado e valores inválidos retornam HTTP 400;
- a resposta informa `limite_percentual`, `operador` e
  `padroes_selecionados`;
- a fotografia registra o mesmo limite efetivamente executado.

## Interface

- Foi adicionado um campo numérico compacto para o limite percentual.
- O valor é enviado no corpo JSON da execução.
- Depois da resposta, a tela mostra o limite efetivo e a lista selecionada.
- O último limite válido fica memorizado no navegador.
- Os detalhes continuam mostrando percentuais como informação principal e
  quantidade/denominador como auditoria.

## Validações reais

- Limite 3%: PD_002, PD_003, PD_005 e PD_006 selecionados; PD_009 não entrou
  porque possui 3,030303%.
- Limite 0%: nenhum padrão selecionado; a família recebeu e aprovou as 423
  combinações, sem exclusões e com fechamento válido.
- Limite padrão 10%: PD_002, PD_003, PD_005, PD_006 e PD_009.

## Regressão

- 508 testes Python aprovados;
- 35 testes JavaScript aprovados;
- 18 fluxos completos no Google Chrome aprovados;
- fluxo Chrome específico confirmou envio de 7,5%, exibição de 7,500000% e
  memorização local;
- banco de dados não alterado.

## Resultado

Subetapa 18-C.9 aprovada tecnicamente.
