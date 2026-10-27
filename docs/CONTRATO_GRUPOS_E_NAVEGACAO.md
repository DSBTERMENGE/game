# Contrato de grupos de padrões e navegação compacta

## Situação do documento

- Item do plano: 10.1.
- Estado: concluído em 2026-10-27.
- Escopo: regras funcionais, de dados e de interface. Este item não altera
  banco, API, Python ou frontend.

## 1. Organização conceitual

Os padrões serão organizados em dois níveis:

1. **Grupo de padrões:** reúne padrões que estudam o mesmo conceito.
2. **Padrão:** representa uma regra específica, detectada por uma função Python.

Exemplo:

```text
Dezenas sequenciais
├── Duas dezenas sequenciais
├── Três dezenas sequenciais
└── Mais de três dezenas sequenciais
```

Na interface será usado o termo **Padrões**, mais direto para o usuário. O nome
técnico `padroes_subgrupo` será usado no banco para deixar explícita a relação.

## 2. Tabela `padroes_grupo`

| Campo | Finalidade | Regra de edição |
|---|---|---|
| `id_grupo` | Chave primária interna | somente leitura |
| `grupo_cod` | Código estável, como `PG_001` | gerado pelo sistema |
| `grupo_nome` | Nome curto do conceito | editável |
| `grupo_descr` | Explicação detalhada do grupo | editável |

`grupo_cod` será único, não editável e nunca será reutilizado. A sequência será
independente da sequência de `padrao_cod`.

O nome normalizado, desconsiderando espaços externos e diferenças entre letras
maiúsculas e minúsculas, não poderá se repetir. Assim, `Dezenas sequenciais` e
` dezenas sequenciais ` serão considerados o mesmo nome.

## 3. Tabela `padroes_subgrupo`

A tabela atual `padroes` será renomeada para `padroes_subgrupo` por migração. Os
campos existentes serão preservados e será acrescentado:

| Campo | Finalidade | Regra de edição |
|---|---|---|
| `id_grupo` | Chave estrangeira para `padroes_grupo` | obrigatório e editável |

Continuarão existindo `id_padrao`, `padrao_cod`, `padrao_nome`, `padrao_descr`,
`num_oco`, `intervalo_medio` e `desv_padrao`, com as regras já definidas no
contrato da Etapa 9.

Todo padrão pertencerá a exatamente um grupo. Um grupo poderá possuir nenhum,
um ou vários padrões. O mesmo `padrao_nome`, normalizado como o nome do grupo,
não poderá aparecer duas vezes dentro do mesmo grupo. Nomes iguais em grupos
diferentes serão permitidos, porque podem representar contextos distintos.

O grupo será uma classificação conceitual. As estatísticas continuarão
pertencendo aos padrões específicos e não serão somadas nem armazenadas no
grupo.

## 4. Integridade e exclusões

- não será permitido cadastrar padrão sem grupo válido;
- não será permitido excluir um grupo que possua padrões;
- a interface informará que os padrões devem ser transferidos ou excluídos
  antes da exclusão do grupo;
- excluir um padrão continuará exigindo confirmação;
- uma migração nunca apagará padrões ou estatísticas existentes;
- códigos excluídos não serão reaproveitados.

A restrição da chave estrangeira será a proteção definitiva. A API repetirá a
validação para apresentar mensagem compreensível ao usuário.

## 5. Migração dos dados existentes

A migração criará os grupos iniciais:

```text
PG_001 — Dezenas sequenciais
PG_002 — Dezenas na mesma coluna
```

Os padrões `PD_001` a `PD_003` serão associados a `PG_001`. Os padrões
`PD_004` a `PD_006`, encontrados no cadastro local antes da migração, serão
associados a `PG_002`. Identificadores, códigos, textos e estatísticas serão
preservados. Se existir outro padrão ainda sem classificação aprovada, a
migração será interrompida em vez de associá-lo silenciosamente ao grupo errado.

## 6. Navegação em uma linha

A aplicação usará uma única barra horizontal permanente:

```text
[← Voltar] [Painel] [Cadastros ▾]                         [Página atual]
```

- **Painel:** exibirá a funcionalidade atual de resultados e gráficos.
- **Cadastros:** abrirá submenu flutuante, sem criar uma segunda linha.
- **Grupos de padrões:** abrirá o CRUD de grupos.
- **Padrões:** abrirá o CRUD de padrões vinculados aos grupos.
- **Voltar:** retornará ao nível anterior da aplicação; quando não houver nível
  interno, ficará desabilitado ou oculto sem reservar uma linha.

Não serão usados menu lateral, cartões grandes de navegação ou títulos que
criem cabeçalhos verticais adicionais. O submenu ocupará espaço apenas enquanto
estiver aberto.

## 7. Aproveitamento do espaço

- título da página e ações como **Novo** ficarão na mesma linha sempre que a
  largura permitir;
- tabelas usarão a área útil disponível e terão cabeçalho fixo;
- colunas numéricas e de ações terão largura reduzida;
- nome e descrição receberão o espaço restante;
- a rolagem horizontal ficará contida na grade, sem alargar a página;
- a rolagem vertical ocorrerá dentro da grade quando isso preservar o menu;
- campos calculados permanecerão compactos e somente para leitura;
- em telas estreitas, controles poderão se reorganizar apenas quando não
  couberem com legibilidade em uma linha.

## 8. Separação técnica

As páginas poderão compartilhar a mesma barra de navegação, mas HTML, CSS e
JavaScript continuarão em arquivos separados por responsabilidade. Banco,
repositório, serviço, API e interface não serão misturados.

Toda função Python pública nova continuará exigindo docstring em português com
finalidade, parâmetros, retorno e regras relevantes.

## 9. Critérios para as próximas subetapas

- migração validada primeiro em PostgreSQL temporário;
- aplicação no `games` somente após o teste isolado;
- testes direcionados após cada pequena mudança;
- regressão completa apenas nos marcos previstos;
- nenhuma alteração no PythonAnywhere durante a Etapa 10;
- cada subetapa dependerá de autorização expressa.
