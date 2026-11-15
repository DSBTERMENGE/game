# Evidência da subetapa 30.4.3 — Integração do cadastro de Padrões

Data: 12/11/2026

## Ambiente

- aplicação Flask real iniciada em porta isolada;
- banco PostgreSQL temporário criado exclusivamente para o teste;
- banco efetivo do Game não utilizado para gravações;
- banco temporário removido ao término da execução.

## Fluxo validado

1. o comando `Novo registro` permanece indisponível antes da escolha do Grupo;
2. a escolha do Grupo carrega somente seus Padrões;
3. um Padrão temporário é criado pelo formulário e pela confirmação;
4. o registro salvo contém o `id_grupo` correspondente ao Grupo escolhido;
5. a descrição é alterada sem perder o relacionamento;
6. o Padrão é excluído após confirmação;
7. a consulta final confirma que o registro temporário não permanece no banco.

## Resultados

- um teste integrado Playwright aprovado;
- 34 testes de API e repositório de Grupos e Padrões aprovados;
- nenhuma alteração realizada no banco efetivo do Game.
