# Evidência do Item 14.1 — contrato e configuração do screener

Data: 2026-10-27.

## Entregas

- Contrato funcional em `docs/CONTRATO_SCREENER.md`.
- Configuração padrão versionável em `MSen/config/screener.toml`.
- Configuração local em `MSen/config/screener.local.toml`, protegida pelo
  `.gitignore`.
- Leitor TOML com sobreposição local e objeto imutável de configuração.
- Limite obrigatório de 5.000 combinações e semente reproduzível.
- Ordem inicial: padrões históricos, estatísticas e geometria.
- Todos os critérios permanecem desabilitados e nenhuma combinação é gerada.

## Verificações

Os seis testes específicos comprovaram configuração padrão, substituição
local parcial, local opcional, rejeição de limite diferente de 5.000, bloqueio
de critério prematuro e rejeição da ordem incompleta.

A regressão Python completa executou 260 testes, todos aprovados. Banco de
dados, servidor e PythonAnywhere não foram modificados.
