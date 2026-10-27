# Contrato do cadastro e da análise de padrões

## Situação do documento

- Item do plano: 9.1.
- Estado: concluído em 2026-10-26.
- Escopo: contrato funcional e de dados; nenhuma tabela ou função detectora é
  criada por este documento.

## 1. Finalidades distintas

Cada padrão será reconhecido por uma função Python própria e documentada. A
detecção terá duas utilizações, sem misturar suas responsabilidades:

1. **Combinação candidata:** responder somente `sim` ou `não` para indicar se a
   combinação corresponde ao padrão.
2. **Resultado histórico:** aplicar a mesma detecção aos resultados ocorridos e
   produzir informações estatísticas sobre a presença do padrão.

O screener será desenvolvido posteriormente. Ele funcionará como funil: ao
primeiro padrão correspondente, contabilizará a exclusão e saltará para a
próxima combinação.

## 2. Tabela `padroes`

Campos aprovados conceitualmente:

| Campo | Finalidade | Origem |
|---|---|---|
| `id_padrao` | Chave interna do banco | banco de dados |
| `padrao_cod` | Referência estável, como `PD_001` | sistema |
| `padrao_nome` | Nome curto, como `Duas dezenas sequenciais` | usuário |
| `padrao_descr` | Explicação detalhada da regra | usuário |
| `num_oco` | Quantidade de resultados que possuem o padrão | cálculo Python |
| `intervalo_medio` | Média dos intervalos entre ocorrências | cálculo Python |
| `desv_padrao` | Desvio-padrão dos intervalos | cálculo Python |

Os tipos, tamanhos e restrições SQL definitivos serão materializados e testados
no Item 9.2, sem acrescentar novas informações funcionais à tabela.

## 3. Identificação e vínculo com Python

`padrao_cod` será único, gerado no formato `PD_001`, `PD_002` e assim por
diante. Ele não poderá ser editado nem reutilizado depois da criação, pois será
a chave de associação com o detector Python.

Exemplo conceitual:

```text
PD_001 -> detectar_duas_dezenas_sequenciais
```

O vínculo será mantido por um registro explícito no módulo Python; descrições e
nomes editáveis nunca serão usados para localizar funções.

Um cadastro novo ainda sem detector poderá servir como especificação de uma
ideia, mas não produzirá estatísticas nem participará do screener. A API deverá
informar claramente que a função está pendente. Todo padrão operacional terá
obrigatoriamente detector implementado e testado. Essa situação será calculada
pelo Python e não exigirá uma coluna adicional em `padroes`.

## 4. Permissões da grade CRUD

Campos editáveis pelo usuário:

- `padrao_nome`;
- `padrao_descr`.

Campos somente para leitura:

- `id_padrao`;
- `padrao_cod`;
- `num_oco`;
- `intervalo_medio`;
- `desv_padrao`.

A inclusão criará um registro e seu código; a exclusão exigirá confirmação. A
grade terá cabeçalho fixo, rolagem vertical e rolagem horizontal quando
necessária. A proteção dos campos calculados existirá tanto no navegador quanto
na API: valores enviados pelo usuário não substituirão cálculos do servidor.

Uma exclusão é respeitada pelos recálculos seguintes: o cadastro não será
recriado automaticamente só porque sua função Python continua disponível. Um
novo padrão receberá o próximo código da sequência, sem reaproveitar o código
excluído.

## 5. Estatísticas históricas

Uma ocorrência significa um resultado histórico que corresponde ao padrão. Um
mesmo concurso acrescentará no máximo uma ocorrência ao padrão, mesmo que nele
existam vários grupos que satisfaçam a mesma regra.

Os concursos correspondentes serão ordenados por `numero_ap`. Cada intervalo
será a diferença entre dois números de apresentação consecutivos. Exemplo:
ocorrências nos concursos 35 e 50 produzem intervalo 15.

- nenhuma ou uma ocorrência: `intervalo_medio` e `desv_padrao` ficam nulos;
- duas ocorrências: existe um intervalo, sua média é o próprio intervalo e o
  desvio-padrão populacional é zero;
- três ou mais ocorrências: média e desvio-padrão populacional são calculados
  sobre todos os intervalos observados;
- resultados decimais serão armazenados com seis casas, seguindo a convenção já
  usada no projeto.

As estatísticas serão recalculadas pelo Python após operações que alterem os
resultados históricos. Elas não serão digitadas nem aceitas como verdadeiras a
partir do frontend.

## 6. Padrões iniciais em estudo

- `PD_001`: o maior bloco consecutivo tem exatamente duas dezenas;
- `PD_002`: o maior bloco consecutivo tem exatamente três dezenas;
- `PD_003`: o maior bloco consecutivo tem quatro, cinco ou seis dezenas.

A classificação pelo maior bloco foi aprovada no Item 9.4. Os padrões são
exclusivos: `10, 25, 26, 27, 50, 58` pertence somente ao `PD_002`, por causa do
bloco `25, 26, 27`, e não é contado novamente no `PD_001`. Vários grupos do
mesmo tamanho dentro de um resultado produzem somente uma ocorrência histórica.

## 7. Organização obrigatória do código

O pacote será criado em `MSen/src/msen/padroes/`. Toda função pública terá
docstring em português informando:

- finalidade;
- parâmetros;
- retorno;
- regra aplicada;
- casos-limite relevantes.

Detecção, estatística, persistência, API e funil permanecerão em funções e
módulos separados. Nenhuma função detectora acessará diretamente interface ou
banco de dados.

## 8. Ordem futura do funil

A ordem altera a atribuição das exclusões, pois uma combinação eliminada deixa
de passar pelos padrões seguintes. A ordem será definida antes do screener e
não será inferida por nome ou descrição. Ela não faz parte da tabela aprovada
nesta etapa.
