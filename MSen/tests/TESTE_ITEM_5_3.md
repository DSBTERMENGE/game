# Teste do Item 5.3

Data: 2026-10-26

## Resultado automatizado

- 7 testes específicos da rota de importação aprovados;
- 128 testes acumulados aprovados;
- arquivo válido e relatório JSON;
- extensão incorreta, arquivo vazio e XLSX corrompido rejeitados;
- upload acima do limite de 10 MiB rejeitado com HTTP 413;
- reimportação incremental sem duplicidade;
- falhas de persistência não expõem detalhes internos;
- arquivos temporários removidos tanto no sucesso quanto na falha.

## Homologação PostgreSQL local

A planilha real foi enviada pelo `POST /api/resultados/importar` ao banco local
`games`, que já possuía todo o histórico:

- HTTP 200;
- registros antes: 3.069;
- registros depois: 3.069;
- inseridos: 0;
- iguais: 3.069;
- alterados: 0;
- inválidos: 0.

Para provar a atomicidade, uma planilha temporária tentou inserir o concurso
3070 e uma falha controlada foi provocada na atualização das frequências. A
contagem permaneceu em 3.069 e o concurso 3070 não persistiu. O arquivo e o
script temporários foram removidos ao final.

O PythonAnywhere não foi acessado e nenhum commit foi criado.
