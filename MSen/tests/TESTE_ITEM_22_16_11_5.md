# Evidência — subetapa 22.16.11.5

Data: 2026-11-02

## Base real

O validador somente de leitura `validar_grafico_intervalos.py` conferiu a
geração ativa:

- Dezena 08: 264 segmentos; primeiro intervalo 495–504 recortado em 500;
  ocorrências de intervalos 1/2/3/10: 28/21/16/15; 9 pares consecutivos iguais;
  maior intervalo 46.
- Dezena 17: 271 segmentos; primeiro intervalo 489–520 recortado em 500;
  ocorrências de intervalos 1/2/3/10: 26/22/21/18; 18 pares consecutivos iguais;
  maior intervalo 60.
- Cada intervalo foi recalculado pela diferença entre seus concursos.
- A média armazenada no concurso 500 coincidiu com o recálculo independente
  dos intervalos concluídos até esse concurso.

## Validação visual automatizada

- Casos de 1, 2, 3 e 10 concursos ficaram abaixo do limiar de 8 pixels na visão
  integral e receberam indicação de intervalo curto.
- O caso de 40 concursos permaneceu como patamar visível normal.
- Nenhum caminho produziu coordenada inválida.

## Regressão

```text
29 testes Python aprovados
60 testes JavaScript aprovados
34 testes de navegador aprovados no Chrome
```
