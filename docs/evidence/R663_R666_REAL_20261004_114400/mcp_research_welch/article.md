# Relatório científico computacional

## Pergunta

Qual é a diferença observada de largura da pétala entre versicolor e virginica no Iris UCI?

## Dados e proveniência

Dataset: Iris UCI — bezdekIris.data. Origem informada: https://archive.ics.uci.edu/static/public/53/iris.zip.
SHA-256 do CSV analisado: 8e6de96d86fbfe22f4fd00bea58e5f159fcb222bfb22e2a52721b68c7a5bbc62.
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
  "original_path": "/home/marceloclaro/opencode-ecosystem-core/docs/evidence/R663_R666_REAL_20261004_114400/sources/iris-two-species.csv",
  "parent_csv_sha256": "09d1766be79ec606b4c045059bc4b0d3e6a693b61d1cdfc6bdd45af42531df65",
  "sha256": "8e6de96d86fbfe22f4fd00bea58e5f159fcb222bfb22e2a52721b68c7a5bbc62",
  "snapshot_bytes": 3208,
  "source_authenticity": "user_declared",
  "source_url": "https://archive.ics.uci.edu/static/public/53/iris.zip",
  "title": "Iris UCI — bezdekIris.data",
  "transformation": "Subconjunto pré-especificado versicolor/virginica: 100 de 150 registros, valores preservados."
}
```

## Método prespecificado

Método: welch_t. Observações: 100.
Colunas/grupos: {"value": "petal_width", "group": "species", "groups": ["Iris-versicolor", "Iris-virginica"]}.
Valores ausentes e não finitos são rejeitados. Um único método foi executado.
Hipótese nula: Diferença entre as médias populacionais igual a zero..

- Observações independentes; esta premissa não é confirmada pelo código.
- A origem e a adequação da amostra dependem da proveniência informada.
- Um único método é executado, sem busca por resultados significativos.
- Os grupos são independentes; a inferência de Welch exige distribuição aproximadamente normal ou amostras adequadas e não implica equivalência de grupos não aleatorizados.

## Resultados executados

Estimativa: -0.7. p-valor bilateral: 2.1115344e-25. Intervalo de 95%: [-0.7951002289073511, -0.6048997710926484].

```json
{
  "alpha": 0.05,
  "alternative": "two-sided",
  "assumptions": [
    "Observações independentes; esta premissa não é confirmada pelo código.",
    "A origem e a adequação da amostra dependem da proveniência informada.",
    "Um único método é executado, sem busca por resultados significativos.",
    "Os grupos são independentes; a inferência de Welch exige distribuição aproximadamente normal ou amostras adequadas e não implica equivalência de grupos não aleatorizados."
  ],
  "causal_inference": false,
  "confidence_interval_95": [
    -0.7951002289073511,
    -0.6048997710926484
  ],
  "degrees_of_freedom": 89.04337511251656,
  "descriptive": {
    "Iris-versicolor": {
      "max": 1.8,
      "mean": 1.326,
      "median": 1.3,
      "min": 1.0,
      "n": 50,
      "standard_deviation": 0.19775268000454405
    },
    "Iris-virginica": {
      "max": 2.5,
      "mean": 2.026,
      "median": 2.0,
      "min": 1.4,
      "n": 50,
      "standard_deviation": 0.27465005563666733
    }
  },
  "estimate": -0.6999999999999997,
  "experiment_executed": true,
  "group_sizes": {
    "Iris-versicolor": 50,
    "Iris-virginica": 50
  },
  "limitations": [
    "A análise não estabelece causalidade.",
    "A revisão computacional não substitui revisão humana por pares.",
    "Não há certificação externa de originalidade ou generalização."
  ],
  "method": "welch_t",
  "missing_values_policy": "reject",
  "n": 100,
  "null_hypothesis": "Diferença entre as médias populacionais igual a zero.",
  "p_value": 2.111534400988574e-25,
  "seed": 663,
  "statistic": -14.625367047410148,
  "variables": {
    "group": "species",
    "groups": [
      "Iris-versicolor",
      "Iris-virginica"
    ],
    "value": "petal_width"
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
