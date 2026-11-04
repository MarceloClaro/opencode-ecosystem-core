# Pesquisador científico — R1053: síntese quantitativa e submissão

O R1053 fecha duas camadas que faltavam no pesquisador:

1. **síntese quantitativa human-gated**: meta-análise fixa/aleatória,
   heterogeneidade, intervalo de predição, risco de viés e GRADE;
2. **pacote de submissão**: Markdown → LaTeX/DOCX, template ABNT genérico,
   checklist, declarações e manifesto.

Nenhuma das duas camadas decide verdade, aceite editorial ou publicação.

## R1053-A — síntese quantitativa

### Entrada

Um JSON com protocolo humano, estudos e, opcionalmente, GRADE:

```json
{
  "project_id": "RP-...",
  "protocol": {
    "reviewer": "nome",
    "declared_at": "2026-11-04T12:00:00Z",
    "effect_measure": "SMD",
    "model": "random",
    "confidence_level": 0.95,
    "min_studies": 3,
    "max_i2_for_pooling": 75,
    "human_confirmation": true
  },
  "studies": [
    {
      "study_id": "S1",
      "effect_size": 0.4,
      "standard_error": 0.1,
      "design": "RCT",
      "outcome": "desfecho",
      "risk_of_bias": {
        "overall": "low",
        "domains": {"randomization": "low", "missing": "low"}
      }
    }
  ],
  "grade": {
    "human_confirmation": true,
    "reviewer": "nome",
    "declared_at": "2026-11-04T12:00:00Z",
    "starting_level": "high",
    "domains": {
      "risk_of_bias": {"judgment": "serious", "reason": "..."},
      "inconsistency": {"judgment": "serious", "reason": "..."},
      "indirectness": {"judgment": "not_serious", "reason": "..."},
      "imprecision": {"judgment": "not_serious", "reason": "..."},
      "publication_bias": {"judgment": "not_serious", "reason": "..."}
    }
  }
}
```

### Comando

```bash
python -m marceloclaro.scientific_lab research refresh \
  --out projects/tema-r1053 \
  --quantitative-data dados-de-efeito.json
```

### Cálculos

- efeitos fixos por variância inversa;
- efeitos aleatórios DerSimonian-Laird;
- Q, df, I², tau², H²;
- IC do efeito combinado;
- intervalo de predição com t de Student;
- resumo de risco de viés;
- GRADE por rebaixamento declarado.

### Recusas

- protocolo sem `human_confirmation=true`;
- menos estudos que `min_studies`;
- efeito não finito ou erro-padrão ≤ 0;
- estudo sem risco de viés;
- `study_id` duplicado;
- GRADE sem humano ou sem razão para julgamento sério.

### Limites

- não extrai efeitos de PDFs;
- não imputa dados;
- não decide risco de viés;
- não atribui nota GRADE automaticamente;
- não declara eficácia, causalidade ou verdade.

## R1053-B — pacote de submissão

### Comando

```bash
python -m marceloclaro.scientific_lab research submission \
  --out projects/tema-r1053 \
  --journal "Revista de Teste" \
  --figures-dir figures \
  --tables-dir tables
```

### Saída

```text
10_submission/
  manuscript.md
  manuscript.tex
  manuscript.docx
  manuscript.pdf
  references.bib
  abnt-template.tex
  journal-checklist.json
  declarations.json
  declarations.md
  cover-letter.md
  figures/
  tables/
  submission-manifest.json
  README.md
```

### Ferramentas

| Ferramenta | Efeito |
|---|---|
| `pandoc` | gera `.tex` e `.docx` |
| `latexmk`/`pdflatex` | gera `.pdf` |
| ausente | status `unavailable`, sem falha silenciosa |

### O que permanece humano

- checklist do periódico;
- declarações éticas;
- conflitos de interesse;
- financiamento;
- contribuição autoral;
- ORCID;
- uso de IA;
- carta de submissão;
- decisão de submeter.

### Limites

- template ABNT genérico, não certificado;
- regras do periódico não são inferidas;
- nenhuma declaração é inventada;
- nada é submetido ou publicado.

## Evidência

- [README R1053](../reports/r1053/README.md)
- [Exemplo de entrada](../reports/r1053/example-input.json)
- [Exemplo de saída](../reports/r1053/example-result.json)
- [Spec R1053](../specs/SPEC-1053-sintese-quantitativa-e-submissao.md)
