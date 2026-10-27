# Evidência do Item 13.1 — contrato geométrico

Data: 2026-10-27.

O contrato foi formalizado em `docs/CONTRATO_ANALISE_GEOMETRICA.md` antes da
criação das funções. Foram definidos:

- coordenadas lógicas da matriz 6 por 10;
- ordenação obrigatoriamente crescente das dezenas;
- extensão da linha aberta e perímetro do percurso fechado;
- decomposição dos cruzamentos em regiões fechadas;
- área total como soma positiva das regiões, sem cancelamentos;
- centro de gravidade único, ponderado pelas áreas componentes;
- comportamento de alinhamentos, contatos e sobreposições;
- distinção entre centro de gravidade e média espacial.

Foram preparados quatro casos de referência: figura simples, figura cruzada com
duas regiões, figura de área nula e invariância da ordem de entrada. Os valores
esperados foram definidos em forma exata e aproximada.

Nenhum código de cálculo, tabela ou dado foi criado ou alterado. O banco
`games` e o PythonAnywhere não foram acessados.
