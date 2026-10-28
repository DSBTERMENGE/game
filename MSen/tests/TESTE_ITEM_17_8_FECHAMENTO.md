# Fechamento da Etapa 17 — perfis e distribuições

## Escopo entregue

- catálogo dos dez parâmetros;
- janela histórica com cortes exclusivos e proteção do futuro backtest;
- perfil estatístico genérico em `Decimal`;
- perfis das seis medidas geométricas, preservando centros ausentes;
- API somente leitura com histogramas e curva normal de referência;
- painel responsivo com os dez gráficos simultâneos;
- configuração local do estudo, com prévia obrigatória e screener inativo.

## Regressões finais

- 446 testes Python;
- 29 testes JavaScript;
- 16 fluxos completos no Google Chrome;
- consulta HTTP real: 3.069 resultados e 10 parâmetros;
- Chrome real contra o PostgreSQL e o servidor local atualizado.
- 1 fluxo integrado final aprovado no Chrome, incluindo a prévia dos dez pares
  de limites sobre os dados reais.

## Estado operacional

- uma única instância Flask está na porta 5050;
- servidor local atualizado no PID 31468;
- nenhuma migração ou gravação de dados foi necessária;
- nenhuma faixa ativa exclusão no screener;
- PythonAnywhere não foi acessado;
- commit e push dependem de autorização expressa.
