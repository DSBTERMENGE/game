# Evidência da subetapa 30.3.1 — Capacidades opcionais do CRUD

Data: 12/11/2026

## Alterações

- operações básicas `listar`, `criar` e `atualizar` continuam obrigatórias;
- `arquivar` e `desarquivar` somente são exigidas quando o cadastro usa
  arquivamento;
- `excluir` somente é exigida quando o cadastro usa exclusão definitiva;
- arquivamento e exclusão definitiva são mutuamente exclusivos;
- a ação de exclusão possui confirmação própria antes de chamar o adaptador;
- o identificador enviado ao adaptador pode ser definido pelo cadastro;
- controles de arquivamento e exclusão somente aparecem quando aplicáveis.

## Compatibilidade

Gestão do desenvolvimento continuou usando arquivamento com o mesmo adaptador e
o mesmo comportamento. Grupo e Subgrupo ainda não foram conectados ao
componente nesta subetapa.

## Validação

- 18 testes direcionados do CRUD e de Gestão do desenvolvimento aprovados;
- 117 testes unitários do frontend aprovados;
- verificação de cadastro sem arquivamento nem exclusão aprovada;
- verificação da exclusão por identificador configurado aprovada;
- verificação de incompatibilidade entre arquivamento e exclusão aprovada.
