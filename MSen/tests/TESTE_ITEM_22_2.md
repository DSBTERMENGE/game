# Teste da subetapa 22.2 — configuração reproduzível

Data: 2026-10-30.

## Escopo

- configuração inicial do estudo de frequência;
- tipagem explícita de método, unidade e arredondamento;
- assinatura SHA-256 determinística;
- comparação campo a campo;
- persistência de linha ativa única;
- rejeição de configuração ambígua e de assinatura divergente.

## Configuração inicial

```text
nome: Estudo acumulado inicial
concurso inicial: 1
tamanho inicial: 500
janela: INICIO_FIXO_FINAL_EXPANSIVO
eventos: TODOS
faixa: MEDIA_MAIS_MENOS_DESVIO_PADRAO
parâmetro: 1.000000
unidade: MULTIPLICADOR_DESVIO_PADRAO
arredondamento: LIMITES_EXTERNOS
versão: 1
SHA-256: a24e8a50eff1957fffcbbc923314e33c852a4333322e2b3d57c58e0b6aeb941f
```

O JSON canônico inclui todos os campos capazes de alterar o resultado. O
repositório recalcula a assinatura na leitura e recusa divergência.

## PostgreSQL efêmero

Executado:

```text
python -m tests.validar_configuracao_frequencia
```

Foram confirmados:

- aplicação única da migração 018 e repetição idempotente;
- semente igual à configuração produzida pelo Python;
- comparação legível de nome, tamanho e parâmetro divergentes;
- substituição da linha ativa com nova assinatura correta;
- rejeição de `PERCENTUAL` como unidade não autorizada nesta etapa;
- detecção de assinatura válida em formato, mas incompatível com o conteúdo.

O database efêmero foi removido. O database persistente `games` não foi
alterado.

## Regressão

```text
python -m unittest discover -s tests -p "test_*.py"
```

Resultado: **590 testes aprovados**. Permaneceram somente avisos preexistentes
de arquivos abertos nos testes do Screener.
