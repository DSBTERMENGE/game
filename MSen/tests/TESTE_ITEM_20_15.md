# Evidência — subetapa 20.15

Data: 2026-10-30.

## Entrega

- Endpoint `GET /api/validacao/exportacao?formato=json|csv`.
- JSON técnico com versão de esquema, horário, registros e identificador
  SHA-256 determinístico do conjunto de referências.
- CSV UTF-8 com BOM, uma linha por avaliação e identificador repetido para
  conferência humana.
- Assinaturas de função, regra e execução; precisão decimal; origem, revisor e
  data da referência; esperado, calculado, diferença e aprovação.
- Downloads acessíveis na página de Validação e auditoria.

## Segurança e reprodução

- O JSON foi serializado, reaberto e comparado sem perda.
- Modificação posterior de qualquer registro invalida o SHA-256.
- O horário de geração não altera a identidade do conjunto.
- Células CSV iniciadas por `=`, `+`, `-`, `@`, tabulação ou retorno recebem
  apóstrofo e não são executadas como fórmula.

## Banco `games`

- Registros: 3.800.
- SHA-256: `aa4b253bedb2107535ce5ffc0ffaf43621605d63d808b87d5c53c8609bb6c8b4`.
- JSON: 5.261.895 bytes na conferência.
- CSV: 2.295.787 bytes na conferência.
- JSON reaberto e validado: sim.

## Testes

- 563 testes Python: aprovados.
- 37 testes Node: aprovados.
- 2 fluxos Chromium: aprovados.
- Nada foi publicado externamente.

Próxima subetapa: 20.16, somente após autorização específica.
