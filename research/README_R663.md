# Percurso científico com proveniência — R663

`ScientificProvenancePipeline.run()` recebe uma pergunta, CSV UTF-8, origem
declarada, método prespecificado, colunas/grupos e diretório novo de saída.
Os métodos disponíveis são `descriptive`, `pearson` e `welch_t`.
Pearson inclui um teste de permutação de sensibilidade com 999 permutações
e semente 663; Welch compara exatamente dois grupos nomeados previamente.

O CSV é limitado a 5 MB e 50 mil observações. Valores ausentes ou não finitos
e grupos adicionais bloqueiam a execução. A API recebe configurações JSON e
não executa programas fornecidos pelo usuário.

```python
from research import ScientificProvenancePipeline

result = ScientificProvenancePipeline().run(
    question="Qual é a associação entre as duas medidas?",
    dataset_csv="/caminho/observacoes.csv",
    dataset_provenance={
        "title": "Título do dataset",
        "source_url": "https://repositorio.example/dataset",
        "evidence_kind": "real_observations",
        "sha256": "HASH_SHA256_DO_CSV",
        "license": "Licença informada na fonte",
        "transformation": "Conversão aplicada ao arquivo de origem",
        "limitations": ["Limitações da amostra e da interpretação"],
    },
    method="pearson",
    variables={"x": "coluna_x", "y": "coluna_y"},
    output_dir="/caminho/estudo-novo",
)
```

Sem `reference_sources`, a API tenta coletar metadados reais em Crossref e
OpenAlex. A indisponibilidade de todas as fontes bloqueia o percurso.
Opcionalmente, `reference_sources` recebe até cinco snapshots bibliográficos:
objetos com `path`, `source_url` HTTPS e `sha256` opcional. Cada JSON contém
`status="online"`, `evidence_kind="retrieved_http_metadata"` e `records`
com título e URL HTTPS. A origem de snapshots fornecidos continua declarada,
sem certificação independente.

A pasta contém dataset, referências/snapshots, configuração, resultados,
código interno dos métodos, `reproduce.py`, revisão computacional, corpus RAG
de metadados, consulta lexical, artigo Markdown e manifesto. A reprodução
executa outro processo Python e compara resultados e hashes. A revisão
computacional e os metadados bibliográficos não substituem avaliação humana
do desenho de estudo, leitura integral dos artigos ou revisão por pares.

O campo `status="completed"` significa que este cálculo delimitado e sua
reprodução passaram. Não certifica causalidade, autenticidade da origem,
originalidade, generalização ou qualidade de uma publicação.

No ResearchHub, dados indisponíveis/demonstrativos ficam em `diagnostic_results`.
DatasetDataSource retorna vazio por padrão se a coleta falhar; exemplos só
aparecem com `allow_demo_fallback=True`, rotulados e inelegíveis como evidência.
