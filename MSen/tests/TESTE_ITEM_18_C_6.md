# Teste da subetapa 18-C.6 — configuração do limite de raridade

Data: 2026-10-29

## Objetivo

Substituir o valor de 10% escrito diretamente no ensaio da Etapa 18 por uma
configuração única, validada e fotografada no início de cada execução.

## Implementação

- `config/screener.toml` passou a declarar
  `raridade.limite_percentual = 10.0`.
- `ConfiguracaoScreener` mantém o limite como `Decimal`, normalizado para seis
  casas decimais.
- O intervalo permitido é de 0% a 100%; booleanos, textos não numéricos,
  números não finitos e valores fora do intervalo são recusados.
- `screener.local.toml`, quando existir, pode substituir apenas esse valor sem
  modificar o arquivo versionado.
- O ensaio extensível deixou de enviar `Decimal(10)` diretamente ao perfil de
  padrões e passou a usar o valor da configuração.
- A explicação do ensaio também apresenta o valor efetivamente configurado.

## Fotografia da execução

O formato 2 da fotografia registra:

- data da fotografia;
- limite percentual utilizado;
- operador estrito `<`;
- concursos e datas inicial e final do histórico;
- denominador histórico;
- frequências utilizadas;
- padrões selecionados como excludentes;
- versões dos cálculos;
- checksum SHA-256 do conteúdo canônico.

Uma nova configuração pode mudar a seleção de uma execução posterior, mas não
altera a fotografia já construída para uma execução anterior.

## Testes

- carregamento do limite padrão de 10%;
- substituição local por 3,25%;
- recusa de -0,1%, 100,1% e texto não numérico;
- presença da data, limite, operador, intervalo e versões na fotografia;
- recusa de data com horário;
- seleção diferente após mudança do limite, preservando a fotografia anterior;
- regressão completa: 500 testes Python aprovados.

Os `ResourceWarning` já existentes nos testes que abrem arquivos do frontend
continuam sem causar falhas.

## Resultado

Subetapa 18-C.6 aprovada tecnicamente. O banco de dados não foi alterado.
