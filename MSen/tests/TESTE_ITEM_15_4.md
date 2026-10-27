# Evidência do Item 15.4 — casos de aceitação do PD_003

Data: 2026-10-27.

O usuário aprovou os 8 casos positivos, 6 negativos e 6 casos de erro descritos
em `docs/CASOS_ACEITACAO_PD003.md`.

## Regras aprovadas

1. A sequência é numérica e pode atravessar 10/11.
2. Não existe continuidade circular entre 60 e 01.
3. Blocos consecutivos separados não são somados.
4. A classificação considera o maior bloco consecutivo e é exclusiva:
   quatro, cinco ou seis dezenas pertencem somente a PD_003.

Consequentemente:

- `58, 59, 60, 01, 02, 03` possui dois blocos de três e não é PD_003;
- `01, 02, 03, 04, 20, 40` possui maior bloco de quatro e é somente PD_003.

Esta aprovação especifica o detector. Não aprova tolerância, sombra,
exclusão ou ativação no funil. Nenhum código ou banco foi alterado.
