# Evidência do Item 15.5 — validação isolada do detector PD_003

Data: 2026-10-27.

O detector existente `detectar_mais_de_tres_dezenas_sequenciais` foi executado
contra os 20 casos aprovados no Item 15.4:

- 8 casos que devem retornar `true`;
- 6 casos que devem retornar `false`;
- 6 entradas inválidas que devem produzir o tipo de erro esperado.

Resultado: 20 casos conformes e zero divergências. Os oito casos positivos
também foram verificados contra PD_001 e PD_002 e não foram classificados por
esses detectores, confirmando a exclusividade pelo maior bloco.

O detector de produção já correspondia integralmente ao contrato e não precisou
ser modificado.

## Saída para validação humana

O script `MSen/tests/validar_detector_pd003.py` apresenta para cada caso código,
combinação, esperado, obtido, motivo e indicador de conformidade. O requisito de
uma saída visual final foi incluído no Item 15.15.

## Testes

- 2 testes específicos aprovados.
- 299 testes Python da regressão aprovados.
- Nenhum filtro, configuração ou banco de dados foi alterado.
