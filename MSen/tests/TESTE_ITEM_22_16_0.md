# Evidência da subetapa 22.16.0

## Finalidade

Definir, antes da implementação, o contrato da página auxiliar destinada à
leitura ampliada dos gráficos de evolução histórica por dezena.

## Contrato aprovado

1. O ponto de partida é o bloco `Evolução histórica por dezena` da página
   `Frequência das dezenas`.
2. `Abrir gráficos` conduz a uma página auxiliar, não a um modal.
3. `Voltar para Frequência das dezenas` retorna ao mesmo bloco e preserva
   dezena, evento e período selecionados.
4. Os dois gráficos ficam em linhas separadas, usando a largura da página e
   altura suficiente para leitura.
5. O eixo horizontal continua linear e representa concursos.
6. A escala vertical oferece modo automático e zoom visual de 10×, sem
   multiplicar valores nem modificar dados ou cálculos.
7. Eventual recorte causado pelo zoom deve ser informado e reversível.
8. A página utiliza a API e a geração existentes; não grava configuração nem
   altera o banco.

## Limites desta subetapa

Foram alterados somente documentos de planejamento e decisão. Não foram
criados página, botões, escalas ou testes de interface, e nenhum dado foi
processado ou gravado.
