# Relatório científico computacional

## Pergunta

Qual é a associação linear entre comprimento e largura da pétala no conjunto Iris da UCI?

## Dados e proveniência

Dataset: Iris UCI — bezdekIris.data. Origem informada: https://archive.ics.uci.edu/static/public/53/iris.zip.
SHA-256 do CSV analisado: 09d1766be79ec606b4c045059bc4b0d3e6a693b61d1cdfc6bdd45af42531df65.
A origem de arquivos fornecidos é uma declaração do responsável; o hash identifica
o conteúdo e não certifica sua autenticidade. Evidência externa independente: ausente.

Metadados de proveniência informados, incluindo transformação e limitações:

```json
{
  "archive_sha256": "d11fe30213d36434a0879aab7cb00ce3c812eb7ba2495874438abff7b7b762e9",
  "dataset_doi": "10.24432/C56C76",
  "evidence_kind": "real_observations",
  "license": "CC-BY-4.0",
  "limitations": "Conjunto histórico; espécies têm origens distintas. Correlação agregada não prova causalidade.",
  "member_sha256": "0fed2a99db77ec533a62dc66894d3ec6df3b58b6a8f3cf4a6b47e4086b7f97dc",
  "original_path": "/home/marceloclaro/opencode-ecosystem-core/docs/evidence/R663_R666_REAL_20261004_114400/sources/iris.csv",
  "sha256": "09d1766be79ec606b4c045059bc4b0d3e6a693b61d1cdfc6bdd45af42531df65",
  "snapshot_bytes": 4608,
  "source_authenticity": "user_declared",
  "source_url": "https://archive.ics.uci.edu/static/public/53/iris.zip",
  "title": "Iris UCI — bezdekIris.data",
  "transformation": "Cabeçalho CSV adicionado; registros preservados."
}
```

## Método prespecificado

Método: pearson. Observações: 150.
Colunas/grupos: {"x": "petal_length", "y": "petal_width"}.
Valores ausentes e não finitos são rejeitados. Um único método foi executado.
Hipótese nula: Correlação linear populacional igual a zero..

- Observações independentes; esta premissa não é confirmada pelo código.
- A origem e a adequação da amostra dependem da proveniência informada.
- Um único método é executado, sem busca por resultados significativos.
- O p-valor paramétrico e o intervalo de Fisher pressupõem distribuição bivariada adequada; o teste de permutação pressupõe permutabilidade sob a hipótese nula.

## Resultados executados

Estimativa: 0.96286543. p-valor bilateral: 4.6750039e-86. Intervalo de 95%: [0.9490524593111144, 0.9729853173787971].

```json
{
  "alpha": 0.05,
  "alternative": "two-sided",
  "assumptions": [
    "Observações independentes; esta premissa não é confirmada pelo código.",
    "A origem e a adequação da amostra dependem da proveniência informada.",
    "Um único método é executado, sem busca por resultados significativos.",
    "O p-valor paramétrico e o intervalo de Fisher pressupõem distribuição bivariada adequada; o teste de permutação pressupõe permutabilidade sob a hipótese nula."
  ],
  "causal_inference": false,
  "confidence_interval_95": [
    0.9490524593111144,
    0.9729853173787971
  ],
  "descriptive": {
    "petal_length": {
      "max": 6.9,
      "mean": 3.758,
      "median": 4.35,
      "min": 1.0,
      "n": 150,
      "standard_deviation": 1.7652982332594664
    },
    "petal_width": {
      "max": 2.5,
      "mean": 1.1993333333333334,
      "median": 1.3,
      "min": 0.1,
      "n": 150,
      "standard_deviation": 0.7622376689603466
    }
  },
  "estimate": 0.9628654314027961,
  "experiment_executed": true,
  "limitations": [
    "A análise não estabelece causalidade.",
    "A revisão computacional não substitui revisão humana por pares.",
    "Não há certificação externa de originalidade ou generalização."
  ],
  "method": "pearson",
  "missing_values_policy": "reject",
  "n": 150,
  "null_hypothesis": "Correlação linear populacional igual a zero.",
  "p_value": 4.675003907328585e-86,
  "permutation": {
    "extreme": 0,
    "p_value": 0.001,
    "replicates": 999,
    "seed": 663
  },
  "seed": 663,
  "statistic": 0.9628654314027961,
  "variables": {
    "x": "petal_length",
    "y": "petal_width"
  }
}
```

## Reprodução e revisão computacional

Reexecução em processo separado: True.
Concordância com o cálculo original: True.
A revisão computacional verificou integridade dos snapshots, consistência numérica
e reprodução; não ocorreu revisão humana por pares.

## Limitações

- A análise não estabelece causalidade.
- A revisão computacional não substitui revisão humana por pares.
- Não há certificação externa de originalidade ou generalização.
- As referências abaixo documentam metadados bibliográficos; não foram inferidos
  resultados dos artigos nem realizado julgamento humano de sua adequação.
- Este relatório não prova originalidade científica nem validade em outros domínios.

## Referências coletadas ou fornecidas como snapshots identificados

1. THE USE OF MULTIPLE MEASUREMENTS IN TAXONOMIC PROBLEMS. 1936. https://doi.org/10.1111/j.1469-1809.1936.tb02137.x
2. The Iris Data Set: In Search of the Source of<i>Virginica</i>. 2021. https://doi.org/10.1111/1740-9713.01589
