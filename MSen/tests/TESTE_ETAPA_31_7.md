# Evidência da etapa 31.7 — Voo e camadas geométricas

Data: 12/11/2026

## Integração realizada

O quadro Voo dos pássaros recebeu quatro seleções independentes:

- Média espacial;
- Linha Poligonal;
- Polígono 1;
- Polígono 2.

Cada alteração redesenha imediatamente o concurso atual e o Voo respeita a
mesma seleção ao avançar pelos concursos. As configurações visuais gerais
continuam definindo cores, espessuras e demais propriedades já existentes.

## Polígono 2 e CG2

A consulta geométrica sob demanda passou a fornecer, no mesmo contrato:

- ordem das seis dezenas do circuito;
- seis vértices do Polígono 2;
- área exata convertida para o contrato decimal;
- coordenadas do CG2.

O navegador desenha o contorno do Polígono 2 e o CG2 com identificação visual
própria. O resumo vertical do concurso distingue Área P1 e Área P2 e apresenta
as coordenadas do CG2. O cálculo permanece sob demanda e reutiliza o cache da
combinação, sem criar tabela ou gravação.

## Validação

- 16 testes Python da API e do Polígono 2 aprovados;
- 127 testes unitários do frontend aprovados;
- teste específico confere que as quatro camadas podem ser ocultadas
  individualmente;
- quatro fluxos Chromium aprovados, incluindo desenho, resumo, alternância do
  Polígono 2, aparência, navegação e voo;
- nenhuma tabela ou linha do banco foi alterada.

As médias e os desvios históricos das medidas geométricas exigem a definição da
persistência incremental prevista na validação final; não são simulados nesta
etapa com cálculos repetidos a cada abertura da página.
