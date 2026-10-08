# Pacote de Datasets

## Finalidade

Este diretorio representa a camada documental e operacional dos dados usados pelo artigo.

Ele deve permitir que a banca saiba:

- quais datasets entraram;
- qual a origem e a licenca;
- quais transformacoes foram feitas;
- quais campos existem;
- o que pode ou nao ser compartilhado.

## Estrutura canonica recomendada

```text
datasets/
  README.md
  raw/
  interim/
  processed/
  external/
  synthetic/
  metadata/
```

## Artefatos obrigatorios associados

- `catalogo_datasets.md`
- `codebook_dados.md`
- `registro_experimentos.md`
- `manifesto_reprodutibilidade.md`

## Regras

1. `raw/` nao deve ser tratado como area de edicao manual.
2. `processed/` deve ser derivavel a partir de regras documentadas.
3. `synthetic/` deve estar explicitamente identificado.
4. `metadata/` deve concentrar versao, origem, licenca e restricoes.
