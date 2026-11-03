# Evidência — subetapa 22.16.11.1

Data: 2026-11-02

## Alteração validada

- `intervalos_individuais` passou a incluir todo intervalo concluído cujo
  segmento intercepta o período consultado.
- Os concursos reais permanecem em `concurso_anterior` e
  `numero_do_concurso`.
- `concurso_inicial_visivel` e `concurso_final_visivel` informam apenas o
  recorte que será desenhado.
- Não é criado intervalo quando ainda não existe a ocorrência seguinte.
- A fotografia do concurso 500 foi conferida com ocorrências a cada cinco
  concursos: 100 ocorrências, 99 intervalos, média 5 e desvio-padrão 0.

## Testes

Com `MSen/src` e `MSen` no caminho de importação:

```text
python -m unittest tests.test_api_frequencias tests.test_frequencia_historica
29 testes executados — OK
```

Validador PostgreSQL:

```text
tests/validar_api_frequencias.py
API validada em PostgreSQL: estado, 60 dezenas por tipo e série filtrada.
```
