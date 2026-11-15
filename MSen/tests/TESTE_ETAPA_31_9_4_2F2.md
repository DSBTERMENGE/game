# Evidência — subetapa 31.9.4.2F2

Data: 14/11/2026

## Inspeção da aplicação real

Endereço inspecionado: `http://127.0.0.1:5050/`.

O Chrome automatizado abriu o Painel, desativou Dezenas e Média espacial,
ativou somente CG1 e executou o desenho da mancha.

Foram confirmados:

- 3.069 círculos de CG1;
- cor única `#7566d9`;
- um único raio para todos os pontos;
- intensidade mínima igual ou superior ao fator salvo 0,12;
- intensidades maiores na região próxima ao centro;
- um centro amarelo;
- três círculos de referência identificados como CG1;
- três rótulos de referência;
- média do CG1 em `(4.51; 2.50)`;
- faixas com 886, 1.359, 638 e 186 ocorrências;
- frequências `1:3`, `1:2`, `1:5` e `1:17`.

O teste específico da aplicação real passou. A inspeção da captura não revelou
necessidade de ajuste no CG1.

## Observação sobre o ambiente integrado isolado

O servidor criado isoladamente em porta 5051 apresentou apenas um ponto
geométrico de CG1 e também não carregou os registros esperados de Padrões. Como
esse conjunto não corresponde ao servidor real usado pelo usuário, ele não foi
adotado como evidência visual desta subetapa e nenhum código do CG1 foi alterado
para acomodar essa divergência ambiental.
