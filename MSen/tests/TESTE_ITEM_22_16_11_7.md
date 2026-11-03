# Evidência — subetapa 22.16.11.7

Data: 2026-11-02

## Servidor

- Instância anterior encerrada: PID 24932.
- Nova instância Flask: PID 18760.
- Único listener TCP do Game: `127.0.0.1:5050`, PID 18760.
- Nenhuma porta adicional foi aberta.
- `graficos-frequencias.html` respondeu HTTP 200.

## API real

Consulta: dezena 17, evento simples, concursos 500–3.069.

- pontos/concursos: 2.570;
- ocorrências no período: 271;
- segmentos: 271;
- primeiro intervalo real: 489–520;
- primeiro trecho visível: 500–520.

A inspeção automatizada adicional da página real no Chrome não retornou saída
conclusiva dentro do tempo inicial e não foi contabilizada como aprovação. A
regressão automatizada anterior permanece em 34 testes Chrome aprovados. A
página real foi liberada para avaliação visual do usuário.
